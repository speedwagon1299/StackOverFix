# """
# Generates FAISS bin index for given embeddings.npy file.
# Generates faiss_metadata.npy file
# """

# import numpy as np

# import faiss
# import os

# embed_path = "pd_embeddings.npy"
# meta_path = "pd_metadata.npy"
# embeddings = np.load(os.path.join("../data", embed_path))
# metadata = np.load(os.path.join("../data", meta_path), allow_pickle=True)  # List of dicts

# embeddings = embeddings.astype('float32')

# assert len(embeddings) == len(metadata), "Embeddings and metadata count mismatch."

# # Initialize FAISS index (L2 similarity)
# dimension = embeddings.shape[1]
# index = faiss.IndexFlatL2(dimension)

# # Add embeddings to the FAISS index
# index.add(embeddings)
# print(f"✅ FAISS index built with {index.ntotal} vectors.")

# # Save the FAISS index
# faiss_index_path = 'pd_faiss_index.bin'
# faiss_index_path = os.path.join("../data", faiss_index_path)
# faiss.write_index(index, faiss_index_path)
# print(f"💾 FAISS index saved to {faiss_index_path}")

# # Save metadata as a NumPy array
# faiss_meta_path = "pd_faiss_metadata.npy"
# faiss_meta_path = os.path.join('../data', faiss_meta_path)
# np.save(faiss_meta_path, metadata)
# print(f"💾 Metadata saved to {faiss_meta_path}")
