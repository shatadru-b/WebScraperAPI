# scraper.py
from serpapi import GoogleSearch
from dotenv import load_dotenv
load_dotenv()
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from googlesearch import search  # from package: googlesearch-python

# --- Config ---
MIN_CONTENT_CHARS = 300  # discard thin/spammy pages
USER_AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Domains/patterns that are almost certainly ads or tracking
AD_HOST_FRAGMENTS = (
    "googlesyndication.", "googleadservices.", "doubleclick.",
    "g.doubleclick.", "adservice.google.", "tpc.googlesyndication.",
    "adsystem.", "adnxs.", "taboola.", "outbrain.", "bing.com/aclick",
)
# Optional: block social/retail sites if you only want articles
OPTIONAL_BLOCKED_DOMAINS = (
    "facebook.", "pinterest.", "linkedin.", "twitter.", "x.com",
    "instagram.", "youtube.", "youtu.be", "amazon.", "ebay.",
    "quora.", "reddit.", "news.google.", "webcache.googleusercontent.com",
)

TRACKING_QUERY_KEYS = {
    "gclid", "gbraid", "wbraid", "fbclid", "msclkid",
    "igshid", "yclid", "spm", "scid", "ref", "ref_src"
}


# --- Utility: strip common tracking params (keeps the useful URL) ---
def strip_tracking_params(url: str) -> str:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return url
        qs = parse_qs(parsed.query, keep_blank_values=True)

        # drop utm_* and known tracking keys
        filtered = {
            k: v for k, v in qs.items()
            if not (k.startswith("utm_") or k in TRACKING_QUERY_KEYS)
        }
        new_q = urlencode(filtered, doseq=True)
        return urlunparse(parsed._replace(query=new_q))
    except Exception:
        return url


# --- Utility: Check if URL is ad/sponsored/tracking ---
def is_ad_url(url: str) -> bool:
    """
    Return True if URL is likely an advertisement, sponsored, or tracking redirect.
    """
    # Non-http(s) → skip
    if not url.startswith(("http://", "https://")):
        return True

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    # Known ad/tracking hosts/patterns
    if any(fragment in host or fragment in url.lower() for fragment in AD_HOST_FRAGMENTS):
        return True

    # Google internal redirect/ads endpoints
    if host.endswith("google.com"):
        # /aclk is an ad click, /url with adurl=, /ads etc.
        if path.startswith("/aclk") or "adurl=" in query or path.startswith("/ads"):
            return True

    # Obvious script/asset files
    if path.endswith((".js", ".css")):
        return True

    # Optionally block social/retail (uncomment if desired)
    if any(b in host for b in OPTIONAL_BLOCKED_DOMAINS):
        return True

    return False


# --- Function: Scrape content from a single URL ---
def scrape_url(url: str, max_chars: int = 2000) -> str:
    try:
        response = requests.get(url, timeout=12, headers=USER_AGENT)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text content from paragraphs
        paragraphs = soup.find_all("p")
        content = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

        # Limit size of content
        content = content.strip()
        return content[:max_chars] if content else ""
    except Exception:
        return ""


# --- Function: Search and scrape results for a query (Google) ---
def search_and_scrape(query: str, max_results: int = 5, max_chars: int = 2000) -> str:
    results_data = []
    import os
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "SERPAPI_KEY")
    # Fetch more results than needed to account for filtering
    fetch_count = max_results * 3
    params = {
        "q": query,
        "num": fetch_count,
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    result = search.get_dict()
    for r in result.get("organic_results", []):
        url = r.get("link")
        title = r.get("title", "No title")
        if not url or ("is_ad_url" in globals() and is_ad_url(url)):
            continue
        content = scrape_url(url, max_chars=max_chars)
        if content:
            results_data.append({
                "title": title,
                "url": url,
                "content": content
            })
        if len(results_data) >= max_results:
            break
    return results_data