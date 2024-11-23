from news.sources import NewsAggregator
from models.article import Articles
from services.openai import structured_chat_completion


aggregator = NewsAggregator()

def get_ai_news():
    # Fetch AI news
    ai_news = aggregator.fetch_ai_news()
    articles = structured_chat_completion(
        text=ai_news, 
        llm_model="gpt-4o-2024-08-06", 
        feature_model=Articles)
    return articles
    # print("AI News:\n")
    # # print each article
    # for article in articles.articles:
    #     print(article.summary)
    #     print("\n")
    
def get_infosec_news():
    # Fetch Infosec news
    infosec_news = aggregator.fetch_infosec_news()
    articles = structured_chat_completion(
        text=infosec_news, 
        llm_model="gpt-4o-2024-08-06", 
        feature_model=Articles)
    return articles

def get_crypto_news():
    # Fetch Crypto news
    crypto_news = aggregator.fetch_crypto_news()
    articles = structured_chat_completion(
        text=crypto_news, 
        llm_model="gpt-4o-2024-08-06", 
        feature_model=Articles)
    return articles