from datetime import date, timedelta
import json
import requests

CONCEPTS = [
    "C27798704",  # Materials Science
    "C301893433",  # Thin Films
    "C129501741",  # Nanomaterials
]

DATA_FILE = "articles.json"


def fetch_papers():
  # Вычисляем дату 30 дней назад для фильтрации за последний месяц
  last_month = (date.today() - timedelta(days=30)).isoformat()

  # Объединяем концепты через знак |
  concepts_ids = "|".join(CONCEPTS)
  url = "https://api.openalex.org/works"

  # Фильтрация по концептам и дате публикации начиная с last_month
  params = {
      "filter": f"concepts.id:{concepts_ids},from_publication_date:{last_month}",
      "per_page": 20,  ,  # Увеличено до 20, так как за месяц может быть больше статей
      "sort": "publication_date:desc",
  }
  headers = {"User-Agent": "mailto:nanonauka@gmail.com"}

  r = requests.get(url, params=params, headers=headers, timeout=30)
  r.raise_for_status()
  return r.json().get("results", [])


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
  url_link = oa_url or (f"https://doi.org{doi}" if doi else "")
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
