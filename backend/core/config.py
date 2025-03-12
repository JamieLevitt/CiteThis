from os.path import join, dirname

from dotenv import load_dotenv
load_dotenv(dirname(__main__), ".env")

class data_config:
    db_name = "citethis"
    db_user = "administrator"
    db_pass = "xEfhWGPDQltjeGoZJjuu"
    db_host = "citethis-db.cbsiwywwk6pc.ap-southeast-2.rds.amazonaws.com"
    db_port = "5432"

    trends_table = "trending_topics"
    entities_table = "entities"
    articles_table = "articles"
    trend_entity_link_table = "links_trending_topics_to_entities"
    trend_article_link_table = "links_trending_topics_to_article_urls"

    trends_fetch_pause = 30 #minutes
    news_fetch_pause = 12 #hours
    purge_check_pause = 1 #days
    
    #db purging
    trend_lifespan = 7 #days
    article_lifespan = 2 #days
    entity_lifespan = 61 #days (2 months)

class collection_config:
    news_api_key = "pub_7338657c5b399dcf95c5a24c0230a517587f9"
    google_genai_key = "AIzaSyAHP4udsHwqXQZJ7O-ilz6QfdL3Nx1ea2o"

    fetch_trends_url = "https://trends.google.com/trending?geo=US&hl=en-US&category=14&hours=48"

    trends_count = 1
    trend_load_wait_time = 30 #seconds

    # news_sources = {
    #             "us": {
    #                     "left": [{"name": "New York Times", "domain": "nytimes.com"},
    #                              {"name": "AP", "domain": "apnews.com"}],
    #                     "centre": [""],
    #                     "right": [{"name": "FOX News", "domain": "foxnews.com"},
    #                               {"name": "The Washington Times", "domain": "washingtontimes.com"}] 
    #                     }
    #                 }

    excluded_news_sources = "indiatoday.in" #Non-US sources API considers to be US Sources
    
    trends_container_tag = "cC57zf"
    trend_name_tag = "mZ3RIc"
    trend_started_tag = "vdw3Ld"

    news_raw_dt_format = "%Y-%m-%d %H:%M:%S"
        
