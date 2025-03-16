from pyppeteer import launch

from data.aitools import AiRequest
from data.aitools.google_genai_funcs import GetTrendEntities, GetEntityMetadata

from . import news_api

from core.config import collection_config as config

async def get_trends_raw():
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
    
    await browser.close()
    return trends[:config.trends_count]

def get_trend_entities_raw(trend_id:str) -> dict:
    req = AiRequest(GetTrendEntities(trend_id))

    if not req.request_succesful: res = None
    else: res = req.response[trend_id]

    return res

def get_entity_data_raw(entity_name:str) -> dict:
    req = AiRequest(GetEntityMetadata(entity_name))
    
    if not req.request_succesful: res = None
    else: res = {"keywords": req.response["keywords"],
                 "wiki_url": req.response["wiki_url"],
                 "handle_url": req.response["handle_url"]}

    return res

def get_trend_articles_raw(topic_name:str) -> list[dict]:
    req = news_api.latest_api(
                        q = topic_name,
                        excludedomain = config.excluded_news_sources,
                        prioritydomain = "top",
                        category = "politics",
                        language = "en") 
    
    if req["status"] != "success": res = None
    else: res = [{"url": article["link"],
                  "source": article["source_name"]
                                if article["creator"] != "Associated Press"
                                    else "Associated Press", #account for AP being a coop
                  "published": article['pubDate'],
                  "timezone": article['pubDateTZ']
                  } for article in req["results"]]

    return res