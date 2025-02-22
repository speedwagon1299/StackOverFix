import numpy as np
import faiss
import os

# Load embeddings and metadata
embeddings = np.load('../data/pd_embeddings.npy')
metadata = np.load('../data/pd_metadata.npy', allow_pickle=True).item()

# FAISS expects float32 data
embeddings = embeddings.astype('float32')

# Initialize FAISS index (using L2 similarity)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the index
index.add(embeddings)
print(f"✅ FAISS index built with {index.ntotal} vectors.")

# Save the FAISS index
faiss_index_path = '../data/faiss_index.bin'
faiss.write_index(index, faiss_index_path)
print(f"💾 FAISS index saved to {faiss_index_path}")

# Save metadata mapped to embeddings
# Metadata list where each entry corresponds to an embedding
metadata_list = [metadata.get(str(i), {}) for i in range(len(embeddings))]
np.save('../data/faiss_metadata.npy', metadata_list)
print("💾 Metadata saved to '../data/faiss_metadata.npy'")
