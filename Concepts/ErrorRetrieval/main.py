import requests
import re
import json
import time
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def fetch_questions_with_errors(page=1, pagesize=100):
    """
    Fetches Stack Overflow questions tagged with 'python' and 'pytorch' 
    that contain error-related keywords.
    """
    api_url = "https://api.stackexchange.com/2.3/search"
    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": "python;pytorch",
        "site": "stackoverflow",
        "pagesize": pagesize,           # Number of results per page
        "page": page,                   # Index of page number
        # Error related keywords to identify questions with error stack traces
        "q": "error OR exception OR traceback OR failed OR not found OR TypeError OR ValueError OR ImportError"
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    return data.get("items", [])


def contains_stack_trace(text):
    """
    Checks if the given text contains:
    - A Python stack trace (File "filename", line N)
    - A known Python error message (e.g., ValueError, TypeError)
    - The word 'Traceback' (used in Python error logs)
    """
    # Detects a Python stack trace (File "script.py", line 12)
    stack_trace_pattern = r"(File \".*?\", line \d+)"

    # Detects Python error messages like TypeError, ValueError, etc.
    error_pattern = r"\b([A-Za-z]+Error): .*"

    # Checks for "Traceback (most recent call last):"
    traceback_pattern = r"Traceback \(most recent call last\):"

    return (
        bool(re.search(stack_trace_pattern, text)) or
        bool(re.search(error_pattern, text)) or
        bool(re.search(traceback_pattern, text))
    )


def fetch_top_answers(question_id):
    """
    Fetches the top 2 highest-voted answers for a given question ID.
    """
    answer_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {"order": "desc", "sort": "votes", "site": "stackoverflow", "pagesize": 2}
    
    response = requests.get(answer_url, params=params)
    answers = response.json().get("items", [])
    return answers

def fetch_top_comment(answer_id):
    """
    Fetches the top comment from the highest-voted answer.
    """
    comment_url = f"https://api.stackexchange.com/2.3/answers/{answer_id}/comments"
    params = {"order": "desc", "sort": "votes", "site": "stackoverflow", "pagesize": 1}
    
    response = requests.get(comment_url, params=params)
    comments = response.json().get("items", [])
    
    return comments[0]["body"] if comments else None


def scrape_stackoverflow_details(question_url):
    """
    Scrapes Stack Overflow page to extract additional code snippets and text from body.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(question_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract full question body
    body = soup.find("div", class_="js-post-body").get_text(strip=True)

    # Extract all code snippets
    code_snippets = [code.get_text(strip=True) for code in soup.find_all("code")]

    return {"body": body, "code_snippets": code_snippets}


def process_questions(num_questions=5000):
    """
    Fetches, filters, and processes Stack Overflow questions containing PyTorch-related errors.
    """
    collected_questions = []
    page = 1

    # Collect num_questions questions
    while len(collected_questions) < num_questions:
        questions = fetch_questions_with_errors(page)

        # For each question
        for q in questions:

            # Ensure stack trace exists
            if contains_stack_trace(q["body"]):  
                question_id = q["question_id"]
                question_url = q["link"]

                # Fetch answers
                answers = fetch_top_answers(question_id)
                top_answers_data = []

                for answer in answers:
                    answer_data = {
                        "answer_text": answer["body"],
                        "upvotes": answer["score"],
                        "answer_id": answer["answer_id"],
                        "top_comment": fetch_top_comment(answer["answer_id"])
                    }

                    # Extract code snippets from the answer
                    soup = BeautifulSoup(answer["body"], "html.parser")
                    code_snippets = [code.get_text(strip=True) for code in soup.find_all("code")]
                    answer_data["code_snippets"] = code_snippets

                    top_answers_data.append(answer_data)

                # Scrape additional details from the Stack Overflow page
                scraped_data = scrape_stackoverflow_details(question_url)

                collected_questions.append({
                    "title": q["title"],
                    "tags": q["tags"],
                    "body": scraped_data["body"],
                    "code_snippets": scraped_data["code_snippets"],
                    "explicit_error_message": re.findall(r"([A-Za-z]+Error: .*?)\n", scraped_data["body"]),
                    "creation_date": q["creation_date"],
                    "views": q["view_count"],
                    "top_answers": top_answers_data
                })

                if len(collected_questions) >= num_questions:
                    break

        page += 1
        # Avoid rate limits
        time.sleep(1)  

    return collected_questions


def store_in_faiss(questions, model_name="BAAI/bge-base-en-v1.5"):
    """
    Converts question texts into embeddings using a better model and stores them in a FAISS index.
    """
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    # Extract text-based fields for embedding
    texts = [q["title"] + " " + q["body"] for q in questions]
    embeddings = model.encode(texts, normalize_embeddings=True)  # Normalization improves retrieval quality

    # Convert to FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Use Inner Product (IP) for cosine similarity
    index.add(np.array(embeddings))

    # Save FAISS index
    faiss.write_index(index, "pytorch_errors.index")
    print(f"✅ Stored {len(questions)} questions in FAISS with {model_name} embeddings.")


if __name__ == "__main__":
    print("Fetching and processing questions...")
    pytorch_questions = process_questions(num_questions=5000)

    print("Saving dataset as JSON...")
    with open("pytorch_errors.json", "w") as f:
        json.dump(pytorch_questions, f, indent=4)

    print("Storing in FAISS...")
    store_in_faiss(pytorch_questions)

    print("✅ Done! 5000 PyTorch error questions stored in FAISS.")
