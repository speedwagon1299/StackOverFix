import faiss
import numpy as np

# Load embeddings
stackoverflow_embeddings = np.load("stackoverflow_embeddings.npy")

# Normalize embeddings (needed for Cosine Similarity)
faiss.normalize_L2(stackoverflow_embeddings)

# Create FAISS index using Inner Product (IP) for Cosine Similarity
dimension = stackoverflow_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(stackoverflow_embeddings)

# Save FAISS index
faiss.write_index(index, "stackoverflow_faiss_index.bin")

print("✅ FAISS index created with Cosine Similarity!")
