"""
Using OPEN_AI_API Key for ada embeddings, not used in project since 
favourable results obtained without it
"""

import json
import numpy as np
import faiss
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

library = "Numpy"

LIB_PATH = {
    "Python": "py",
    "Numpy": "np", 
    "Pandas": "pd", 
    "PyTorch": "pt", 
    "Scikit-Learn": "sklearn", 
    "TensorFlow Keras": "tfkeras"
}

DATA_DIR = "../data"
DOCS_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "scraped_docs.json")
EMBED_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "embeddings.npy")
META_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_metadata.npy")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_index.bin")

MAX_TOKENS = 8191  

def chunk_text(text, max_tokens=MAX_TOKENS):
    """Naively chunk text based on token count approximation."""
    max_chars = max_tokens * 4
    chunks = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    return chunks

def generate_embedding(text):
    """Generates an embedding using OpenAI's text-embedding-ada-002 model."""
    try:
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding 
        norm = np.linalg.norm(embedding)
        return (np.array(embedding) / norm).astype("float32")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return None


def process_json_and_generate_embeddings():
    """Processes the JSON file, generates embeddings, and saves metadata."""
    try:
        with open(DOCS_PATH, 'r') as f:
            docs = json.load(f)
        print(f"✅ Successfully loaded {DOCS_PATH}")
    except Exception as e:
        print(f"❌ Error loading {DOCS_PATH}: {e}")
        return
    
    all_embeddings = []
    all_metadata = []

    for i, doc in enumerate(docs):
        doc_id = i
        url = doc.get("url", "")
        content = doc.get("content", "")

        try:
            chunks = chunk_text(content)
            for idx, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)
                if embedding is None:
                    continue  

                all_embeddings.append(embedding)
                all_metadata.append({
                    "doc_id": doc_id,
                    "url": url,
                    "chunk_index": idx,
                    "text": chunk
                })

            if i == 0 and idx == 0 and embedding is not None:
                print("\n🔹 Sample Embedding Output (First 10 dimensions):")
                print(embedding[:10])

            if (i + 1) % 5 == 0:
                print(f"✅ Processed {i + 1}/{len(docs)} documents")
                
        except Exception as e:
            print(f"❌ Error processing document {i}: {e}")

    try:
        np.save(EMBED_PATH, np.array(all_embeddings))
        np.save(META_PATH, np.array(all_metadata, dtype=object))
        print(f"💾 Saved embeddings to {EMBED_PATH}")
        print(f"💾 Saved metadata to {META_PATH}")
    except Exception as e:
        print(f"❌ Error saving .npy files: {e}")

def build_faiss_index():
    """Builds FAISS index from embeddings and deletes `embeddings.npy` after indexing."""
    try:
        embeddings = np.load(EMBED_PATH)
        metadata = np.load(META_PATH, allow_pickle=True)
        
        assert len(embeddings) == len(metadata), "❌ Embeddings and metadata count mismatch."
        embeddings = embeddings.astype('float32')

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)

        index.add(embeddings)
        print(f"✅ FAISS index built with {index.ntotal} vectors.")

        faiss.write_index(index, FAISS_INDEX_PATH)
        print(f"💾 FAISS index saved to {FAISS_INDEX_PATH}")
        
        if os.path.exists(EMBED_PATH):
            os.remove(EMBED_PATH)
            print(f"🗑️ Deleted {EMBED_PATH} as FAISS index is now built!")

    except Exception as e:
        print(f"❌ Error building FAISS index: {e}")

if __name__ == "__main__":
    process_json_and_generate_embeddings()
    build_faiss_index()
