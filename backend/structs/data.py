from __future__ import annotations
from typing import TypeVar, Type

from data.database import insert_entry, fetch_entry, delete_entry
from core.config import db_config as db_config
from core.config import data_config as config

from datetime import datetime, date, timedelta, timezone
from dataclasses import dataclass, fields

D = TypeVar('D', bound='DataStruct')

#region INTERNAL
@dataclass
class DataStruct:
    table = None
    id_alias = None
    excluded_fields = []

    lifespan = None
    lifespan_attr = None

    id : str

    @classmethod
    def is_in_db(cls:Type[D], id:str) -> bool:
        try: return len(fetch_entry(cls.table, "*", cls.id_alias, (id,))) != 0
        except: return None

    @classmethod
    def load_from_db(cls:Type[D], id:str) -> D: 
        try: raw = fetch_entry(cls.table, "*",
                          cls.id_alias, (id,))
        except: return None
        
        if len(raw) == 0: return None
        resp = cls(*raw[0])
        return resp

    @classmethod
    def load_all_from_db(cls:Type[D]) -> list[D]:
        raws = fetch_entry(cls.table, "*")

        if len(raws) == 0: return None
        return [cls(*raw) for raw in raws if raw is not None]

    @classmethod
    def purge_db(cls:Type[D]):
        structs = cls.load_all_from_db()
        if structs is None: return
        for struct in structs:
            lifespan_marker = getattr(struct, struct.lifespan_attr)
            if type(lifespan_marker) is date: comp = (
                    datetime.now(timezone.utc) - timedelta(days = struct.lifespan)).date()
            else: comp = datetime.now(timezone.utc) - timedelta(days = struct.lifespan)

            if lifespan_marker <= comp:
                delete_entry(cls.table, cls.id_alias, (struct.id,))
        
    def get_table_vars(self) -> tuple:
        resp = {
            "fields": "".join(f"{field.name}," if field.name != "id" else f"{self.id_alias},"
                                            for field in fields(self)
                                            if not field.name.startswith("_")
                                            and field.name not in self.excluded_fields)
                                            .removesuffix(","),
            "vars": tuple([getattr(self, field.name) for field in fields(self) if field.name not in self.excluded_fields])
                }
        return resp

    def insert_into_db(self):
        table_vars = self.get_table_vars()
        insert_entry(self.table, table_vars["fields"], table_vars["vars"])

@dataclass
class EntityStruct(DataStruct):
    table = db_config.entities_table
    id_alias = "id"
    excluded_fields = []

    lifespan = config.entity_lifespan
    lifespan_attr = "last_linked"

    keywords : str
    wiki_url : str
    twitter_url : str
    last_linked : date = None

@dataclass
class ArticleStruct(DataStruct):
    table = db_config.articles_table
    id_alias = "url"
    excluded_fields = []

    lifespan = config.article_lifespan
    lifespan_attr = "last_linked"

    source : str
    published_date : date
    last_linked : date = None

@dataclass
class TrendStruct(DataStruct):
    table = db_config.trends_table
    id_alias = "topic"
    excluded_fields = ["entities", "articles"]

    lifespan = config.trend_lifespan
    lifespan_attr = "started_trending"

    started_trending : date
    entities : list[EntityStruct] = None
    articles : list[ArticleStruct] = None
    
    @staticmethod
    def load_all_with_kw() -> dict:
        return { trend.id: [keyword for entity in
                                    TrendStruct.get_topic_entities(trend.id)
                                        for keyword in entity.keywords]
                    for trend in TrendStruct.load_all_from_db()}

    @staticmethod
    def get_topic_entities(topic_id:str) -> list[EntityStruct]:
        ids = [id[0] for id in fetch_entry(db_config.trend_entity_link_table,
                                                "entity_id",
                                                "topic_id", (topic_id,))]
        
        return [EntityStruct.load_from_db(entity_id) for entity_id in ids]
    
    @staticmethod
    def get_topic_articles(topic_id:str) -> list[ArticleStruct]:
        ids = [id[0] for id in fetch_entry(db_config.trend_article_link_table,
                                    "article_url",
                                    "topic_id", (topic_id,))]
        
        return [ArticleStruct.load_from_db(article_id) for article_id in ids]
    
    def affirm_db_entity_link(self, entity_id:str):
        if entity_id not in self.get_topic_entities(self.id):
            insert_entry(db_config.trend_entity_link_table,
                            "topic_id, entity_id",
                            (self.id, entity_id))
        
    def affirm_db_article_link(self, article_url:str):
        if article_url not in TrendStruct.get_topic_entities(self.id):
            insert_entry(db_config.trend_article_link_table,
                            "topic_id, article_url",
                            (self.id, article_url))

    @staticmethod
    def calc_start_date(start_date_label:str) -> date:
        raw = start_date_label.split(" ")
        if len(raw) == 1:
            return date.today() - timedelta(days = 1) #for raw = ["yesterday"]
        elif raw[1].lower() == "hours":
            return date.today()
        else: 
            return date.today() - timedelta(days = int(raw[0]))
        
#endregion
