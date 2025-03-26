import numpy as np
import faiss
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
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

# Define paths
DATA_DIR = "..\\data_2"
faiss_index_path = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_index.bin")
meta_path = os.path.join(DATA_DIR, LIB_PATH[library], "faiss_metadata.npy")

# Load FAISS index and metadata
index = faiss.read_index(faiss_index_path)
metadata = np.load(meta_path, allow_pickle=True)

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

# Input your query
query_text = """
What does the 'axis' parameter in numpy.mean() do?
"""

# Get embedding for query
query_embedding = generate_embedding(query_text)
if query_embedding is None:
    print("❌ Failed to generate embedding. Exiting.")
    exit()

# Search in FAISS index
k = 3
distances, indices = index.search(query_embedding.reshape(1, -1), k)

# Display results
print(f"\n🔍 Top {k} Matches for Query: '{query_text.strip()}'")
for i, idx in enumerate(indices[0]):
    print(f"\nResult {i+1}:")
    print(f"Distance: {distances[0][i]:.4f}")
    print(f"Metadata: {metadata[idx]}")
