import requests
import json
import time
import re

# Stack Overflow API settings
API_URL = "https://api.stackexchange.com/2.3/search"
HEADERS = {"User-Agent": "StackOverflow-Error-Fetcher"}
PARAMS = {
    "order": "desc",
    "sort": "votes",
    "tagged": "pytorch",
    "intitle": "error",
    "site": "stackoverflow",
    "pagesize": 50,  # Fetch top 50 error-related questions
}

# Function to fetch Stack Overflow errors
def fetch_stackoverflow_errors():
    print("🔍 Fetching Python errors from Stack Overflow...")
    
    response = requests.get(API_URL, params=PARAMS, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Error fetching data: {response.status_code}")
        return []

    data = response.json()
    return data.get("items", [])

# Function to clean HTML tags from text
def clean_html(raw_html):
    """Removes HTML tags from the text"""
    clean_text = re.sub('<.*?>', '', raw_html)
    return clean_text.strip()

# Function to extract the first code snippet from the body
def extract_code_snippet(body):
    """Extracts first code snippet from Stack Overflow question body"""
    code_matches = re.findall(r"<code>(.*?)</code>", body, re.DOTALL)
    if code_matches:
        return clean_html(code_matches[0])  # Return first code snippet
    return None

# Function to process errors into errors.json format
def process_errors(questions):
    errors_data = []
    for idx, question in enumerate(questions):
        error_title = question.get("title", "Unknown Error")
        question_id = question.get("question_id", "")
        link = question.get("link", "")
        
        # Fetch detailed question data (including body & code)
        details_url = f"https://api.stackexchange.com/2.3/questions/{question_id}?site=stackoverflow&filter=withbody"
        details_response = requests.get(details_url, headers=HEADERS)
        details_data = details_response.json()
        
        if "items" in details_data and len(details_data["items"]) > 0:
            body = details_data["items"][0].get("body", "")
        else:
            body = "No details available."

        # Extract description and code snippet
        description = clean_html(body[:500])  # Limit description to first 500 chars
        code_snippet = extract_code_snippet(body)

        error_entry = {
            "exception": error_title,
            "message": error_title,  # Using title as the general message
            "code_snippet": code_snippet if code_snippet else "",
            "description": description
        }

        errors_data.append(error_entry)
        time.sleep(1)  # Prevent rate limiting

        print(f"✅ Processed error {idx + 1}/{len(questions)}: {error_title}")

    return errors_data

# Fetch errors and process them
questions = fetch_stackoverflow_errors()
errors_json = process_errors(questions)

# Save to errors.json
with open("errors.json", "w") as f:
    json.dump(errors_json, f, indent=4)

print("`errors.json` has been successfully generated!")
