print("=== DEBUG: script started ===")

import json
import os
import requests

# Константы
DATA_FILE = "articles.json"
EMAIL = "nanonauka@gmail.com"

def fetch_papers():
    url = "https://openalex.org"
    
    # Убрали фильтр по дате, берутся любые 10 статей
    params = {
        "per_page": 10,
        "sort": "relevance",
        "mailto": EMAIL,  # Polite Pool
    }
    
    headers = {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (mailto:{EMAIL})"
    }
    
    try:
        print("Fetching data from OpenAlex...")
        r = requests.get(url, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json().get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"[WARNING] API request failed: {e}")
        print("Returning empty list to prevent build failure.")
        return []

def format_paper(paper):
    title = paper.get("title", "No title")
    
    # Безопасное извлечение аннотации
    abstract = (paper.get("abstract") or "")[:350]
    if len(paper.get("abstract") or "") > 350:
        abstract += "…"
        
    journal = "Unknown journal"
    sources = paper.get("primary_location") or {}
    if sources and isinstance(sources, dict):
        source_details = sources.get("source") or {}
        journal = source_details.get("display_name", "Unknown journal")
        
    doi = paper.get("doi")
    oa_url = paper.get("open_access", {}).get("oa_url")
    
    if doi and doi.startswith("http"):
        doi_link = doi
    else:
        doi_link = f"https://doi.org{doi}" if doi else ""
        
    url_link = oa_url or doi_link
    date_str = paper.get("publication_date", "")
    
    return {
        "title": title,
        "abstract": abstract,
        "journal": journal,
        "url": url_link,
        "date": date_str,
    }

def save_articles(papers):
    if not papers:
        if os.path.exists(DATA_FILE):
            print(f"Keeping existing {DATA_FILE} unmodified due to API failure.")
        else:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            print(f"Created empty {DATA_FILE} to satisfy workflow conditions.")
        return
        
    formatted = [format_paper(p) for p in papers]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(formatted)} articles to {DATA_FILE}")

if __name__ == "__main__":
    papers = fetch_papers()
    save_articles(papers)
    
print(f"=== DEBUG: Scripta finished. Saved {len(results)} articles ===")
