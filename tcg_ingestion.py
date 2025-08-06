import requests
from bs4 import BeautifulSoup
import time

def scrape_tcgplayer_sets():
    """
    Scrape the list of TCG sets and basic info from TCGPlayer.
    """
    url = "https://www.tcgplayer.com/all-products"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    sets_data = []
    for set_div in soup.find_all("div", class_="search-result__content"):
        set_name = set_div.find("a").text.strip()
        set_url = set_div.find("a")["href"]
        sets_data.append({"name": set_name, "url": set_url})
    return sets_data

def scrape_ebay_trending(category="pokemon cards"):
    """
    Use eBay's search to pull trending items (public data).
    """
    url = f"https://www.ebay.com/sch/i.html?_nkw={category.replace(' ', '+')}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    items = []
    for item in soup.select(".s-item__info"):
        title = item.find("h3")
        price = item.find("span", class_="s-item__price")
        if title and price:
            items.append({"title": title.text.strip(), "price": price.text.strip()})
    return items

def scrape_starcitygames():
    """
    Example: scrape SCG's latest articles.
    """
    url = "https://starcitygames.com/articles/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    articles = []
    for entry in soup.find_all("article"):
        title = entry.find("h2")
        link = entry.find("a")
        if title and link:
            articles.append({"title": title.text.strip(), "url": link["href"]})
    return articles

def scrape_wizards_news():
    url = "https://magic.wizards.com/en/news"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    news = []
    for entry in soup.find_all("a", class_="card"):
        title = entry.find("div", class_="card__title")
        if title:
            news.append({"title": title.text.strip(), "url": entry["href"]})
    return news

def scrape_pokemon_company_news():
    url = "https://www.pokemon.com/us/pokemon-news/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    news = []
    for entry in soup.select(".news-article"):
        title = entry.find("h5")
        link = entry.find("a")
        if title and link:
            news.append({"title": title.text.strip(), "url": "https://www.pokemon.com" + link["href"]})
    return news

def scrape_bandai_news():
    url = "https://www.bandai.com/news/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    news = []
    for entry in soup.select(".news-content"):
        title = entry.find("h2")
        link = entry.find("a")
        if title and link:
            news.append({"title": title.text.strip(), "url": link["href"]})
    return news

def scrape_games_workshop_news():
    url = "https://www.warhammer-community.com/news/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    news = []
    for entry in soup.select("article"):
        title = entry.find("h2")
        link = entry.find("a")
        if title and link:
            news.append({"title": title.text.strip(), "url": link["href"]})
    return news

def process_and_embed_tcg_data(agent):
    """
    Scrapes and embeds all available data into the agent's vector DB.
    """
    sets = scrape_tcgplayer_sets()
    ebay = scrape_ebay_trending()
    scg = scrape_starcitygames()
    wotc = scrape_wizards_news()
    pokemon = scrape_pokemon_company_news()
    bandai = scrape_bandai_news()
    gw = scrape_games_workshop_news()
    all_chunks = sets + ebay + scg + wotc + pokemon + bandai + gw
    for entry in all_chunks:
        content = entry.get("title", entry.get("name", ""))
        meta = {"url": entry.get("url", ""), "source": entry.get("source", "")}
        agent.vector_db.add_document(content, meta)
        time.sleep(0.1)
    return f"Indexed {len(all_chunks)} TCG/hobby news and product items."