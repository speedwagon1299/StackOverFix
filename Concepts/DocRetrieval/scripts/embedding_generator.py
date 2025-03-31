"""
Processes scraped_docs.json → Generates FAISS embeddings & metadata → Builds FAISS index.
Deletes embeddings.npy after indexing.
"""

import json
import numpy as np
import faiss
import os
import torch
from transformers import AutoTokenizer, AutoModel
from config import EMBED_MODEL

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


tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(EMBED_MODEL, trust_remote_code=True)

MAX_TOKENS = 510 

def chunk_text(text, max_tokens=MAX_TOKENS):
    """Chunks text into segments based on token limits."""
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)
    return chunks


def generate_embedding(text):
    """Generates a pooled embedding with proper token limits and attention masking."""
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding="max_length"
    )
    
    with torch.no_grad():
        outputs = model(**inputs)
        last_hidden = outputs.last_hidden_state 
        attention_mask = inputs["attention_mask"].unsqueeze(-1) 

        masked_hidden = last_hidden * attention_mask
        summed = masked_hidden.sum(dim=1)
        counts = attention_mask.sum(dim=1)
        mean_pooled = summed / counts  
        embedding = mean_pooled[0]
        embedding = embedding / embedding.norm() 
        return embedding.numpy().astype('float32')


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
                all_embeddings.append(embedding)
                all_metadata.append({
                    "doc_id": doc_id,  
                    "url": url,
                    "chunk_index": idx,
                    "text": chunk  
                })

            if i == 0:
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
        index = faiss.IndexFlatL2(dimension)

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
