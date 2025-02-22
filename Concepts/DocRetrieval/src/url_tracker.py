import json
import os

class URLTracker:
    def __init__(self, filename="scraped_urls.json"):
        self.filename = filename
        self.scraped_urls = self.load_scraped_urls()

    def load_scraped_urls(self):
        """Load scraped URLs from JSON file."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return set(json.load(f))
        return set()

    def save_scraped_urls(self):
        """Save scraped URLs to JSON file."""
        with open(self.filename, 'w') as f:
            json.dump(list(self.scraped_urls), f, indent=2)

    def is_scraped(self, url):
        """Check if the URL has already been scraped."""
        return url in self.scraped_urls

    def mark_as_scraped(self, url):
        """Mark URL as scraped and save."""
        self.scraped_urls.add(url)
        self.save_scraped_urls()
