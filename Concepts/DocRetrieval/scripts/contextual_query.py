"""
Sim Search on embeddings
Top chunk match with neighbouring chunks for context
"""

import chromadb
from chromadb.config import Settings
import numpy as np

def contextual_query(collection, query_embedding, n_results=1):
    # Search for the top matching chunk
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    # Collect matched chunks and their neighbors
    contextual_results = []

    for doc_meta in results['metadatas'][0]:
        chunk_index = doc_meta.get('chunk_index', 0)
        doc_id = doc_meta.get('doc_id', 'unknown')

        # Retrieve previous, current, and next chunks
        context_chunks = []
        for neighbor_idx in [chunk_index - 1, chunk_index, chunk_index + 1]:
            neighbor_results = collection.get(
                where={"doc_id": doc_id, "chunk_index": neighbor_idx},
                include=["documents", "metadatas"]
            )
            if neighbor_results['documents']:
                context_chunks.append(neighbor_results['documents'][0])

        contextual_results.append({
            "doc_id": doc_id,
            "matched_chunk_index": chunk_index,
            "context": context_chunks
        })

    return contextual_results

# Example Usage
if __name__ == "__main__":
    # Connect to ChromaDB
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="../chroma_db"))
    collection = client.get_collection(name="debug_docs")

    # Load a sample query embedding (replace with actual embedding)
    query_embedding = np.load('../data/pd_embeddings.npy')[0]  # Example: first embedding

    # Run Contextual Query
    contextual_results = contextual_query(collection, query_embedding, n_results=1)

    # Display Results
    for res in contextual_results:
        print(f"\n📄 Document ID: {res['doc_id']}")
        print("Contextual Chunks:")
        for idx, chunk in enumerate(res['context']):
            print(f"Chunk {idx+1}: {chunk}")
