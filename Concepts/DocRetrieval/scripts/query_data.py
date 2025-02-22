"""
Connects to chromadb and queries using text
Returns top 3 matches
"""

import chromadb
from chromadb.config import Settings

# Connect to the Persistent ChromaDB Directory
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="../chroma_db"))

# Load Existing Collection
collection = client.get_collection(name="debug_docs")

# Perform a Sample Query
query_text = "AttributeError"  # Replace with actual query text

results = collection.query(
    query_texts=[query_text],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)

# Display Results
print(f"🔍 Query Results for '{query_text}':")
for idx, doc in enumerate(results['documents'][0]):
    print(f"\nResult {idx+1}:")
    print(f"Document: {doc}")
    print(f"Metadata: {results['metadatas'][0][idx]}")
    print(f"Distance: {results['distances'][0][idx]}")
