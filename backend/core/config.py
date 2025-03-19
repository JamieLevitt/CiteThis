import os

class db_config:
    host = "35.244.83.45" #os.getenv("DB_HOST")
    user = "postgres"
    password = "K36A8`*GLQy>i)gp" #os.getenv("DB_PASSWORD")
    name = "postgres"

    trends_table = "trending_topics"
    entities_table = "entities"
    articles_table = "articles"
    trend_entity_link_table = "links_trending_topics_to_entities"
    trend_article_link_table = "links_trending_topics_to_article_urls"

class data_config:
    trends_fetch_pause = 30 #minutes
    news_fetch_pause = 12 #hours
    purge_check_pause = 1 #days
    
    #db purging
    trend_lifespan = 7 #days
    article_lifespan = 2 #days
    entity_lifespan = 61 #days (2 months)

class collection_config:
    news_api_key = "pub_7338657c5b399dcf95c5a24c0230a517587f9" #os.getenv("NEWS_API_KEY")
    google_genai_key = "AIzaSyAHP4udsHwqXQZJ7O-ilz6QfdL3Nx1ea2o" #os.getenv("GOOGLE_GENAI_KEY")

    fetch_trends_url = "https://trends.google.com/trending?geo=US&hl=en-US&category=14&hours=48"

    trends_count = 10

    excluded_news_sources = "indiatoday.in" #Non-US sources API considers to be US Sources
    
    trend_name_selector = "div.mZ3RIc"
    trend_started_selector = "div.vdw3Ld"

    news_raw_dt_format = "%Y-%m-%d %H:%M:%S"