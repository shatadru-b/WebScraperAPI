import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, parse_qs
from newspaper import Article

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/92.0.4515.131 Safari/537.36"
}


def clean_duckduckgo_url(url: str) -> str:
    """Extract the real target URL from DuckDuckGo redirect links."""
    parsed = urlparse(url)
    if parsed.netloc == "duckduckgo.com" and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        if "uddg" in qs:
            return unquote(qs["uddg"][0])
    return url


def fetch_article_content(url: str) -> str:
    """
    Extract meaningful article text using newspaper3k,
    fallback to BeautifulSoup if parsing fails.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # Extract summary/keywords
        return article.text.strip()
    except Exception:
        # Fallback: simple readability-based scrape
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Keep only meaningful tags
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
                tag.decompose()

            paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
            content = " ".join(paragraphs)

            return content[:5000].strip()  # limit size
        except Exception:
            return ""


def search_and_scrape(query: str, limit: int = 3):
    """
    Search DuckDuckGo for a query, visit top links, and extract article content.
    """
    search_url = f"https://duckduckgo.com/html/?q={query}"
    resp = requests.get(search_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    for idx, a in enumerate(soup.select(".result__a"), start=1):
        if idx > limit:
            break
        title = a.get_text()
        raw_url = a.get("href")
        url = clean_duckduckgo_url(raw_url)
        content = fetch_article_content(url)

        results.append({
            "title": title,
            "url": url,
            "content": content
        })

    return results
