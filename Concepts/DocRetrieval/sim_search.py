import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

# Load GraphCodeBERT for embeddings
tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = AutoModel.from_pretrained("microsoft/graphcodebert-base")

MAX_TOKENS = 510  # Reduced to account for special tokens [CLS] and [SEP]

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

def search_similar_errors(error_message, embeddings_file="pd_embeddings.npy", metadata_file="pd_metadata.npy", top_k=10):
    """Finds top K similar errors from embeddings."""
    # Load precomputed embeddings and metadata
    embeddings = np.load(embeddings_file)
    metadata = np.load(metadata_file, allow_pickle=True)

    # Generate embedding for the error message
    error_embedding = generate_embedding(error_message)

    # Calculate cosine similarities
    similarities = [cosine_similarity(error_embedding, emb) for emb in embeddings]

    # Get top K matches
    top_k_indices = np.argsort(similarities)[-top_k:][::-1]

    print(f"\n🔍 Top {top_k} Matches for Error: '{error_message}'\n")
    for idx in top_k_indices:
        score = similarities[idx]
        meta = metadata[idx]
        print(f"\nScore: {score:.4f} | URL: {meta['url']}")
        print(f"\nFull Documentation:\n{meta.get('full_content', 'No content available.')}\n")

if __name__ == "__main__":
    # Example error message
    error_msg = "KeyError: 'column_name' not found in DataFrame"
    search_similar_errors(error_msg)
