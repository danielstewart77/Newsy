import feedparser
import requests
import os

from dotenv import load_dotenv

load_dotenv(dotenv_path='secrets.env')

class NewsAggregator:
    def __init__(self):
        self.headers = {
            "User-Agent": "NewsAggregator/1.0",
            "Accept": "application/json",
        }

    # Function to fetch RSS feeds
    def fetch_rss(self, urls):
        results = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    results.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.summary if 'summary' in entry else "No summary available",
                    })
            except Exception as e:
                print(f"Error fetching RSS feed from {url}: {e}")
        return results

    # Function to fetch data from News APIs
    def fetch_api(self, urls):
        results = []
        for url in urls:
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    results.append(response.json())
                else:
                    print(f"Error fetching API data from {url}: {response.status_code}")
            except Exception as e:
                print(f"Error fetching API data from {url}: {e}")
        return results

    # Stub function to scrape websites
    def scrape_site(self, urls):
        results = []
        for url in urls:
            # Implement scraping logic here for each URL
            results.append({
                "url": url,
                "data": "Scraped content placeholder"
            })
        return results

    # Function to aggregate AI news
    def fetch_ai_news(self):
        rss_urls = [
            "https://www.wired.com/feed/tag/ai/latest/rss",
            "https://news.mit.edu/rss/topic/artificial-intelligence2",
            "https://www.artificial-intelligence.blog/rss-feeds"
        ]
        api_urls = [
            f"https://newsapi.org/v2/everything?q=AI&apiKey={os.getenv('NEWS_API_KEY')}",
            "https://api.gdeltproject.org/api/v2/geo/geo?query=AI"
        ]
        websites = [
            "https://openai.com/blog/",
            "https://deepmind.com/blog"
        ]
        return {
            "rss": self.fetch_rss(rss_urls),
            "api": self.fetch_api(api_urls),
            "scraped": self.scrape_site(websites)
        }

    # Function to aggregate Infosec news
    def fetch_infosec_news(self):
        rss_urls = [
            "https://www.infosecurity-magazine.com/rss/news/",
            "https://krebsonsecurity.com/feed/",
            "https://www.csoonline.com/news/index.rss"
        ]
        api_urls = [
            f"https://newsapi.org/v2/everything?q=cybersecurity&apiKey={os.getenv('NEWS_API_KEY')}",
            "https://api.threatpost.com/v1/articles/"
        ]
        websites = [
            "https://www.darkreading.com/",
            "https://thehackernews.com/"
        ]
        return {
            "rss": self.fetch_rss(rss_urls),
            "api": self.fetch_api(api_urls),
            "scraped": self.scrape_site(websites)
        }

    # Function to aggregate Crypto news
    def fetch_crypto_news(self):
        rss_urls = [
            "https://cointelegraph.com/rss",
            "https://news.bitcoin.com/feed/",
            "https://coinjournal.net/feeds/"
        ]
        api_urls = [
            "https://api.coingecko.com/api/v3/news?category=cryptocurrency"
        ]
        websites = [
            "https://bitcoinmagazine.com/",
            "https://cryptoslate.com/"
        ]
        return {
            "rss": self.fetch_rss(rss_urls),
            "api": self.fetch_api(api_urls),
            "scraped": self.scrape_site(websites)
        }
