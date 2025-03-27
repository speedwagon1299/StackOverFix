import json
import numpy as np
import faiss
import os
import torch
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import requests
import spacy
from config import EMBED_MODEL

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Setup Paths
library = "Pandas"
LIB_PATH = {
    "Python": "py", "Numpy": "np", "Pandas": "pd", "PyTorch": "pt",
    "Scikit-Learn": "sklearn", "TensorFlow Keras": "tfkeras"
}
DATA_DIR = "../data_2"
DOCS_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "scraped_docs.json")
EMBED_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "embeddings.npy")
META_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_metadata.npy")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_index.bin")

nlp = spacy.load("en_core_web_sm")

# Load embedding model
tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(EMBED_MODEL, trust_remote_code=True)

def semantic_chunk_text(text, max_chars=1000):
    """Chunks text semantically using spaCy sentence boundaries."""
    doc = nlp(text)
    chunks, current = [], ""
    for sent in doc.sents:
        if len(current) + len(sent.text) <= max_chars:
            current += " " + sent.text
        else:
            chunks.append(current.strip())
            current = sent.text
    if current:
        chunks.append(current.strip())
    return chunks


def generate_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    with torch.no_grad():
        outputs = model(**inputs)
        cls = outputs.last_hidden_state[:, 0, :]
        cls = cls / cls.norm(dim=-1, keepdim=True)
        return cls[0].numpy().astype("float32")

def process_json_and_generate_embeddings():
    try:
        with open(DOCS_PATH, 'r') as f:
            docs = json.load(f)
        print(f"✅ Loaded {DOCS_PATH}")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return

    all_embeddings, all_metadata = [], []
    for i, doc in enumerate(docs):
        doc_id, url, content = i, doc.get("url", ""), doc.get("content", "")
        try:
            chunks = semantic_chunk_text(content)
            for idx, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)
                all_embeddings.append(embedding)
                all_metadata.append({
                    "doc_id": doc_id, "url": url,
                    "chunk_index": idx, "text": chunk
                })

            if i == 0:
                print("🔹 Sample Embedding:", embedding[:10])
            if (i + 1) % 5 == 0:
                print(f"✅ Processed {i + 1}/{len(docs)}")

        except Exception as e:
            print(f"❌ Error processing doc {i}: {e}")

    np.save(EMBED_PATH, np.array(all_embeddings))
    np.save(META_PATH, np.array(all_metadata, dtype=object))
    print("💾 Embeddings and metadata saved.")

def build_faiss_index():
    try:
        embeddings = np.load(EMBED_PATH)
        metadata = np.load(META_PATH, allow_pickle=True)
        assert len(embeddings) == len(metadata)

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings.astype('float32'))

        faiss.write_index(index, FAISS_INDEX_PATH)
        print(f"✅ FAISS index built with {index.ntotal} vectors.")

        if os.path.exists(EMBED_PATH):
            os.remove(EMBED_PATH)
            print(f"🗑️ Deleted {EMBED_PATH}")

    except Exception as e:
        print(f"❌ Error building index: {e}")

# ---------- MAIN ----------
if __name__ == "__main__":
    process_json_and_generate_embeddings()
    build_faiss_index()
