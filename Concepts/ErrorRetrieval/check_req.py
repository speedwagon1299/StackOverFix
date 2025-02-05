import requests
import re
import json
import time
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests

def check_api_quota():
    """
    Checks the Stack Overflow API quota before making requests.
    """
    api_url = "https://api.stackexchange.com/2.3/info"
    params = {"site": "stackoverflow"}
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()
        print(f"📌 **API Quota Information:**")
        print(f"🔹 **Total Quota:** {data.get('quota_max', 'Unknown')}")
        print(f"🔹 **Remaining Calls:** {data.get('quota_remaining', 'Unknown')}")
        print(f'Full Response: {data}')
        return data.get('quota_remaining', 'Unknown')  # Return remaining quota for further checks

    except requests.exceptions.RequestException as e:
        print(f"⚠️ API request failed: {e}")
        return 0  # Assume no quota available if request fails
    

print(check_api_quota())