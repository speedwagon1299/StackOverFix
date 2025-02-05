import requests
import re
import json
import time
import random
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


### 🔹 Safe API Request with Rate Limit Handling
def safe_api_request(url, params, retries=5, base_wait_time=4):
    """
    Makes a request to the Stack Overflow API and retries if rate-limited (429 error).
    Implements exponential backoff to avoid hitting the limit again.
    """
    for attempt in range(retries):
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            return response.json().get("items", [])

        elif response.status_code == 429:  # Too many requests
            wait_time = base_wait_time * (2 ** attempt) + random.uniform(0, 1)
            print(f"⏳ Rate limited (429). Retrying in {round(wait_time, 2)}s...")
            time.sleep(wait_time)  # Exponential backoff

        else:
            print(f"⚠️ API Error {response.status_code}: {response.text}")
            return None

    print("❌ Failed after multiple retries due to API rate limits.")
    return None


### 🔹 Check API Quota Before Running
def check_api_quota():
    """
    Checks the Stack Overflow API quota before making requests.
    If quota is too low, waits and retries later.
    """
    api_url = "https://api.stackexchange.com/2.3/info"
    params = {"site": "stackoverflow"}

    try:
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()

        quota_remaining = data.get("quota_remaining", "Unknown")
        print(f"📌 **API Quota Remaining:** {quota_remaining}")

        if quota_remaining == "Unknown" or quota_remaining == 0:
            print("❌ API quota too low! Waiting 2.5 hours before retrying...")
            time.sleep(9000)  # Sleep for 2.5 hours (2.5 * 3600)
            
            print("🔄 Retrying after 2.5 hours...")
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
            quota_remaining = data.get("quota_remaining", "Unknown")

            if quota_remaining == "Unknown" or quota_remaining == 0:
                print("❌ API quota still too low! Waiting another hour before retrying...")
                time.sleep(3600)  # Wait another hour
                return 0  # Skip processing this run

        return quota_remaining
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API request failed: {e}")
        return 0  # Assume no quota available


### 🔹 Save & Load Processed Question IDs
def save_processed_questions(processed_questions, filename="processed_questions.json"):
    """ Saves processed question IDs to a file to prevent duplicates. """
    with open(filename, "w") as f:
        json.dump(processed_questions, f, indent=4)

def load_processed_questions(filename="processed_questions.json"):
    """ Loads previously processed question IDs from a file. """
    try:
        with open(filename, "r") as f:
            return set(json.load(f))  # Load as a set for fast lookups
    except FileNotFoundError:
        return set()  # Return an empty set if file doesn't exist


def fetch_questions_with_errors(page=1, pagesize=100):
    """ Fetches Stack Overflow questions while handling API rate limits. """
    if check_api_quota() == 0:  # If quota is low, stop fetching
        return []

    api_url = "https://api.stackexchange.com/2.3/search"
    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": "python;pytorch",
        "site": "stackoverflow",
        "pagesize": pagesize,
        "page": page,
        "q": "error OR exception OR traceback OR failed OR not found OR TypeError OR ValueError OR ImportError"
    }

    questions = safe_api_request(api_url, params)
    return questions if questions else []



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
    Fetches the top 2 highest-voted answers with rate limit handling.
    """
    answer_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "pagesize": 2,
        "filter": "withbody"
    }

    return safe_api_request(answer_url, params)


def fetch_top_comment(answer_id):
    """
    Fetches the top comment from the highest-voted answer.
    Implements API rate limit handling and error handling.
    """
    comment_url = f"https://api.stackexchange.com/2.3/answers/{answer_id}/comments"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "pagesize": 1
    }
    
    comments = safe_api_request(comment_url, params)

    if comments is None:  # <- Handle API failure
        return None

    if comments:
        return comments[0].get("body", "")

    return None



def scrape_stackoverflow_details(question_url, base_wait_time=4):
    """
    Scrapes Stack Overflow page to extract:
    - Full question body
    - Code snippets from the question
    - Explicit error messages if available
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(question_url, headers=headers)
    if response.status_code == 200:
        print('Success: 200')
    elif response.status_code == 429:  # Too many requests
        wait_time = base_wait_time * 2 + random.uniform(0, 1)
        print(f"⏳ Rate limited (429). Retrying in {round(wait_time, 2)}s...")
        time.sleep(wait_time)
        return {"body": None, "code_snippets": [], "explicit_error_message": []}
    else:
        print(f"response: {response}")
        return {"body": None, "code_snippets": [], "explicit_error_message": []}
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract full question body
    body_elem = soup.find("div", class_="js-post-body")
    body = body_elem.get_text(strip=True) if body_elem else ""

    # Extract all code snippets from the question
    code_snippets = [code.get_text(strip=True) for code in soup.find_all("code")]

    # Extract explicit error messages
    error_pattern = r"\b([A-Za-z]+Error: .*?)\n"
    explicit_error_message = re.findall(error_pattern, body)

    return {
        "body": body,
        "code_snippets": code_snippets,
        "explicit_error_message": explicit_error_message
    }

