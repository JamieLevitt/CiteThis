from .collection import (get_trend_entities_raw,
                            get_entity_data_raw, get_trend_articles_raw)
from .aitools.post_analysis import extract_instances

from structs.data import TrendStruct, EntityStruct, ArticleStruct

from core.config import collection_config as config

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

def __process_entities(trend_id: str) -> list[EntityStruct]:
    """
    Processes entity data for a given trend ID.
    
    Args:
        trend_id (str): The ID of the trend.
    
    Returns:
        list[EntityStruct]: A list of processed EntityStruct objects.
    """
    entity_raws = get_trend_entities_raw(trend_id)
    res = []
    
    if entity_raws is not None:
        for entity in entity_raws:
            # Check if the entity already exists in the database
            if not EntityStruct.is_in_db(entity):
                meta_raw = get_entity_data_raw(entity)
                
                # If request is succesful
                if meta_raw is not None:
                    # Extract entity metadata, ensuring values are None if missing
                    wiki_url = meta_raw["wiki_url"] if meta_raw["wiki_url"] is not None else None
                    handle_url = meta_raw["handle_url"] if meta_raw["handle_url"] is not None else None
                
                    # Create a new entity structure and store it in the database
                    struct = EntityStruct(
                        entity,
                        [keyword.replace(",", "") for keyword in meta_raw["keywords"]],
                        wiki_url,
                        handle_url
                    )
                    struct.insert_into_db()
                    res.append(struct)
            else:
                # Load existing entity from the database
                res.append(EntityStruct.load_from_db(entity))
    
    return res

def process_articles(trend_id: str) -> list[ArticleStruct]:
    """
    Processes articles related to a given trend ID.
    
    Args:
        trend_id (str): The ID of the trend.
    
    Returns:
        list[ArticleStruct]: A list of processed ArticleStruct objects.
    """
    articles_raw = get_trend_articles_raw(trend_id)
    res = []
    
    if articles_raw is not None:
        for article in articles_raw:
            # Remove the 'https://' prefix to get a clean URL
            url = article["url"].removeprefix("https://")
            
            # Check if the article already exists in the database
            if not ArticleStruct.is_in_db(url):
                struct = ArticleStruct(
                    url,
                    article["source"],
                    datetime.strptime(article["published"], config.news_raw_dt_format)
                    .replace(tzinfo=ZoneInfo(article["timezone"])).date()
                )
                struct.insert_into_db()
                res.append(struct)
            else:
                # Load existing article from the database
                res.append(ArticleStruct.load_from_db(url))
    
    return res

def __calc_trend_start_date(start_date_label: str) -> date:
    """
    Calculates the start date of a trend based on a label.
    
    Args:
        start_date_label (str): The label describing when the trend started.
    
    Returns:
        date: The calculated start date.
    """
    # Split label into [{number}, {quanitifier}] (or ["yesterday"])
    raw = start_date_label.split(" ")
    
    if len(raw) == 1: # If the label is "yesterday"
        return date.today() - timedelta(days=1)  
    elif raw[1].lower() == "hours": # Quantifier is hours
        return date.today()  # Assume today
    else: # Quantifier is day
        return date.today() - timedelta(days=int(raw[0]))  

def process_trend(trend_raw: dict):
    """
    Processes a trend by extracting its entities and articles, then storing it in the database.
    
    Args:
        trend_raw (dict): Raw trend data containing the topic and start date label.
    """
    # Process and fetch trend's entities
    entities = __process_entities(trend_raw["topic"])
    # Process and fetch trend's articles
    articles = process_articles(trend_raw["topic"])
    
    struct = TrendStruct(
        trend_raw["topic"],
        __calc_trend_start_date(trend_raw["started_label"]), # Calculate trend's start date
        entities,
        articles
    )
    
    struct.insert_into_db()
    
    # Link entities and articles to the trend in the database
    for entity in entities:
        struct.affirm_db_entity_link(entity.id)
    for article in articles:
        struct.affirm_db_article_link(article.id)

def process_post(post_body: str) -> dict:
    """
    Processes a social media post or text input, extracting relevant topics, entities, and articles.
    
    Args:
        post_body (str): The body of the post.
    
    Returns:
        dict: Processed post data containing topics, entities, and articles.
    """
    # Process post
    topics = extract_instances(post_body)
    
    # Return data structured for extension
    return {
        "topics": [
            {
                "topic": topic,
                "instances": instances,
                "entities": [
                    {"wiki_url": entity.wiki_url,
                     "twitter_url": entity.twitter_url}
                        for entity in TrendStruct.get_topic_entities(topic)
                ],
                "articles": [
                    {"url": article.id,
                     "source": article.source,
                     "published": article.published_date.strftime("%d/%m/%Y")}
                        for article in TrendStruct.get_topic_articles(topic)
                ]
            }
            for topic, instances in topics.items()
        ]
    }
