import os
import requests
import json

def is_not_blacklisted(title_str: str) -> bool:
    """Проверяет, нет ли в названии слов из черного списка."""
    BLACKLIST_WORDS = {'negro', 'colonial', 'vocabulary', 'history', 'culture', 'art', 'literature'}
    t = title_str.lower()
    return not any(word in t for word in BLACKLIST_WORDS)

def is_relevant_by_content(title_str: str, abstract: str, subjects: list, search_terms: list) -> bool:
    """Проверяет наличие поисковых термов в названии, аннотации или темах."""
    t = title_str.lower()
    a = abstract.lower() if abstract else ""
    s = " ".join([sub.lower() for sub in subjects])
    
    for term in search_terms:
        term = term.lower()
        if term in t or term in a or term in s:
            return True
    return False

def fetch_crossref_articles(query: str, years: tuple = (2025, 2025), limit: int = 10):
    """Основная функция для запроса статей из Crossref."""
    print(f"=== DEBUG: Starting Crossref fetch for '{query}' ===")
    
    url = "https://api.crossref.org/works"
    
    # Формируем фильтр по датам и типу документа
    start_year, end_year = years
    filter_str = f"type-name:journal-article,has-affiliation:true,from-pub-date:{start_year}-01-01,until-pub-date:{end_year}-12-31"
    
    params = {
        "query": query,
        "filter": filter_str,
        "rows": limit,  # Количество запрашиваемых строк
        "mailto": "nanonauka@gmail.com"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

    items = data.get("message", {}).get("items", [])
    search_terms = query.replace("OR", "").replace("AND", "").split()
    print(f"=== Raw hits before filtering: {len(items)} ===")
    
    clean_articles = []
    
    for item in items:
        # Crossref возвращает title как список, берем первый элемент
        titles_list = item.get("title", [])
        title = titles_list[0] if titles_list else "No title"
        
        abstract = item.get("abstract", "")
        subjects = item.get("subject", [])
        
        # Фильтр 1: чёрный список
        if not is_not_blacklisted(title):
            print(f"⛔ Skipped (blacklist): {title}")
            continue
            
        # Фильтр 2: проверка по содержанию
        if not is_relevant_by_content(title, abstract, subjects, search_terms):
            print(f"⛔ Skipped (no match in content): {title}")
            continue
            
        # Сбор авторов
        authors_list = item.get("author", [])
        authors_names = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list if a.get('family')]
        authors_str = ", ".join(authors_names)
        
        doi = item.get("DOI", "")
        
        # Получение года из структуры issued
        date_parts = item.get("issued", {}).get("date-parts", [[None]])
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        
        clean_articles.append({
            "title": title,
            "authors": authors_str,
            "doi": doi,
            "year": year,
            "abstract": abstract,
            "keywords": subjects
        })
        
    # Сохранение результатов
    data_dir = "_data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"=== DEBUG: Created directory ({data_dir}) ===")
        
    output_path = os.path.join(data_dir, "articles.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean_articles, f, ensure_ascii=False, indent=2)
        
    print(f"=== Final articles after filtering: {len(clean_articles)} ===")
    return clean_articles

if __name__ == "__main__":
    print("=== DEBUG: script started ===")
    search_query = "new materials"
    papers = fetch_crossref_articles(search_query, years=(2025, 2025), limit=20)
    print(f"=== DEBUG: Script finished. Saved {len(papers)} articles ===")
