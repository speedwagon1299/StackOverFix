import os
import json
import faiss
import numpy as np
import torch
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModel
from pydantic import BaseModel
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Globals (initialized on startup)
tokenizer = None
embed_model = None
client = None

EMBED_MODEL = "nomic-ai/nomic-embed-text-v1"
RERANK_MODEL = "nvidia/nv-rerankqa-mistral-4b-v3"
LIB_PATH = {
    "Python": "py",
    "Numpy": "np",
    "Pandas": "pd",
    "PyTorch": "pt",
    "Scikit-Learn": "sklearn",
    "TensorFlow Keras": "tfkeras"
}

session_store = {}

# ✅ Startup: load models only when app starts
@app.on_event("startup")
async def load_models():
    global tokenizer, embed_model, client
    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL, trust_remote_code=True)
    embed_model = AutoModel.from_pretrained(EMBED_MODEL, trust_remote_code=True)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    print("✅ Models and Gemini client loaded.")


def load_faiss_index(library):
    base_path = os.path.join("../DocRetrieval/data_2", LIB_PATH[library])
    index = faiss.read_index(os.path.join(base_path, "faiss_index.bin"))
    metadata = np.load(os.path.join(base_path, "faiss_metadata.npy"), allow_pickle=True)
    return index, metadata


def generate_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = embed_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].numpy().astype('float32')


class AnalyzeErrorRequest(BaseModel):
    session_id: str
    user_prompt: str
    code_snippet: str
    stack_trace: dict


@app.post("/analyze_error")
async def analyze_error(request: AnalyzeErrorRequest):
    session_id = request.session_id
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=json.dumps({
                "user_prompt": request.user_prompt,
                "code_snippet": request.code_snippet,
                "stack_trace": request.stack_trace
            }))]
        ),
    ]

    config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["DocReq", "SearchPhrase", "Library"],
            properties={
                "DocReq": genai.types.Schema(type=genai.types.Type.BOOLEAN),
                "SearchPhrase": genai.types.Schema(type=genai.types.Type.STRING),
                "Library": genai.types.Schema(
                    type=genai.types.Type.STRING,
                    enum=list(LIB_PATH.keys()),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(
                text="""You will be given a stack trace of an error and its associated code snippet in Python.
                If the error is simple and solvable by your current knowledge without available documentation in enum,
                return \"DocRequired\" with False and the other parameters with NULL.
                Else, return the required library documentation as an enum in \"Library\"
                and generate a compact (≤8 words) phrase for FAISS-based similarity search in the parameter \"SearchPhrase\"."""
            )
        ],
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(model="gemini-2.0-flash-lite", contents=contents, config=config):
        response_text += chunk.text

    try:
        gemini_response = json.loads(response_text)
        session_store[session_id] = {
            "user_prompt": request.user_prompt,
            "code_snippet": request.code_snippet,
            "stack_trace": request.stack_trace,
            "doc_req": gemini_response.get("DocReq", False),
            "search_phrase": gemini_response.get("SearchPhrase", ""),
            "library": gemini_response.get("Library", ""),
            "gemini_response": gemini_response
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing Gemini response.")

    return {"session_id": session_id, "response": response_text}


class SubmitDocumentsRequest(BaseModel):
    session_id: str


@app.post("/submit_documents")
async def submit_documents(request: SubmitDocumentsRequest):
    if request.session_id not in session_store:
        raise HTTPException(status_code=400, detail="Session ID not found.")

    ctx = session_store[request.session_id]
    top_k_docs, used_urls = [], []

    if ctx["doc_req"]:
        index, metadata = load_faiss_index(ctx["library"])
        query_embedding = generate_embedding(ctx["search_phrase"])
        D, I = index.search(query_embedding.reshape(1, -1), 25)
        candidates = [{"score": float(D[0][i]), **metadata[I[0][i]]} for i in range(len(I[0]))]

        payload = {
            "model": RERANK_MODEL,
            "query": {"text": ctx["search_phrase"]},
            "passages": [{"text": doc["text"]} for doc in candidates]
        }

        try:
            response = requests.post(
                f"https://ai.api.nvidia.com/v1/retrieval/{RERANK_MODEL}/reranking",
                headers={
                    "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}",
                    "Accept": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            rankings = response.json().get("rankings", [])
            reranked_docs = [candidates[r["index"]] | {"rerank_score": r["logit"]}
                             for r in rankings if r["logit"] >= 0]

            if reranked_docs:
                top_k_docs = sorted(reranked_docs, key=lambda x: x["rerank_score"], reverse=True)[:2]
                used_urls = [doc["url"] for doc in top_k_docs]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"NVIDIA Rerank API failed: {str(e)}")

    full_convo = {
        "user_prompt": ctx["user_prompt"],
        "code_snippet": ctx["code_snippet"],
        "stack_trace": ctx["stack_trace"],
        "retrieved_documents": top_k_docs
    }

    system_instruction = (
        "You have access to additional documentation. Use it only if directly relevant. "
        "Include URLs if used. Ensure clean format and spacing."
        if ctx["doc_req"] and top_k_docs else
        "Please proceed to solve the user's issue without relying on external documentation. "
        "Ensure clean format and spacing."
    )

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=json.dumps(full_convo))])]
    config = types.GenerateContentConfig(
        temperature=1, top_p=0.95, top_k=40, max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[types.Part.from_text(text=system_instruction)]
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(model="gemini-2.0-flash-lite", contents=contents, config=config):
        response_text += chunk.text

    if ctx["doc_req"]:
        response_text += f"\n\n📌 **Sources Used:** {', '.join(used_urls)}"

    session_store[request.session_id]["gemini_response"] = response_text
    return {
        "session_id": request.session_id,
        "user_prompt": ctx["user_prompt"],
        "code_snippet": ctx["code_snippet"],
        "stack_trace": ctx["stack_trace"],
        "retrieved_documents": used_urls,
        "updated_response": response_text
    }
