from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from data.aitools import AiRequest
from data.aitools.google_genai_funcs import GetTrendEntities, GetEntityMetadata

from . import news_api

from core.config import collection_config as config

def get_trends_raw():
    url = config.fetch_trends_url

    opts = Options()
    for arg in config.selenium_args:
        opts.add_argument(arg)

    driver = webdriver.Firefox(options = opts)
    driver.get(url)
    
    try:
        trends_container = WebDriverWait(driver, config.trend_load_wait_time).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR,
                        f"[jsname='{config.trends_container_tag}']")) #wait for trends to load
        )
    except Exception as e:
        driver.quit()
        return None

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    names = [trend.text for trend in soup.find_all("div", class_ = config.trend_name_tag)]
    times = [time.text for time in soup.find_all("div", class_ = config.trend_started_tag)]
    list_len = config.trends_count
    return [{"name": name, "started_label": time_label}
                for name, time_label in zip(names[1:list_len], times[1:list_len])]

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