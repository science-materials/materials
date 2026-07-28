import os
import requests
import json

def is_not_blacklisted(title_str: str) -> bool:
    BLACKLIST_WORDS = {'negro', 'colonial'}
    t = title_str.lower()
    return not any(word in t for word in BLACKLIST_WORDS)

def is_relevant_by_content(title_str: str, abstract: str, subjects: list, search_terms: list) -> bool:
    t = title_str.lower()
    a = abstract.lower() if abstract else ""
    s = " ".join([sub.lower() for sub in subjects])

    for term in search_terms:
        term = term.lower()
        if term in t or term in a or term in s:
            return True
    return False

def fetch_crossref_articles(query: str, years: tuple = (2023, 2024), limit: int = 100):
    print(f"=== DEBUG: Starting Crossref fetch for '{query}' ===")

    url = "https://api.crossref.org/works"
    start_year, end_year = years

    # Оставляем только фильтр по датам — это даёт максимум результатов
    filter_str = f"from-pub-date:{start_year}-01-01,until-pub-date:{end_year}-12-31"

    params = {
        "query": query,
        "filter": filter_str,
        "rows": limit,
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
    search_terms = [
        "new materials",
        "novel materials",
        "advanced materials",
        "emerging materials",
        "functional materials",
        "smart materials",
        "nanomaterials",
        "metamaterials"
    ]

    print(f"=== Raw hits before filtering: {len(items)} ===")
    if len(items) == 0:
        # Для отладки выведем часть ответа, чтобы понять, что прислал Crossref
        message = data.get("message", {})
        print("=== DEBUG: Crossref response summary ===")
        print(f"status: {data.get('status')}")
        print(f"message keys: {list(message.keys())}")
        print(f"facets: {message.get('facets')}")
        print(f"total-results: {message.get('total-results')}")

    clean_articles = []

    for item in items:
        titles_list = item.get("title", [])
        if not titles_list:
            continue
        title = titles_list[0]

        abstract = item.get("abstract", "")
        subjects = item.get("subject", [])

        if not is_not_blacklisted(title):
            continue

        if not is_relevant_by_content(title, abstract, subjects, search_terms):
            continue

        authors_list = item.get("author", [])
        authors_names = [f"{a.get('given', '')} {a.get('family', '')}".strip()
                         for a in authors_list if a.get('family')]
        authors_str = ", ".join(authors_names)

        doi = item.get("DOI", "")

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
    search_query = "materials"  # более широкое слово, чем "new materials"
    papers = fetch_crossref_articles(search_query, years=(2023, 2024), limit=100)
    print(f"=== DEBUG: Script finished. Saved {len(papers)} articles ===")
