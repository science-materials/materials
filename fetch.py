 
import requests
from datetime import date, timedelta
import json
import time

# Концепты OpenAlex: материалы, плёнки, наноматериалы
CONCEPTS = [
    "C27798704",  # Materials Science
    "C301893433",  # Thin Films
    "C129501741"   # Nanomaterials
]

DATA_FILE = "articles.json"
TRANSLATE_URL = "https://libretranslate.com/translate"

def fetch_papers():
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    concepts_filter = " OR ".join([f"concepts.id:{c}" for c in CONCEPTS])
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"({concepts_filter}),publication_date:[{yesterday} TO {today}]",
        "per_page": 7,
        "sort": "relevance",
    }

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

def translate_text(text):
    if not text or len(text.strip()) == 0:
        return ""
    payload = {
        "q": text,
        "source": "en",
        "target": "ru",
        "format": "text"
    }
    try:
        r = requests.post(TRANSLATE_URL, json=payload, timeout=15)
        r.raise_for_status()
        return r.json().get("translatedText", "")
    except Exception:
        # Если перевод не сработал — возвращаем пустую строку, чтобы не ломать весь скрипт
        return ""

def format_paper(paper):
    title_en = paper.get("title", "No title")
    abstract_en = (paper.get("abstract") or "")[:350]
    if len(paper.get("abstract", "")) > 350:
        abstract_en += "…"

    # Переводим заголовок и аннотацию
    title_ru = translate_text(title_en)
    abstract_ru = translate_text(abstract_en) if abstract_en else ""

    journal = ""
    sources = paper.get("primary_source") or []
    if sources and isinstance(sources, list) and len(sources) > 0:
        journal = sources[0].get("display_name", "Unknown journal")

    doi = paper.get("doi")
    oa_url = paper.get("open_access", {}).get("oa_url")
    url_link = oa_url or (f"https://doi.org/{doi}" if doi else "")

    date_str = paper.get("publication_date", "")

    return {
        "title_en": title_en,
        "title_ru": title_ru,
        "abstract_en": abstract_en,
        "abstract_ru": abstract_ru,
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
