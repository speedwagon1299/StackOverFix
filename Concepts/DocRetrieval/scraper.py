import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
import json
import time

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_internal_links(base_url, page_url):
    """Extract all valid internal documentation links from a page, excluding anchor links."""
    try:
        response = requests.get(page_url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"[❌] Error fetching {page_url}: {e}")
        return []

    if response.status_code != 200:
        print(f"[❌] Failed to fetch {page_url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag.attrs["href"]
        full_url = urljoin(base_url, href)

        # Remove URL fragment (anchor) part
        full_url, _ = urldefrag(full_url)

        # Keep only valid internal documentation URLs
        if full_url.startswith(base_url) and is_valid_url(full_url):
            links.add(full_url)

    return list(links)

def scrape_content(url):
    """Extract main text content from a documentation page."""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"[❌] Error fetching content from {url}: {e}")
        return ""

    if response.status_code != 200:
        print(f"[❌] Failed to fetch content from {url}")
        return ""

    soup = BeautifulSoup(response.content, 'html.parser')
    texts = []

    # Target the main content area
    main_content = soup.find('div', {'role': 'main'})
    if not main_content:
        main_content = soup  # Fallback

    for tag in main_content.find_all(['h1', 'h2', 'h3', 'p', 'code', 'li']):
        text = tag.get_text(strip=True)
        if text:
            texts.append(text)

    return "\n".join(texts)

def bfs_scrape_and_collect(base_url):
    """Perform BFS to scrape all documentation pages, excluding anchor links."""
    queue = deque([base_url])
    visited = set()
    scraped_data = []

    while queue:
        current_url = queue.popleft()
        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"[🔍] Visiting: {current_url}")

        # Scrape content from current page
        content = scrape_content(current_url)
        if content:
            scraped_data.append({
                "url": current_url,
                "content": content
            })

        # Find and enqueue internal links, excluding anchor links
        child_links = get_internal_links(base_url, current_url)
        for link in child_links:
            if link not in visited:
                queue.append(link)

        # Add delay to avoid overloading the server
        time.sleep(0.3)

    # Save all scraped data to JSON
    with open("scraped_docs.json", "w") as f:
        json.dump(scraped_data, f, indent=2)

    print(f"[✅] Scraped {len(scraped_data)} pages (internal + leaf nodes).")
    return scraped_data
