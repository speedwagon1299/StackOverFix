from config import SITE_CONFIG
from scraper import bfs_scrape

def main():
    print("Select the documentation to scrape:")
    for key, site in SITE_CONFIG.items():
        print(f"{key}. {site['name']}")

    choice = int(input("Enter the number: "))

    if choice not in SITE_CONFIG:
        print("[❌] Invalid choice. Exiting.")
        return

    site_config = SITE_CONFIG[choice]
    print(f"[🚀] Starting scrape for {site_config['name']} documentation...")
    bfs_scrape(site_config)

if __name__ == "__main__":
    main()
