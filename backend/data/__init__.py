from newsdataapi import NewsDataApiClient

from core.config import collection_config as config

# Initialize NewsDataApiClient with API key
news_api = NewsDataApiClient(apikey=config.news_api_key)