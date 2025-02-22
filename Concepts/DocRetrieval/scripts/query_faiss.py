"""
Returns top 3 matches from faiss
"""

import numpy as np
import faiss

# Load FAISS index
faiss_index_path = '../data/faiss_index.bin'
index = faiss.read_index(faiss_index_path)

# Load metadata
metadata = np.load('../data/faiss_metadata.npy', allow_pickle=True)

# Example: Use one of the existing embeddings as a query
query_embedding = np.load('../data/pd_embeddings.npy')[0].astype('float32')

# Perform similarity search
k = 3  # Number of nearest neighbors
distances, indices = index.search(np.array([query_embedding]), k)

# Display results
print("🔍 Top Matches:")
for i, idx in enumerate(indices[0]):
    print(f"\nResult {i+1}:")
    print(f"Distance: {distances[0][i]}")
    print(f"Metadata: {metadata[idx]}")
