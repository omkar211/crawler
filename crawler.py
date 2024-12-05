import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from concurrent.futures import ThreadPoolExecutor
import re

# Step 1: Function to fetch and parse a webpage
def fetch_page(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

# Step 2: Function to find product URLs on a webpage
def extract_product_urls(base_url, soup):
    product_urls = set()
    for link in soup.find_all("a", href=True):
        full_url = urljoin(base_url, link["href"])
        if re.search(r'/(product|item|p)/[\w\-]+', full_url):  # Match product-like patterns
            product_urls.add(full_url)
    return product_urls

# Step 3: Function to crawl a single website
def crawl_domain(domain):
    print(f"Starting crawl for {domain}")
    visited = set()  # Keep track of visited pages
    to_visit = {f"https://{domain}"}  # Start from the homepage
    product_urls = set()

    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited:
            continue

        visited.add(current_url)
        soup = fetch_page(current_url)  # Fetch and parse the current page
        if not soup:
            continue

        # Extract product URLs from the current page
        product_urls.update(extract_product_urls(current_url, soup))

        # Find more pages to visit
        for link in soup.find_all("a", href=True):
            full_url = urljoin(current_url, link["href"])
            if domain in full_url and full_url not in visited:
                to_visit.add(full_url)

    print(f"Finished crawl for {domain}")
    return domain, list(product_urls)

# Step 4: Function to crawl multiple websites in parallel
def crawl_multiple_domains(domains):
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:  # Use 10 threads for parallel processing
        futures = {executor.submit(crawl_domain, domain): domain for domain in domains}
        for future in futures:
            domain, product_urls = future.result()
            results[domain] = product_urls
    return results

# Step 5: Main function to take input and save output
if __name__ == "__main__":
    # Input list of domains
    domains = ["example1.com", "example2.com"]

    # Crawl all domains
    results = crawl_multiple_domains(domains)

    # Save results to a JSON file
    output_file = "product_urls.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Product URLs saved to {output_file}")
