from pydantic import BaseModel

class PostBody(BaseModel):
    """
    Model used for API request type hinting.
    """
    text : str

class EntityData(BaseModel):
    """
    Model assisting API response type hinting.
    """
    wiki_url : str
    twitter_url : str

class ArticleData(BaseModel):
    """
    Model assisting API response type hinting.
    """
    url : str
    source : str
    published : str

class TrendData(BaseModel):
    """
    Model assisting API response type hinting.
    """
    topic : str
    instances : list[str]
    entities : list[EntityData]
    articles : list[ArticleData]

class APIResponse(BaseModel):
    """
    Model used for API response type hinting.
    """
    topics : list[TrendData]