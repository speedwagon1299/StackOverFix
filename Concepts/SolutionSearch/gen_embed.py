import json
import numpy as np
import torch
import faiss
from transformers import AutoTokenizer, AutoModel

# Load Stack Overflow dataset
try:
    with open("stackoverflow.json", "r") as f:
        stackoverflow_data = json.load(f)
    print("✅ Successfully loaded stackoverflow.json")
except Exception as e:
    print(f"❌ Error loading stackoverflow.json: {e}")
    exit(1)  # Exit script if file loading fails

# Load GraphCodeBERT model and tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
    model = AutoModel.from_pretrained("microsoft/graphcodebert-base")
    print("✅ Successfully loaded GraphCodeBERT model")
except Exception as e:
    print(f"❌ Error loading GraphCodeBERT model: {e}")
    exit(1)  # Exit script if model fails to load

def encode_with_graphcodebert(text):
    """Encodes text using GraphCodeBERT"""
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    except Exception as e:
        print(f"❌ Error encoding text: {e}")
        return np.zeros((768,))  # Return a zero-vector in case of failure

# Create embeddings for Stack Overflow solutions
stackoverflow_texts = [
    f"{entry['title']} | {entry['explicit_error_message']} | {entry['body']}" 
    for entry in stackoverflow_data
]

stackoverflow_embeddings = []

for i, text in enumerate(stackoverflow_texts):
    try:
        embedding = encode_with_graphcodebert(text)
        stackoverflow_embeddings.append(embedding)
        
        # Debug message for first embedding
        if i == 0:
            print("\n🔹 First Embedding Output (Sample):")
            print(embedding[:10])  # Print only the first 10 dimensions

        if (i + 1) % 500 == 0:
            print(f"✅ Processed {i + 1}/{len(stackoverflow_texts)} embeddings")
    
    except Exception as e:
        print(f"❌ Error processing entry {i}: {e}")

# Convert to NumPy array
stackoverflow_embeddings = np.array(stackoverflow_embeddings)

# Save embeddings
try:
    np.save("stackoverflow_embeddings.npy", stackoverflow_embeddings)
    print("✅ Stack Overflow embeddings successfully saved!")
except Exception as e:
    print(f"❌ Error saving embeddings: {e}")
