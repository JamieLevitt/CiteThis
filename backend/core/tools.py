from structs.data import TrendStruct, EntityStruct, ArticleStruct

from data.collection import get_trends_raw
from data.processing import process_trend, process_articles

def update_trends():
    raw_trends = get_trends_raw()
    for raw in raw_trends:
        print(raw)
        print(TrendStruct.is_in_db(raw["name"]))
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