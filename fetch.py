import json
from datetime import date, timedelta
import requests

CONCEPTS = [
    "C27798704",  # Materials Science
    "C301893433",  # Thin Films
    "C129501741",  # Nanomaterials
]
DATA_FILE = "articles.json"

def fetch_papers():
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    concepts_filter = " OR ".join([f"concepts.id:{c}" for c in CONCEPTS])

    # 1. Ensure this is exactly api.openalex.org/works
    url = "https://openalex.org"

    params = {
        "filter": f"({concepts_filter}),from_publication_date:{yesterday},to_publication_date:{today}",
        "per_page": 7,
        "sort": "relevance",
    }

    # 2. Add headers to identify yourself and enter the polite pool
    headers = {
        "User-Agent": "mailto:your-email@example.com"  # Change to your actual email
    }

    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

def format_paper(paper):
    title = paper.get("title", "No title")
    abstract = (paper.get("abstract") or "")[:350]
    if len(paper.get("abstract", "")) > 350:
        abstract += "…"

    journal = "Unknown journal"
    sources = paper.get("primary_location") or {}
    if sources and isinstance(sources, dict):
        source_details = sources.get("source") or {}
        journal = source_details.get("display_name", "Unknown journal")

    doi = paper.get("doi")
    oa_url = paper.get("open_access", {}).get("oa_url")
    url_link = oa_url or (f"https://doi.org/{doi}" if doi else "")
    date_str = paper.get("publication_date", "")

    return {
        "title": title,
        "abstract": abstract,
        "journal": journal,
        "url": url_link,
        "date": date_str,
    }

def save_articles(papers):
    formatted = [format_paper(p) for p in papers]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(formatted)} articles to {DATA_FILE}")

if __name__ == "__main__":
    papers = fetch_papers()
    save_articles(papers)
