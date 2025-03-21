from __future__ import annotations
from typing import TypeVar, Type

from data.database import insert_entry, fetch_entry, delete_entry
from core.config import db_config as db_config
from core.config import data_config as config

from datetime import datetime, date, timedelta, timezone
from dataclasses import dataclass, fields

# Type hint for DataStruct or child class of DataStruct
D = TypeVar('D', bound='DataStruct')

@dataclass
class DataStruct:
    """
    Base class for data structures interacting with the database.
    """
    table = None
    id_alias = None
    excluded_fields = []
    lifespan = None
    lifespan_attr = None
    
    id: str

    @classmethod
    def is_in_db(cls: Type[D], id: str) -> bool:
        """Checks if an entry exists in the database."""
        try:
            return len(fetch_entry(cls.table, "*", cls.id_alias, (id,))) != 0
        except:
            return None

    @classmethod
    def load_from_db(cls: Type[D], id: str) -> D:
        """Loads a single entry from the database."""
        try:
            raw = fetch_entry(cls.table, "*", cls.id_alias, (id,))
        except:
            return None
        
        if len(raw) == 0:
            return None
        return cls(*raw[0])

    @classmethod
    def load_all_from_db(cls: Type[D]) -> list[D]:
        """Loads all entries from the database."""
        raws = fetch_entry(cls.table, "*")
        return [cls(*raw) for raw in raws if raw is not None] if raws else None

    @classmethod
    def purge_db(cls: Type[D]):
        """Removes expired entries from the database based on lifespan."""
        structs = cls.load_all_from_db()
        if not structs:
            return
        
        # Find earliest datetime for survival
        # All structs share same lifespan as it is class attribute
        cutoff = datetime.now(timezone.utc) - timedelta(days=structs[0].lifespan) 

        for struct in structs:
            lifespan_marker = getattr(struct, struct.lifespan_attr)
            
            if lifespan_marker:
                if type(lifespan_marker) is date:
                    # Compare date to date
                    if lifespan_marker <= cutoff.date():
                        delete_entry(cls.table, cls.id_alias, (struct.id,))
                else:
                    # Compare datetime to datetime
                    if lifespan_marker <= cutoff:
                        delete_entry(cls.table, cls.id_alias, (struct.id,))
    
    def get_table_vars(self) -> tuple:
        """Prepares table fields and values for database insertion."""
        resp = {
            "fields": "".join(f"{field.name},"
                        if field.name != "id" 
                            else f"{self.id_alias},"
                                for field in fields(self)
                                    if field.name not in self.excluded_fields)
                                        .removesuffix(","),
            "vars": tuple([
                        getattr(self, field.name) 
                            for field in fields(self)
                                if field.name not in self.excluded_fields])
                }
        return resp

    def insert_into_db(self):
        """Inserts the current instance into the database."""
        table_vars = self.get_table_vars()
        insert_entry(self.table, table_vars["fields"], table_vars["vars"])

@dataclass
class EntityStruct(DataStruct):
    """Represents an entity record in the database."""
    table = db_config.entities_table
    id_alias = "id"
    lifespan = config.entity_lifespan
    lifespan_attr = "last_linked"

    keywords: str
    wiki_url: str
    twitter_url: str
    last_linked: date = None

@dataclass
class ArticleStruct(DataStruct):
    """Represents an article record in the database."""
    table = db_config.articles_table
    id_alias = "url"
    lifespan = config.article_lifespan
    lifespan_attr = "last_linked"

    source: str
    published_date: date
    last_linked: date = None

@dataclass
class TrendStruct(DataStruct):
    """Represents a trending topic record in the database."""
    table = db_config.trends_table
    id_alias = "topic"
    excluded_fields = ["entities", "articles"]
    lifespan = config.trend_lifespan
    lifespan_attr = "started_trending"

    started_trending: date
    entities: list[EntityStruct] = None
    articles: list[ArticleStruct] = None
    
    @staticmethod
    def load_all_with_kw() -> dict[str, list[str]]:
        """Loads all trends along with associated keywords."""
        return {
            trend.id: [kw for entity in
                        TrendStruct.get_topic_entities(trend.id)
                            for kw in entity.keywords]
                                for trend in 
                                    TrendStruct.load_all_from_db()
        }
    
    @staticmethod
    def get_topic_entities(topic_id: str) -> list[EntityStruct]:
        """Fetches entities linked to a given topic."""
        entity_ids = [entry[0] for entry in
                        fetch_entry(
                            db_config.trend_entity_link_table,
                            "entity_id", "topic_id", (topic_id,))]
        
        return [EntityStruct.load_from_db(eid) for eid in entity_ids]
    
    @staticmethod
    def get_topic_articles(topic_id: str) -> list[ArticleStruct]:
        """Fetches articles linked to a given topic."""
        article_ids = [entry[0] for entry in
                        fetch_entry(
                            db_config.trend_article_link_table,

                            "article_url", "topic_id", (topic_id,))]
        return [ArticleStruct.load_from_db(aid) for aid in article_ids]
    
    def affirm_db_entity_link(self, entity_id: str):
        """Ensures a database link exists between a trend and an entity."""
        if entity_id not in {e.id for e in self.get_topic_entities(self.id)}:
            insert_entry(db_config.trend_entity_link_table,
                            "topic_id, entity_id",
                                (self.id, entity_id))
    
    def affirm_db_article_link(self, article_url: str):
        """Ensures a database link exists between a trend and an article."""
        if article_url not in {a.id for a in self.get_topic_articles(self.id)}:
            insert_entry(db_config.trend_article_link_table,
                            "topic_id, article_url",
                                (self.id, article_url))
