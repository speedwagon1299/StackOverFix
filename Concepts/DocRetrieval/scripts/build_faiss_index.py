import numpy as np
import faiss
import os

# Load embeddings and metadata
embeddings = np.load('../data/pd_embeddings.npy')
metadata = np.load('../data/pd_metadata.npy', allow_pickle=True)  # List of dicts

# Ensure embeddings are float32 for FAISS
embeddings = embeddings.astype('float32')

# Validate data alignment
assert len(embeddings) == len(metadata), "Embeddings and metadata count mismatch."

# Initialize FAISS index (L2 similarity)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the FAISS index
index.add(embeddings)
print(f"✅ FAISS index built with {index.ntotal} vectors.")

# Save the FAISS index
faiss_index_path = '../data/faiss_index.bin'
faiss.write_index(index, faiss_index_path)
print(f"💾 FAISS index saved to {faiss_index_path}")

# Save metadata as a NumPy array
np.save('../data/faiss_metadata.npy', metadata)
print("💾 Metadata saved to '../data/faiss_metadata.npy'")