def save_to_json(data, filename="python_errors_sample.json"):
    """ Saves collected data to a JSON file. """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def process_questions(num_questions=5000, save_every=100):
    """
    Fetches, filters, and processes Stack Overflow questions while avoiding duplicates.
    Automatically resumes after quota resets.
    """
    collected_questions = []
    processed_questions = load_processed_questions()  # Load previously processed question IDs
    page = 1

    print(f"🔍 Starting to fetch {num_questions} questions...")

    while len(collected_questions) < num_questions:
        print(f'🔄 Fetching questions from page {page}...')
        questions = fetch_questions_with_errors(page, pagesize=100)

        if not questions:
            print(f"⚠️ No questions returned on page {page}. Skipping to next page.")
            page += 1
            continue

        q_no = 1  # Question counter for debugging

        for q in questions:
            print(f"⚡ Processing question {q_no} on page {page}...")
            q_no += 1
            question_id = q.get("question_id")
            question_url = q.get("link")

            # Skip already processed questions
            if question_id in processed_questions:
                print(f"🔄 Skipping already processed question {question_id}.")
                continue  

            # Scrape question details
            scraped_data = scrape_stackoverflow_details(question_url)
            body_text = scraped_data.get("body", "")
            code_snippets = scraped_data.get("code_snippets", [])

            # Debugging: Log progress every 10 questions
            if q_no % 10 == 0 and body_text != None:
                print(f"📝 Question {q_no}: body_text length={len(body_text)}, code_snippets={len(code_snippets)}")

            # If no body text, use code snippets as fallback
            if not body_text and code_snippets:
                body_text = " ".join(code_snippets)

            # If neither body nor code snippets exist, discard the question
            if not body_text:
                print(f"⚠️ Skipping question {question_id} due to missing body text.")
                continue 

            # Ensure stack trace exists in the final body text
            if contains_stack_trace(body_text):
                print(f"✅ Stack trace detected in question {question_id}. Fetching answers...")

                # Fetch top answers
                answers = fetch_top_answers(question_id)
                if answers is None:  # <- Handle API failure
                    print(f"⚠️ Skipping answers for question {question_id} due to API failure.")
                    continue
                top_answers_data = []

                for answer in answers:
                    print(f"📝 Processing answer {answer.get('answer_id')}...")
                    answer_data = {
                        "answer_text": answer.get("body", ""),
                        "upvotes": answer.get("score", 0),
                        "answer_id": answer.get("answer_id"),
                        "top_comment": fetch_top_comment(answer.get("answer_id"))
                    }

                    # Extract code snippets from the answer
                    soup = BeautifulSoup(answer.get("body", ""), "html.parser")
                    answer_data["code_snippets"] = [code.get_text(strip=True) for code in soup.find_all("code")]

                    top_answers_data.append(answer_data)

                # Store final structured data
                collected_questions.append({
                    "title": q.get("title"),
                    "tags": q.get("tags", []),
                    "body": body_text,  # Fetched from scraping
                    "code_snippets": code_snippets,  # Extracted snippets from question
                    "explicit_error_message": re.findall(r"([A-Za-z]+Error: .*?)\n", body_text),  # Extract error messages
                    "creation_date": q.get("creation_date"),
                    "views": q.get("view_count"),
                    "top_answers": top_answers_data
                })

                # Mark question as processed
                processed_questions.add(question_id)

                # Save progress every `save_every` questions
                if len(collected_questions) % save_every == 0:
                    print(f"💾 Saving progress at {len(collected_questions)} questions...")
                    save_to_json(collected_questions, filename="python_errors_sample.json")
                    save_processed_questions(list(processed_questions))
                    print(f"✅ Data successfully saved.")

                if len(collected_questions) >= num_questions:
                    print(f"🏁 Goal reached! {num_questions} questions processed. Stopping.")
                    break

        page += 1
        print(f"🕒 Moving to next page: {page}")
        time.sleep(1)  # Avoid API Limits

    # Final save before exiting
    print("💾 Final save before exiting...")
    save_to_json(collected_questions, filename="python_errors_sample.json")
    save_processed_questions(list(processed_questions))
    print("✅ Final save complete.")

    return collected_questions



def store_in_faiss(questions, model_name="BAAI/bge-base-en-v1.5", batch_size=1000):
    """
    Converts question texts into embeddings using a better model and stores them in FAISS in batches.
    """
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    # Extract text-based fields for embedding
    texts = [q.get("title", "") + " " + q.get("body", "") for q in questions]

    # Create FAISS index
    dimension = model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatIP(dimension)

    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        embeddings = model.encode(batch_texts, normalize_embeddings=True)
        index.add(np.array(embeddings))
        print(f"✅ Stored {i + len(batch_texts)} embeddings in FAISS...")

    # Save FAISS index
    faiss.write_index(index, "pytorch_errors.index")
    print(f"✅ Final FAISS index saved with {len(texts)} questions.")


if __name__ == "__main__":
    print("🔍 Fetching and processing questions...")
    pytorch_questions = process_questions(num_questions=5000)

    print("💾 Saving dataset...")
    with open("python_errors_sample.json", "w") as f:
        json.dump(pytorch_questions, f, indent=4)

    print("✅ Done! Processed questions saved.")
