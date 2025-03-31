import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from config import EMBED_MODEL

tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
model = AutoModel.from_pretrained(EMBED_MODEL)

MAX_TOKENS = 510  

def generate_embedding(text):
    """Generates embedding for the input text."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_TOKENS)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].numpy()

def cosine_similarity(a, b):
    """Computes cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

def search_similar_errors(error_message, embeddings_file="py_embeddings.npy", metadata_file="py_metadata.npy", top_k=10):
    """Finds top K similar errors from embeddings."""
    embeddings = np.load(embeddings_file)
    metadata = np.load(metadata_file, allow_pickle=True)
    error_embedding = generate_embedding(error_message)
    similarities = [cosine_similarity(error_embedding, emb) for emb in embeddings]
    top_k_indices = np.argsort(similarities)[-top_k:][::-1]

    print(f"\n🔍 Top {top_k} Matches for Error: '{error_message}'\n")
    for idx in top_k_indices:
        score = similarities[idx]
        meta = metadata[idx]
        print(f"\nScore: {score:.4f} | URL: {meta['url']}")
        print(f"\nFull Documentation:\n{meta.get('full_content', 'No content available.')}\n")

if __name__ == "__main__":
    error_msg = "KeyError: 'column_name' not found in DataFrame"
    search_similar_errors(error_msg)
