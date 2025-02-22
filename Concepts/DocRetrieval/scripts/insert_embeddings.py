"""
Loads .npy files and inserts into chromadb
"""

import numpy as np
import chromadb
from chromadb.config import Settings
import os

# Initialize ChromaDB with Persistent Directory
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="../chroma_db"))

# Create or Get the Collection
collection = client.get_or_create_collection(name="debug_docs")

# Load Embeddings and Metadata from the Data Directory
embeddings_path = os.path.join("../data", "pd_embeddings.npy")
metadata_path = os.path.join("../data", "pd_metadata.npy")

embeddings = np.load(embeddings_path)
metadata = np.load(metadata_path, allow_pickle=True).item()

# Prepare Data for Insertion
ids, documents, metadatas = [], [], []
for idx, embed in enumerate(embeddings):
    doc_meta = metadata.get(str(idx), {})
    ids.append(str(idx))
    documents.append(doc_meta.get("text", ""))
    metadatas.append(doc_meta)

# Insert into ChromaDB
collection.add(
    embeddings=embeddings.tolist(),
    metadatas=metadatas,
    documents=documents,
    ids=ids
)

# Persist Changes
client.persist()

print("✅ Data successfully stored in ChromaDB at '../chroma_db'")
