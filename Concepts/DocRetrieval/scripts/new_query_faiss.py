import numpy as np
import faiss
import os
import requests
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModel
import json

# Load API key
load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# === File Paths ===
library = "Python"
LIB_PATH = {
    "Python": "py", "Numpy": "np", "Pandas": "pd", "PyTorch": "pt",
    "Scikit-Learn": "sklearn", "TensorFlow Keras": "tfkeras"
}
DATA_DIR = "../data_2"
FAISS_INDEX_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_index.bin")
META_PATH = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_metadata.npy")

# === Embed Model ===
EMBED_MODEL = "nomic-ai/nomic-embed-text-v1"
tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(EMBED_MODEL, trust_remote_code=True)

def generate_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    with torch.no_grad():
        outputs = model(**inputs)
        cls = outputs.last_hidden_state[:, 0, :]
        cls = cls / cls.norm(dim=-1, keepdim=True)
        return cls[0].numpy().astype("float32")

def search_and_rerank(query_text, top_k=25, rerank_k=5):
    index = faiss.read_index(FAISS_INDEX_PATH)
    metadata = np.load(META_PATH, allow_pickle=True)

    query_embed = generate_embedding(query_text)
    D, I = index.search(query_embed.reshape(1, -1), top_k)

    retrieved = [{"score": D[0][i], **metadata[I[0][i]]} for i in range(top_k)]

    # NVIDIA rerank request
    payload = {
        "model": "nvidia/nv-rerankqa-mistral-4b-v3",
        "query": { "text": query_text },
        "passages": [{"text": r["text"]} for r in retrieved]
    }
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            "https://ai.api.nvidia.com/v1/retrieval/nvidia/nv-rerankqa-mistral-4b-v3/reranking",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        json_data = response.json()

        if "rankings" not in json_data:
            print("❌ NVIDIA API response missing 'rankings'. Full response:")
            print(json.dumps(json_data, indent=2))
            return

        # 🔁 Use correct 'rankings' field, not 'results'
        rankings = json_data["rankings"]

    except Exception as e:
        print(f"❌ NVIDIA API error: {e}")
        try:
            print("📦 Full API response:")
            print(response.text)
        except:
            pass
        return

    # Assign rerank_score based on returned ranking logits
    for r in rankings:
        idx = r["index"]
        score = r["logit"]
        retrieved[idx]["rerank_score"] = score

    top_reranked = sorted(retrieved, key=lambda x: x["rerank_score"], reverse=True)[:rerank_k]

    print(f"\n🔍 Top {rerank_k} Results for Query: {query_text.strip()}")
    for i, res in enumerate(top_reranked):
        print(f"\nResult {i+1}:")
        print(f"Score: {res['rerank_score']:.4f}")
        print(f"URL: {res['url']}")
        print(f"Text: {res['text'][:300]}...")

if __name__ == "__main__":
    # Example query
    query = "AttributeError list object has no attribute keys Python"
    search_and_rerank(query)
