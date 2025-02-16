import faiss
import json
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# Load Stack Overflow dataset
with open("stackoverflow.json", "r") as f:
    stackoverflow_data = json.load(f)

# Load Stack Overflow embeddings
stackoverflow_embeddings = np.load("stackoverflow_embeddings.npy")

# ✅ Load GraphCodeBERT tokenizer & model
tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = AutoModel.from_pretrained("microsoft/graphcodebert-base")

# ✅ Normalize embeddings for cosine similarity
faiss.normalize_L2(stackoverflow_embeddings)

# ✅ Create FAISS index using Inner Product (IP) for Cosine Similarity
dimension = stackoverflow_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(stackoverflow_embeddings)

# ✅ Save FAISS index
faiss.write_index(index, "stackoverflow_faiss_index.bin")
print(f"✅ FAISS index created with Cosine Similarity! (Dimension: {dimension})")

# Load FAISS index
index = faiss.read_index("stackoverflow_faiss_index.bin")

# Load errors dataset (New format)
with open("errors.json", "r") as f:
    errors_data = json.load(f)

def encode_with_graphcodebert(text):
    """Encodes text using GraphCodeBERT"""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def embed_and_normalize_error(error):
    """Embeds error using GraphCodeBERT and ensures correct FAISS dimension."""
    exception = error.get("exception", "UnknownException")
    message = error.get("message", "")
    code_snippet = error.get("code_snippet", "No code provided")
    description = error.get("description", "")

    # Concatenate relevant information
    error_text = f"{exception} | {message} | Code: {code_snippet} | {description}"

    # Generate embedding using GraphCodeBERT
    embedding = encode_with_graphcodebert(error_text)

    # ✅ Ensure embedding matches FAISS index dimension
    embedding = np.array(embedding).reshape(1, -1)  # Convert to 2D array

    # ✅ Normalize embedding for cosine similarity
    faiss.normalize_L2(embedding)

    return embedding

def retrieve_and_rerank_solutions(query_embedding, k=5):
    """Retrieves and re-ranks solutions based on Stack Overflow upvotes"""
    print(f"FAISS Index Dimension: {index.d}")
    print(f"Query Embedding Dimension: {query_embedding.shape}")

    distances, indices = index.search(query_embedding, k)

    retrieved_solutions = []
    for i, idx in enumerate(indices[0]):
        entry = stackoverflow_data[idx]
        upvotes = entry.get("upvotes", 0)  # Default to 0 if upvotes field is missing
        retrieved_solutions.append((entry, distances[0][i], upvotes))

    # ✅ Re-rank by upvotes (higher is better)
    retrieved_solutions.sort(key=lambda x: -x[2])

    return retrieved_solutions

# ✅ Run retrieval on sample errors
for error in errors_data[20:26]:  # Limiting to 5 errors for testing
    query_embedding = embed_and_normalize_error(error)
    similar_solutions = retrieve_and_rerank_solutions(query_embedding, k=3)

    print(f"\n🔍 **Error:** {error['message']}")
    print(f"📜 **Code Snippet:** {error['code_snippet']}")
    print(f"📝 **Description:** {error['description']}")

    for idx, (solution, dist, upvotes) in enumerate(similar_solutions):
        print(f"\n🔹 **Suggested Fix {idx+1} (Distance: {dist:.4f}, Upvotes: {upvotes}):**")
        print(f"📌 **Title:** {solution['title']}")
        print(f"📖 **Solution Snippet:** {solution['body'][:300]}...\n")  # Print first 300 characters
    print("-" * 50)
