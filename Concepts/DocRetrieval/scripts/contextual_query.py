"""
Sim Search on embeddings
Top chunk match with neighbouring chunks for context
"""
import numpy as np
import faiss

def contextual_query(query_embedding, index, metadata, k=1):
    # Perform similarity search
    distances, indices = index.search(np.array([query_embedding]), k)

    # Collect matched chunks and their neighbors
    contextual_results = []

    for idx in indices[0]:
        doc_meta = metadata[idx]
        chunk_index = doc_meta.get('chunk_index', 0)
        doc_id = doc_meta.get('doc_id', 'unknown')

        # Retrieve previous, current, and next chunks
        context_chunks = []
        for neighbor_idx in [chunk_index - 1, chunk_index, chunk_index + 1]:
            # Find the metadata with matching doc_id and chunk_index
            neighbor_meta = next((m for m in metadata if m.get('doc_id') == doc_id and m.get('chunk_index') == neighbor_idx), None)
            if neighbor_meta:
                context_chunks.append(neighbor_meta.get('text', ''))

        contextual_results.append({
            "doc_id": doc_id,
            "matched_chunk_index": chunk_index,
            "context": context_chunks
        })

    return contextual_results

# Example Usage
if __name__ == "__main__":
    # Load FAISS index and metadata
    faiss_index_path = '../data/faiss_index.bin'
    index = faiss.read_index(faiss_index_path)
    metadata = np.load('../data/faiss_metadata.npy', allow_pickle=True)

    # Load query embedding
    query_embedding = np.load('../data/pd_embeddings.npy')[0].astype('float32')

    # Run contextual query
    results = contextual_query(query_embedding, index, metadata, k=1)

    # Display results
    for res in results:
        print(f"\n📄 Document ID: {res['doc_id']}")
        print("Contextual Chunks:")
        for idx, chunk in enumerate(res['context']):
            print(f"Chunk {idx+1}: {chunk}")
