import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
import json
import time

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_internal_links(base_url, page_url, valid_link_prefix):
    """Extract valid internal documentation links from a page."""
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
        full_url, _ = urldefrag(full_url)  # Remove anchor links

        # Only keep valid internal documentation URLs
        if full_url.startswith(valid_link_prefix) and is_valid_url(full_url):
            links.add(full_url)

    return list(links)

def scrape_content(url, content_selector, content_tags, exclude_selectors):
    """Extract main content from a documentation page."""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"[❌] Error fetching content from {url}: {e}")
        return ""

    if response.status_code != 200:
        print(f"[❌] Failed to fetch content from {url}")
        return ""

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove excluded sections (e.g., sidebars)
    for selector in exclude_selectors:
        for tag in soup.find_all(selector['name'], selector['attrs']):
            tag.decompose()

    # Use site-specific selector to extract the main content
    main_content = soup.find(content_selector['name'], content_selector['attrs'])

    if not main_content:
        print(f"[⚠️] No specific content found for {url}, scraping entire page.")
        main_content = soup

    texts = []

    # Extract text from relevant tags
    for tag in main_content.find_all(content_tags):
        text = tag.get_text(separator=' ', strip=True)
        if text:
            texts.append(text)

    # Combine and deduplicate content
    content = "\n".join(list(dict.fromkeys(texts)))  # Remove duplicates while preserving order

    # Quality control: avoid saving pages with too little content
    if len(content.strip()) < 50:
        print(f"[⚠️] Extracted content from {url} seems too short or generic.")
        return ""

    return content

def bfs_scrape(site_config):
    """Perform BFS to scrape all documentation pages based on site config."""
    base_url = site_config['base_url']
    valid_link_prefix = site_config['valid_link_prefix']
    content_selector = site_config['content_selector']
    content_tags = site_config.get('content_tags', ['h1', 'h2', 'h3', 'p', 'code', 'li', 'pre'])
    exclude_selectors = site_config.get('exclude_selectors', [])

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
        content = scrape_content(current_url, content_selector, content_tags, exclude_selectors)
        if content:
            scraped_data.append({
                "url": current_url,
                "content": content
            })

        # Find and enqueue internal links
        child_links = get_internal_links(base_url, current_url, valid_link_prefix)
        for link in child_links:
            if link not in visited:
                queue.append(link)

        # Add delay to avoid overloading the server
        time.sleep(0.3)

    # Save all scraped data to JSON
    with open("np_scraped_data.json", "w") as f:
        json.dump(scraped_data, f, indent=2)

    print(f"[✅] Scraped {len(scraped_data)} pages for {site_config['name']}.")
    return scraped_data
