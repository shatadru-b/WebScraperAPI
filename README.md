# WebScraperAPI

A FastAPI-based web API that searches the web for a given query, scrapes the top results using SerpAPI (Google Search), and returns the content as a downloadable text file or api response.

## Features
- Search the web using Google via SerpAPI
- Scrape and extract content from top search results
- Download results as a text file
- Configurable result limit

## Requirements
- Python 3.8+
- FastAPI
- Uvicorn
- requests
- beautifulsoup4
- google-search-results (SerpAPI client)
- python-dotenv

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/WebScraperAPI.git
   cd WebScraperAPI
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up SerpAPI key:**
   - Create a `.env` file in the project root:
     ```env
     SERPAPI_KEY=your_serpapi_key_here
     ```

## Running the API

Start the FastAPI server with Uvicorn:
```sh
uvicorn main:app --reload --host 0.0.0.0 --port 1234
```

## Usage

Send a GET request to:
```
http://localhost:1234/searchfor/<query>?limit=2
```
- Replace `<query>` with your search term.
- `limit` is optional (default: 3).
- The API will return a downloadable `.txt` file with the scraped results.

## Deployment

You can deploy this API to platforms like Render, Railway, or any cloud provider that supports Python web apps.

## Security
- Do **not** commit your `.env` file or API keys to public repositories.
- The `.gitignore` is set to ignore `.env` and other sensitive files.

## License
MIT
