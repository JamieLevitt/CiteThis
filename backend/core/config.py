import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class db_config:
    """
    Database configuration settings, including connection credentials and table names.
    """
    host = os.getenv("DB_HOST") # Environment variable
    user = "postgres"
    password = os.getenv("DB_PASSWORD") # Environment variable
    name = "postgres"

    # DB table names
    trends_table = "trending_topics"
    entities_table = "entities"
    articles_table = "articles"
    trend_entity_link_table = "links_trending_topics_to_entities"
    trend_article_link_table = "links_trending_topics_to_article_urls"

class data_config:    
    """
    Data retention settings defining how long different data types are kept in the database.
    """
    trend_lifespan = 7  # Number of days a trending topic is stored
    article_lifespan = 2  # Number of days an article is stored
    entity_lifespan = 61  # Number of days an entity is stored (approx. 2 months)

class collection_config:
    """
    Configuration for data collection, including API keys and scraping settings.
    """
    news_api_key = os.getenv("NEWS_API_KEY") # Environment variable
    google_genai_key = os.getenv("GOOGLE_GENAI_KEY") # Environment variable

    # Google Trends URL to fetch trending topics
    fetch_trends_url = "https://trends.google.com/trending?geo=US&hl=en-US&category=14&hours=48"

    # Number of trends to fetch
    trends_count = 10

    # Excluded news sources (API may misclassify non-US sources as US sources)
    excluded_news_sources = "indiatoday.in"
    
    # CSS Selectors for parsing Google Trends page
    trend_name_selector = "div.mZ3RIc"
    trend_started_selector = "div.vdw3Ld"

    # Date format used in raw news data
    news_raw_dt_format = "%Y-%m-%d %H:%M:%S"
