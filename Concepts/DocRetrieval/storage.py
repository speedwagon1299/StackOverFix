import chromadb
from chromadb.config import Settings

class ChromaDBHandler:
    def __init__(self, collection_name='tfkeras_docs'):
        self.client = chromadb.Client(Settings())
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_embeddings(self, texts, embeddings, metadatas):
        """Stores embeddings with metadata in ChromaDB."""
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=[f"doc_{i}" for i in range(len(texts))]
        )
