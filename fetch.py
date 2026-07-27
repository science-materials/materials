print("=== DEBUG: script started ===")

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
    params = {
        "query": query,                 # Поисковая фраза
        "filter": f"from-pub-date:{start_date},until-pub-date:{end_date}",
        "sort": "published",            # Сортировка по дате публикации
        "order": "desc",                # Сначала самые новые
        "rows": limit                   # Количество результатов
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"=== DEBUG: Status Code: {response.status_code} ===")
        
        if response.status_code != 200:
            print(f"Error: API returned {response.status_code}")
            return []
            
        data = response.json()
        results = data.get("message", {}).get("items", [])
        
        clean_articles = []
        
        for item in results:
            # Извлекаем авторов (часто это самый сложный блок в JSON)
            authors = []
            if "author" in item:
                for author in item["author"]:
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                    if name:
                        authors.append(name)
            
            # Получаем DOI и ссылку
            doi = item.get("DOI", "No DOI")
            link = f"https://doi.org/{doi}" if doi else ""
            
            # Название журнала
            journal = ""
            if "container-title" in item and len(item["container-title"]) > 0:
                journal = item["container-title"][0]
            
            # Дата публикации (берем год)
            year = ""
            if "issued" in item and "date-parts" in item["issued"]:
                date_parts = item["issued"]["date-parts"][0]
                if len(date_parts) >= 1:
                    year = str(date_parts[0])
            
            abstract = item.get("abstract", "No abstract available")
            title = item.get("title", ["No Title"])[0] if isinstance(item.get("title"), list) else item.get("title", "No Title")

            clean_article = {
                "id": doi,
                "title": title,
                "authors": ", ".join(authors),
                "abstract": abstract,
                "journal": journal,
                "year": year,
                "link": link,
                "source": "Crossref"
            }
            clean_articles.append(clean_article)
            
        print(f"=== DEBUG: Saved {len(clean_articles)} real articles. ===")
        
        with open("articles.json", "w", encoding="utf-8") as f:
            json.dump(clean_articles, f, ensure_ascii=False, indent=2)
            
        return clean_articles

    except Exception as e:
        print(f"=== DEBUG: Error occurred: {e} ===")
        return []

if __name__ == "__main__":
    # ТВОЯ НАСТРОЙКА: Меняй фразу здесь
    search_query = "new materials research films"
    
    papers = fetch_crossref_articles(search_query, years=(2025, 2025), limit=10)
    
    print(f"=== DEBUG: Scripta finished. Saved {len(papers)} articles ===")
