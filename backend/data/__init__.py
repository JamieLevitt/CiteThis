from newsdataapi import NewsDataApiClient

from core.config import collection_config as config

news_api = NewsDataApiClient(apikey = config.news_api_key)