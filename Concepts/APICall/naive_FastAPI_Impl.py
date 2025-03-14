from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from google import genai
from pydantic import BaseModel
from google.genai import types
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash-lite"

# Temporary in-memory session storage (Replace with Redis for production)
session_store = {}

class AnalyzeErrorRequest(BaseModel):
    session_id: str
    user_prompt: str
    code_snippet: str
    stack_trace: dict

# 🚀 1st API Call: Analyze Error
@app.post("/analyze_error")
async def analyze_error(
    request: AnalyzeErrorRequest
):
    # Store session input for later use in session_store
    session_id = request.session_id
    user_prompt = request.user_prompt
    code_snippet = request.code_snippet
    stack_trace = request.stack_trace
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=json.dumps({
                        "user_prompt": user_prompt,
                        "code_snippet": code_snippet,
                        "stack_trace": stack_trace
                    })
                )
            ],
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
                and generate a compact (≤8 words) phrase for FAISS-based similarity search in the parameter \"SearchPhrase\" which would work with the embedding microsoft/graphcodebert-base."""
            ),
        ],
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    ):
        response_text += chunk.text

    # Store API response in session
    if session_id not in session_store:
        session_store[session_id] = {}  # Now session_id is initialized
    session_store[session_id]["gemini_response"] = response_text

    return {"session_id": session_id, "response": response_text}


# 🚀 2nd API Call: Submit Documents (Uses First Call's Context)
@app.post("/submit_documents")
async def submit_documents(session_id: str = Form(...), file: UploadFile = File(...)):
    # Retrieve stored session context
    if session_id not in session_store:
        raise HTTPException(status_code=400, detail="Session ID not found. Make the first call first.")

    previous_context = session_store[session_id]

    # Convert uploaded file to text (if applicable)
    document_text = file.file.read().decode("utf-8")

    # Append document info to previous context
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"Here is the additional document: {file.filename}. Contents: {document_text}")]
        )
    ]

    # Use previous conversation in API request
    contents.insert(0, types.Content(role="user", parts=[types.Part.from_text(text=previous_context["gemini_response"])]))

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text="""You now have additional documents. Use them to refine your solution only if they are of use.
                Return the best fix or explanation. If the documents are used, provide metadata information about them,
                else purely return the solution."""
            ),
        ],
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    ):
        response_text += chunk.text

    return {"session_id": session_id, "updated_response": response_text}
