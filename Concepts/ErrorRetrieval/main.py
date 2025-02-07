import requests
import re
import json
import time
import random
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from dotenv import load_dotenv
from check_req import check_api_quota

load_dotenv()

# when quota 0 give up
flag = 0

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
            quota = check_api_quota()
            if quota == 0:
                flag = 1
            return None

    print("❌ Failed after multiple retries due to API rate limits.")
    return None


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


### 🔹 Fetch Stack Overflow Questions
def fetch_questions_with_errors(page=1, pagesize=100):
    """ Fetches Stack Overflow questions while handling API rate limits. """
    api_url = "https://api.stackexchange.com/2.3/search"
    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": "pytorch",
        "site": "stackoverflow",
        "pagesize": pagesize,
        "page": page,
        "q": "error OR exception OR traceback OR failed OR not found OR TypeError OR ValueError OR ImportError",
        "key": os.getenv("STACK_OVERFLOW_API_KEY"),
    }

    return safe_api_request(api_url, params) or []


### 🔹 Check for Stack Traces
def contains_stack_trace(text):
    """ Checks if the given text contains a Python stack trace or error messages. """
    stack_trace_pattern = r"(File \".*?\", line \d+)"
    error_pattern = r"\b([A-Za-z]+Error): .*"
    traceback_pattern = r"Traceback \(most recent call last\):"

    return (
        bool(re.search(stack_trace_pattern, text)) or
        bool(re.search(error_pattern, text)) or
        bool(re.search(traceback_pattern, text))
    )


### 🔹 Fetch Answers
def fetch_top_answers(question_id):
    """ Fetches the top 2 highest-voted answers. """
    answer_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "pagesize": 2,
        "filter": "withbody",
        "key": os.getenv("STACK_OVERFLOW_API_KEY"),
    }

    return safe_api_request(answer_url, params) or []


### 🔹 Fetch Top Comment
def fetch_top_comment(answer_id):
    """ Fetches the top comment from an answer. """
    comment_url = f"https://api.stackexchange.com/2.3/answers/{answer_id}/comments"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "pagesize": 1,
        "key": os.getenv("STACK_OVERFLOW_API_KEY"),
    }

    comments = safe_api_request(comment_url, params)
    return comments[0].get("body", "") if comments else None


### 🔹 Scrape Stack Overflow Question Details
def scrape_stackoverflow_details(question_url):
    """ Scrapes Stack Overflow question for details. """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(question_url, headers=headers)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch question {question_url} (Status: {response.status_code})")
        time.sleep(4)
        return {"body": None, "code_snippets": [], "explicit_error_message": []}

    soup = BeautifulSoup(response.text, "html.parser")
    body_elem = soup.find("div", class_="js-post-body")
    body = body_elem.get_text(strip=True) if body_elem else ""

    code_snippets = [code.get_text(strip=True) for code in soup.find_all("code")]
    error_pattern = r"\b([A-Za-z]+Error: .*?)\n"
    explicit_error_message = re.findall(error_pattern, body)

    return {
        "body": body,
        "code_snippets": code_snippets,
        "explicit_error_message": explicit_error_message
    }


### 🔹 Save to JSON
def save_to_json(data, filename="pytorch_errors_sample.json"):
    """ Saves collected data to a JSON file. """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


### 🔹 Process Questions & Save Progress
def process_questions(num_questions=5000):
    """ Fetches, filters, and processes Stack Overflow questions. Saves after every page. """
    collected_questions = []
    processed_questions = load_processed_questions()
    page = 1

    while len(collected_questions) < num_questions:
        print(f'🔄 Fetching questions from page {page}...')
        questions = fetch_questions_with_errors(page, pagesize=100)

        if not questions:
            print(f"⚠️ No questions returned on page {page}. Skipping to next page.")
            page += 1
            continue

        for q in questions:
            question_id = q.get("question_id")
            if question_id in processed_questions:
                continue

            question_url = q.get("link")
            scraped_data = scrape_stackoverflow_details(question_url)
            body_text = scraped_data.get("body", "")
            code_snippets = scraped_data.get("code_snippets", [])
            print(f'Processing question {question_id}...')
            
            if not body_text and code_snippets:
                body_text = " ".join(code_snippets)

            if not body_text:
                print(f'No body found in question {question_id}. Skipping...')
                continue

            answers = fetch_top_answers(question_id)
            if flag == 1:
                print("Quota 0, exiting...")
                break
            top_answers_data = []
            for answer in answers:
                answer_data = {
                    "answer_text": answer.get("body", ""),
                    "upvotes": answer.get("score", 0),
                    "answer_id": answer.get("answer_id"),
                    "top_comment": fetch_top_comment(answer.get("answer_id"))
                }
                soup = BeautifulSoup(answer.get("body", ""), "html.parser")
                answer_data["code_snippets"] = [code.get_text(strip=True) for code in soup.find_all("code")]
                top_answers_data.append(answer_data)

            collected_questions.append({
                "title": q.get("title"),
                "tags": q.get("tags", []),
                "body": body_text,
                "code_snippets": code_snippets,
                "explicit_error_message": re.findall(r"([A-Za-z]+Error: .*?)\n", body_text),
                "creation_date": q.get("creation_date"),
                "views": q.get("view_count"),
                "top_answers": top_answers_data
            })

            processed_questions.add(question_id)

        save_to_json(collected_questions)
        save_processed_questions(list(processed_questions))
        print(f"✅ Page {page} data saved.")

        page += 1
        time.sleep(1)  # Avoid API Limits
        if flag == 1:
            break

    return collected_questions


if __name__ == "__main__":
    print("🔍 Fetching and processing questions...")
    pytorch_questions = process_questions(num_questions=5000)
    print("✅ Done! Processed questions saved.")
