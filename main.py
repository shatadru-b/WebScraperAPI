from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from scraper import search_and_scrape

app = FastAPI()

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/searchfor/{query}")
def search(query: str, limit: int = 3):
    """
    API endpoint:
    Example: http://localhost:1234/searchfor/cricket?limit=2
    -> Scrapes top 2 links about cricket and returns text file.
    """
    # Run the scraper
    results = search_and_scrape(query, limit)

    # Save results into a text file
    file_path = os.path.join(OUTPUT_DIR, f"{query}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        for idx, r in enumerate(results, start=1):
            f.write(f"--- Result {idx} ---\n")
            f.write(f"Title: {r['title']}\n")
            f.write(f"URL: {r['url']}\n\n")
            f.write(f"Content:\n{r['content']}\n\n")
            f.write("=" * 80 + "\n\n")

    return FileResponse(file_path, media_type="text/plain", filename=f"{query}.txt")
