from pyppeteer import launch

from data.aitools import AiRequest
from data.aitools.google_genai_funcs import GetTrendEntities, GetEntityMetadata

from . import news_api
from core.config import collection_config as config

async def get_trends_raw() -> list[dict]:
    """
    Fetches raw trending topics from Google Trends using headless browsing.
    
    Returns:
        list[dict]: A list of trending topics with their labels.
    """
    # Launch browser
    browser = await launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False,
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    
    # Navigate to the Google Trends page
    await page.goto(config.fetch_trends_url)
    
    # Wait until topic elements are loaded
    await page.waitForSelector(config.trend_name_selector)
    await page.waitForSelector(config.trend_started_selector)
    
    # Find trends + when they started and compile them into dicts
    trends = await page.evaluate(f"""
        (trendNameSelector, trendStartedSelector) => {{
            // Get all trend names and started texts using the provided selectors
            const topics = Array.from(document.querySelectorAll(trendNameSelector)).map(el => el.innerText.trim());
            const starteds = Array.from(document.querySelectorAll(trendStartedSelector)).map(el => el.innerText.trim());
        
            // Combine the topics and started values
            return topics.map((topic, index) => ({'''{
                topic,
                started_label: starteds[index] || ''
            }'''}));
        }}""", config.trend_name_selector, config.trend_started_selector)
    
    #close browser
    await browser.close()

    return trends[:config.trends_count]

def get_trend_entities_raw(trend_id: str) -> dict | None:
    """
    Retrieves AI-generated entity data related to a trend.
    
    Args:
        trend_id (str): The ID of the trend.
    
    Returns:
        dict | None: A dictionary containing trend entity data or None if unsuccessful.
    """
    req = AiRequest(GetTrendEntities(trend_id))

    # Return None if request unsuccesful
    if not req.request_succesful:
        return None
    
    # Else return response
    return req.response[trend_id]

def get_entity_data_raw(entity_name: str) -> dict | None:
    """
    Retrieves metadata for a specific entity.
    
    Args:
        entity_name (str): The name of the entity.
    
    Returns:
        dict | None: A dictionary containing entity metadata or None if unsuccessful.
    """
    req = AiRequest(GetEntityMetadata(entity_name))
    
    # Return None if request unsuccesful
    if not req.request_succesful:
        return None
    
    # Else return response
    return {
        "keywords": req.response["keywords"],
        "wiki_url": req.response["wiki_url"],
        "handle_url": req.response["handle_url"]
    }

def get_trend_articles_raw(topic_name: str) -> list[dict] | None:
    """
    Retrieves 10 latest news articles related to a trending topic.

    NOTE - News is delayed by 12 hours due to API limitation
    
    Args:
        topic_name (str): The topic name to search for in news articles.
    
    Returns:
        list[dict] | None: A list of dictionaries containing article information or None if unsuccessful.
    """
    req = news_api.latest_api(
        q = topic_name,
        excludedomain = config.excluded_news_sources,
        prioritydomain = "top",
        category = "politics",
        language = "en"
    )
    
    # Return None if request unsuccesful
    if req["status"] != "success":
        return None
    
    # Else return article information 
    return [
        {
            "url": article["link"],
            "source": article["source_name"]
                        if article["creator"] != "Associated Press"
                            else "Associated Press",  # Account for AP being a cooperative
            "published": article['pubDate'],
            "timezone": article['pubDateTZ']
        }
        for article in req["results"]
    ]
