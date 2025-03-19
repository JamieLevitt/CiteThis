from pydantic import BaseModel

from datetime import datetime

class PostBody(BaseModel):
    text : str

class EntityData(BaseModel):
    wiki_url : str = None
    twitter_url : str = None

class ArticleData(BaseModel):
    url : str
    source : str
    published : datetime

class TrendData(BaseModel):
    topic : str
    instances : list[str]
    entities : list[EntityData]
    articles : list[ArticleData]