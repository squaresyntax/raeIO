import requests
from bs4 import BeautifulSoup
import time

def scrape_music_theory_and_industry():
    """
    Scrapes open music theory and genre/industry info (stub).
    """
    # Example: Wikipedia Music Theory, Metal-Archives, Bandcamp Blog, etc.
    sources = [
        "https://en.wikipedia.org/wiki/Music_theory",
        "https://en.wikipedia.org/wiki/Category:Rock_music_genres",
        "https://www.metal-archives.com/",
        "https://daily.bandcamp.com/",
        "https://pitchfork.com/",
        # add more as needed
    ]
    docs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in sources:
        try:
            page = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(page.text, "html.parser")
            # Simple extraction: all text in <p>
            for p in soup.find_all("p"):
                text = p.get_text().strip()
                if text:
                    docs.append({"source": url, "content": text})
            time.sleep(0.3)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return docs

def process_and_embed_music_data(agent):
    docs = scrape_music_theory_and_industry()
    for doc in docs:
        agent.vector_db.add_document(doc["content"], {"source": doc["source"]})
        time.sleep(0.05)
    return f"Indexed {len(docs)} music theory and industry content chunks."