import numpy as np
import faiss
import json
import os
from pydantic import BaseModel
import torch
from fastapi import FastAPI, HTTPException, Form
from google import genai
from google.genai import types
from transformers import AutoTokenizer, AutoModel
from dotenv import load_dotenv

load_dotenv()

os.environ['TF_ENABLE_ONEDNN_OPTS']="0"

app = FastAPI()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash-lite"

# ✅ FAISS & Embedding Setup
LIB_PATH = {
    "Python": "py",
    "Numpy": "np",
    "Pandas": "pd",
    "PyTorch": "pt",
    "Scikit-Learn": "sklearn",
    "TensorFlow Keras": "tfkeras"
}

def load_faiss_index(library):
    """Loads FAISS index and metadata for the specified library."""
    base_path = os.path.join("../DocRetrieval/data", LIB_PATH[library])

    index = faiss.read_index(os.path.join(base_path, "faiss_index.bin"))
    metadata = np.load(os.path.join(base_path, "faiss_metadata.npy"), allow_pickle=True)
    
    return index, metadata

# ✅ Load GraphCodeBERT for Generating Query Embeddings
tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
graph_model = AutoModel.from_pretrained("microsoft/graphcodebert-base")

def generate_embedding(text):
    """Generates embeddings for input text using GraphCodeBERT."""
    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = graph_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling
    return embeddings[0].numpy().astype('float32')

def search_faiss(query_embedding, index, metadata, k=3):
    """Finds the most relevant documents using FAISS similarity search."""
    _, indices = index.search(query_embedding.reshape(1, -1), k)

    top_docs = []
    for idx in indices[0]:
        doc_meta = metadata[idx]  # Retrieve metadata (contains text + URL)
        top_docs.append({
            "text": doc_meta.get("text", ""),  # ✅ Full text chunk
            "url": doc_meta.get("url", "")  # ✅ Source URL
        })
    
    return top_docs

# ✅ In-Memory Session Storage (Replace with Redis for Production)
session_store = {}

class AnalyzeErrorRequest(BaseModel):
    session_id: str
    user_prompt: str
    code_snippet: str
    stack_trace: dict

# 🚀 **1st API Call: Analyze Error**
@app.post("/analyze_error")
async def analyze_error(
    request: AnalyzeErrorRequest
):
    """Processes an error, determines if documentation is required, and saves session data."""
    session_id = request.session_id
    user_prompt = request.user_prompt
    code_snippet = request.code_snippet
    stack_trace = request.stack_trace
    # ✅ Send initial query to Gemini
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(
                text=json.dumps({
                    "user_prompt": user_prompt,
                    "code_snippet": code_snippet,
                    "stack_trace": stack_trace
                })
            )]
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
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
                    enum=["Python", "Numpy", "Pandas", "PyTorch", "Scikit-Learn", "TensorFlow Keras"],
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
            ),
        ],
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    ):
        response_text += chunk.text

    try:
        gemini_response = json.loads(response_text)  
        doc_req = gemini_response.get("DocReq", False)
        search_phrase = gemini_response.get("SearchPhrase", "")
        library = gemini_response.get("Library", "")

        # ✅ Store structured data into session_store
        session_store[session_id] = {
            "user_prompt": user_prompt,
            "code_snippet": code_snippet,
            "stack_trace": stack_trace,
            "doc_req": doc_req,
            "search_phrase": search_phrase,
            "library": library,
            "gemini_response": gemini_response  
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing Gemini response.")

    return {"session_id": session_id, "response": response_text}

class SubmitDocumentsRequest(BaseModel):
    session_id: str

@app.post("/submit_documents")
async def submit_documents(request: SubmitDocumentsRequest):
    """Enhances previous analysis using FAISS document retrieval if needed."""
    session_id = request.session_id
    if session_id not in session_store:
        raise HTTPException(status_code=400, detail="Session ID not found. Make the first call first.")

    previous_context = session_store[session_id]
    user_prompt = previous_context["user_prompt"]
    code_snippet = previous_context["code_snippet"]
    stack_trace = previous_context["stack_trace"]
    doc_req = previous_context["doc_req"]
    search_phrase = previous_context["search_phrase"]
    library = previous_context["library"]

    retrieved_docs = []
    used_urls = []

    if doc_req:
        print("🔍 Performing FAISS search for:", search_phrase)
        index, metadata = load_faiss_index(library)
        query_embedding = generate_embedding(search_phrase)
        retrieved_docs = search_faiss(query_embedding, index, metadata, k=3)

    full_conversation = {
        "user_prompt": user_prompt,
        "code_snippet": code_snippet,
        "stack_trace": stack_trace,
        "retrieved_documents": retrieved_docs if doc_req else []
    }

    if doc_req:
        system_instruction = (
            "You have access to additional documentation. "
            "Use the attached information only if it is directly relevant to the user's request. "
            "If a document is useful, include the URLs of the sources you used at the end of your response."
        )
    else:
        system_instruction = "Answer the user's request to the best of your ability without requiring external documentation."

    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=json.dumps(full_conversation))])
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[types.Part.from_text(text=system_instruction)],
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    ):
        response_text += chunk.text

    if doc_req:
        used_urls = [doc["url"] for doc in retrieved_docs]
        response_text += f"\n\n📌 **Sources Used:** {', '.join(used_urls)}"

    session_store[session_id]["gemini_response"] = response_text

    return {"session_id": session_id, "updated_response": response_text}
