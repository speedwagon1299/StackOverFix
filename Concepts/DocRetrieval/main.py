import json
from scraper import bfs_scrape_and_collect
from embedder import Embedder
from storage import ChromaDBHandler

def main():
    base_url = "https://www.tensorflow.org/api_docs/python/tf/keras"

    # Step 1: BFS Crawl to scrape all documentation pages
    print("[🚀] Starting BFS documentation crawl...")
    scraped_pages = bfs_scrape_and_collect(base_url)

    # Step 2: Prepare texts and metadata for embedding
    print("[📋] Preparing content for embedding...")
    texts = [page["content"] for page in scraped_pages]
    metadatas = [{"source": page["url"]} for page in scraped_pages]

    # Step 3: Generate embeddings
    if texts:
        print("[🧠] Generating embeddings...")
        embedder = Embedder()
        embeddings = embedder.embed(texts)

        # Step 4: Store embeddings in ChromaDB
        print("[💾] Storing embeddings in ChromaDB...")
        db_handler = ChromaDBHandler()
        db_handler.add_embeddings(texts, embeddings, metadatas)

        print("[🎉] Completed! All documentation pages embedded and stored.")
    else:
        print("[⚠️] No content found to embed.")

if __name__ == "__main__":
    main()
