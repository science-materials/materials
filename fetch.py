print("=== DEBUG: script started ===")

import os
import requests
import json
from datetime import date

def fetch_crossref_articles(query, years=(2025), limit=10):
    """
    query: поисковая фраза (например, "new materials research films")
    years: кортеж (start_year, end_year) — теперь по умолчанию 2025
    limit: количество статей
    """
    print(f"=== DEBUG: Starting Crossref fetch for '{query}' ===")
    
    # Формируем диапазон дат для фильтра
    start_date = f"{years[0]}-01-01"
    end_date = f"{years[1]}-12-31"
    
    url = "https://api.crossref.org/works"
    
    # Параметры запроса

BLACKLIST_WORDS = {"negro", "colonial", "vocabulary", "history", "culture", "art", "literature"}

def is_not_blacklisted(title: str) -> bool:
    t = title.lower()
    return not any(word in t for word in BLACKLIST_WORDS)

def is_relevant_by_content(title: str, abstract: str, subjects: list, search_terms: list) -> bool:
    t = title.lower()
    a = abstract.lower() if abstract else ""
    s = " ".join([sub.lower() for sub in subjects])
    
    for term in search_terms:
        term = term.lower()
        if term in t or term in a or term in s:
            return True
    return False

def fetch_articles():
    print(f"=== Starting fetch for: '{SEARCH_QUERY}' ===")
    
    # ВАЖНО: query (а не query.title) — поиск по всем полям
    params = {
        "query": SEARCH_QUERY,
        "filter": "type-name:journal-article,has-affiliation:true",
        "rows": MAX_ITEMS,
        "mailto": "your_email@example.com"
    }

    try:
        response = requests.get(CROSSREF_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

    items = data.get("message", {}).get("items", [])
    search_terms = SEARCH_QUERY.split()
    
    print(f"=== Raw hits before filtering: {len(items)} ===")
    
    clean_articles = []
    for item in items:
        title = item.get("title", ["No title"])
        abstract = item.get("abstract", "")
        subjects = item.get("subject", [])
        
        # Фильтр 1: чёрный список (убираем гуманитарный мусор)
        if not is_not_blacklisted(title):
            print(f"⛔ Skipped (blacklist): {title}")
            continue
        
        # Фильтр 2: проверка по содержанию (название/аннотация/ключевые слова)
        if not is_relevant_by_content(title, abstract, subjects, search_terms):
            print(f"⛔ Skipped (no match in content): {title}")
            continue
        
        # Дальше обычная обработка
        authors_list = item.get("author", [])
        authors_names = [f"{a.get('given', '')} {a.get('family', '')}".strip()
                         for a in authors_list if a.get('family')]
        authors_str = ", ".join(authors_names)

        doi = item.get("DOI", "")
        issued = item.get("issued", {}).get("date-parts", [[None]])
        year = issued if issued and isinstance(issued, int) else None

        clean_articles.append({
            "title": title,
            "authors": authors_str,
            "doi": doi,
            "year": year,
            "abstract": abstract,          # можно сохранить и в JSON, если нужно
            "keywords": subjects           # и ключевые слова тоже
        })

    print(f"=== Final articles after filtering: {len(clean_articles)} ===")

        data_dir = "_data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"=== DEBUG: Created directory '(data_dir)' ===")

        output_path = os.path.join(data_dir, "articles.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(clean_articles, f, ensure_ascii=False, indent=2)
            
        return clean_articles

    except Exception as e:
        print(f"=== DEBUG: Error occurred: {e} ===")
        return []

if __name__ == "__main__":
    # ТВОЯ НАСТРОЙКА: Меняй фразу здесь
    search_query = "new materials OR research OR films"
    
    papers = fetch_crossref_articles(search_query, years=(2025, 2025), limit=10)
    
    print(f"=== DEBUG: Scripta finished. Saved {len(papers)} articles ===")
