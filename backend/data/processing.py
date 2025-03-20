from .collection import (get_trend_entities_raw,
                            get_entity_data_raw, get_trend_articles_raw)

from .aitools.post_analysis import extract_instances

from structs.data import TrendStruct, EntityStruct, ArticleStruct

from core.config import collection_config as config

def __process_entities(trend_id:str) -> list[EntityStruct]:
    entity_raws = get_trend_entities_raw(trend_id)
    res = []
    if entity_raws is not None:
        for entity in entity_raws:
            if not EntityStruct.is_in_db(entity):
                meta_raw = get_entity_data_raw(entity)

                if meta_raw["wiki_url"] is not None:
                    wiki_url = meta_raw["wiki_url"] 
                else: 
                    wiki_url = None
                
                if meta_raw["handle_url"] is not None:
                    handle_url = meta_raw["handle_url"] 
                else: 
                    handle_url = None


                struct = EntityStruct(
                                entity, 
                                [keyword.replace(",", "") for keyword in meta_raw["keywords"]],
                                wiki_url, handle_url)
                struct.insert_into_db()
                res.append(struct)
            else:
                res.append(EntityStruct.load_from_db(entity))
                     
    return res

from datetime import datetime
from zoneinfo import ZoneInfo

def process_articles(trend_id:str) -> list[ArticleStruct]:
    articles_raw = get_trend_articles_raw(trend_id)
    res = []
    if articles_raw is not None:
        for article in articles_raw:
            url = article["url"].removeprefix("https://")
            if not ArticleStruct.is_in_db(url):
                struct = ArticleStruct(url,
                                       article["source"],
                                       datetime.strptime(article["published"],
                                                config.news_raw_dt_format)
                                                .replace(tzinfo = ZoneInfo(article["timezone"]))
                                                .date())
                struct.insert_into_db()
                res.append(struct)
            else: 
                res.append(ArticleStruct.load_from_db(url))
    
    return res

def process_trend(trend_raw:dict):
    entities = __process_entities(trend_raw["topic"])
    articles = process_articles(trend_raw["topic"])
    struct = TrendStruct(trend_raw["topic"],
                         TrendStruct.calc_start_date(trend_raw["started_label"]),
                         entities,
                         articles)
    
    struct.insert_into_db()
    for entity in entities: struct.affirm_db_entity_link(entity.id)
    for article in articles: struct.affirm_db_article_link(article.id)

def process_post(post_body:str) -> str: 
    topics = extract_instances(post_body)
    return {
        "topics": [
            {"topic": topic, 
             "instances": instances,
             "entities": [
                {"wiki_url": entity.wiki_url, "twitter_url": entity.twitter_url}
                for entity in TrendStruct.get_topic_entities(topic)],
             "articles": [
                {"url": article.id, "source": article.source, "published": article.published_date}
                for article in TrendStruct.get_topic_articles(topic)]
             } for topic, instances in topics.items()],
    }