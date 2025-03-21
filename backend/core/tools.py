from data.collection import get_trends_raw
from data.processing import process_trend, process_articles, process_post
from structs.data import TrendStruct, EntityStruct, ArticleStruct

async def update_trends() -> None:
    """
    Fetches raw trending topics and processes them if they are not already in the database.
    """
    # Retrieve raw trend data asynchronously
    raw_trends = await get_trends_raw()  
    # Check if the trend is already stored
    for raw in raw_trends:
        if not TrendStruct.is_in_db(raw["topic"]):  
            # Process and store the new trend
            process_trend(raw)  

def update_articles() -> None:
    """
    Processes articles for all trends currently stored in the database.
    """
    # Load all trends from the database
    trends = TrendStruct.load_all_from_db()  
    if trends is None:
        return  # Exit if there are no trends
    
    # Process and store articles related to each trend
    for trend in trends:
        # Allow for new articles to be processed
        articles = process_articles(trend.id)
        for article in articles:
            # Link articles to the trend in the database
            trend.affirm_db_article_link(article.id)

def purge_dead_entries() -> None:    
    """
    Purges outdated or irrelevant entries from the database for trends, entities, and articles.
    """
    TrendStruct.purge_db()  # Remove outdated trends
    EntityStruct.purge_db()  # Remove outdated entities
    ArticleStruct.purge_db()  # Remove outdated articles

def tag_post(post_body: str) -> str:
    """
    Processes a given post body and returns a tagged version of the post.
    
    Args:
        post_body (str): The text content of the post to be processed.
    
    Returns:
        str: The processed and tagged post.
    """
    # Process and return the tagged post
    return process_post(post_body)  