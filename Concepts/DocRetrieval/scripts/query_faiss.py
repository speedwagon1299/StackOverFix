import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
import torch
import os
from config import EMBED_MODEL

library = "Pandas"

LIB_PATH = {
    "Python": "py",
    "Numpy": "np", 
    "Pandas": "pd", 
    "PyTorch": "pt", 
    "Scikit-Learn": "sklearn", 
    "TensorFlow Keras": "tfkeras"
}

# Load FAISS index
DATA_DIR = "..\data_2"
faiss_index_path = 'faiss_index.bin'
faiss_index_path = os.path.join(DATA_DIR, LIB_PATH[library], faiss_index_path)
index = faiss.read_index(faiss_index_path)

# Load metadata
meta_path = 'faiss_metadata.npy'
meta_path = os.path.join(DATA_DIR, LIB_PATH[library], meta_path)
metadata = np.load(meta_path, allow_pickle=True)

# Load GraphCodeBERT (same as in embedder)
tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(EMBED_MODEL, trust_remote_code=True)

def generate_embedding(text):
    """Generates embeddings for input text using GraphCodeBERT."""
    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        # Mean pooling over token embeddings
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].numpy().astype('float32')

# Get user input
query_text = """
Access non-existent column in dataframe
"""

# Convert query to embedding
query_embedding = generate_embedding(query_text)

# Perform similarity search (fixed reshaping)
k = 3  # Number of nearest neighbors

distances, indices = index.search(query_embedding.reshape(1, -1), k)

# Display results
print(f"\n🔍 Top {k} Matches for Query: '{query_text}'")
for i, idx in enumerate(indices[0]):
    print(f"\nResult {i+1}:")
    print(f"Distance: {distances[0][i]:.4f}")
    print(f"Metadata: {metadata[idx]}")
