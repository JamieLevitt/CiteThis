from structs.data import TrendStruct, EntityStruct, ArticleStruct

from data.collection import get_trends_raw
from data.processing import process_trend, process_articles, process_post

def update_trends():
    raw_trends = get_trends_raw()
    for raw in raw_trends:
        if not TrendStruct.is_in_db(raw["name"]):
            process_trend(raw)

def update_articles():
    trends = TrendStruct.load_all_from_db()
    if trends is None: return
    for trend in trends: process_articles(trend.id)

def purge_dead_entries():    
    TrendStruct.purge_db()
    EntityStruct.purge_db()
    ArticleStruct.purge_db()

def analyse_post(post_body:str) -> str:
    return process_post(post_body)
