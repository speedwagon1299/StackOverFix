import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

# Load GraphCodeBERT for embeddings
tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = AutoModel.from_pretrained("microsoft/graphcodebert-base")

MAX_TOKENS = 510  # Reduced to account for special tokens [CLS] and [SEP]

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
    """Generates embeddings for text chunks within token limits."""
    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].numpy()

def load_and_store_json(file_path, embeddings_file="pd_embeddings.npy", metadata_file="pd_metadata.npy"):
    """Loads JSON, chunks content, and saves embeddings and metadata as .npy files."""
    try:
        with open(file_path, 'r') as f:
            docs = json.load(f)
        print(f"✅ Successfully loaded {file_path}")
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return

    all_embeddings = []
    all_metadata = []

    for i, doc in enumerate(docs):
        url = doc.get("url", "")
        content = doc.get("content", "")
        try:
            chunks = chunk_text(content)
            print(f'{i}: ')
            for idx, chunk in enumerate(chunks):
                print(f'{idx}, {len(chunk.split())}')
                embedding = generate_embedding(chunk)
                all_embeddings.append(embedding)
                all_metadata.append({
                    "url": url,
                    "chunk_index": idx,
                    "content_snippet": chunk[:200]
                })

            if i == 0:
                print("\n🔹 First Embedding Output (Sample):")
                print(embedding[:10])  # Print first 10 dimensions

            if (i + 1) % 50 == 0:
                print(f"✅ Processed {i + 1}/{len(docs)} documents with chunking")
                # Save after every 50 documents
                np.save(embeddings_file, np.array(all_embeddings))
                np.save(metadata_file, np.array(all_metadata, dtype=object))
                print(f"💾 Intermediate save to {embeddings_file} and {metadata_file}")

        except Exception as e:
            print(f"❌ Error processing document {i}: {e}")

    # Final save
    try:
        np.save(embeddings_file, np.array(all_embeddings))
        np.save(metadata_file, np.array(all_metadata, dtype=object))
        print(f"✅ Final save to {embeddings_file}")
        print(f"✅ Final save to {metadata_file}")
    except Exception as e:
        print(f"❌ Error saving .npy files: {e}")

if __name__ == "__main__":
    # Example usage
    load_and_store_json("pd_scraped_docs.json")
