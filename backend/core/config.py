import os
from dotenv import load_dotenv
load_dotenv()

class db_config:
    host = os.getenv("DB_HOST")
    user = "postgres"
    password = os.getenv("DB_PASSWORD")
    name = "postgres"

    trends_table = "trending_topics"
    entities_table = "entities"
    articles_table = "articles"
    trend_entity_link_table = "links_trending_topics_to_entities"
    trend_article_link_table = "links_trending_topics_to_article_urls"

class data_config:    
    #db purging
    trend_lifespan = 7 #days
    article_lifespan = 2 #days
    entity_lifespan = 61 #days (2 months)

class collection_config:
    news_api_key = os.getenv("NEWS_API_KEY")
    google_genai_key = os.getenv("GOOGLE_GENAI_KEY")

    fetch_trends_url = "https://trends.google.com/trending?geo=US&hl=en-US&category=14&hours=48"

    trends_count = 10

    excluded_news_sources = "indiatoday.in" #Non-US sources API considers to be US Sources
    
    trend_name_selector = "div.mZ3RIc"
    trend_started_selector = "div.vdw3Ld"

    news_raw_dt_format = "%Y-%m-%d %H:%M:%S"