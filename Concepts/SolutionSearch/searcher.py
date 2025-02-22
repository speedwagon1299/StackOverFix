import faiss
import json
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from rank_bm25 import BM25Okapi  # ✅ New: BM25 for keyword retrieval

# Load Stack Overflow dataset
with open("stackoverflow.json", "r") as f:
    stackoverflow_data = json.load(f)

# Initialize BM25
stackoverflow_texts = [
    f"{entry['title']} {entry['explicit_error_message']} {entry['body']}"
    for entry in stackoverflow_data
]
bm25 = BM25Okapi([text.split() for text in stackoverflow_texts])

# Load FAISS index
index = faiss.read_index("stackoverflow_faiss_index.bin")

# Load GraphCodeBERT tokenizer & model
tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = AutoModel.from_pretrained("microsoft/graphcodebert-base")

def encode_with_graphcodebert(text):
    """Encodes text using GraphCodeBERT"""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def retrieve_hybrid_solutions(query_text, k=5):
    """Hybrid retrieval: FAISS (semantic) + BM25 (keyword matching)."""
    query_embedding = encode_with_graphcodebert(query_text)
    query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    # FAISS Search
    distances, indices = index.search(query_embedding, k)
    faiss_results = [stackoverflow_data[i] for i in indices[0]]

    # BM25 Search
    bm25_results = bm25.get_top_n(query_text.split(), stackoverflow_data, n=k)

    # Combine results & remove duplicates
    combined_results = list({entry['title']: entry for entry in (faiss_results + bm25_results)}.values())

    return combined_results
