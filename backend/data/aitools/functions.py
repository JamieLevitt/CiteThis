from structs.ai import AiFunction

class GetTrendEntities(AiFunction):
    def __init__(self, obj_id:str):
        super().__init__(obj_id)
        
    prompt = lambda cls: f"""
        Using web search, work out and extract all named entities from the following topic: "{cls.obj_id}".
        
        Classify them as:
            - People
            - Organizations/Companies/Brands
            - Countries/States
            - Events
            - General Entities (currencies, locations, cultures, pejoratives etc.)

        These entities should be relevant to current news surrounding the topic, and should be returned in a JSON string representing a dict with the topic's name, and a list of the entities.
        In the case of an entity being referred to solely by their last name, or a name that could apply to two or more possible candidates, use Google Trends data, alongside the fact that the topic relates to current western Politics to work out specifically who/what is being referred to.
        In the case of a living politician and a living celebrity sharing a name, if unsure who the topic is referring to, assume it's the politician.
        Do not include abstract concepts unless specifically related to the trend/ current articles.

        Entities SHOULD NOT be sorted by type, and you are not required to find one or more of each type, only relevant ones

        Once you have all these, return them in a json string representing a python dictionary
        
        Response Structure: {'{"TOPIC_NAME": ["ENTITY_NAME_1", "ENTITY_NAME_2", "ENTITY_NAME_3", ...]}'}
        """

class GetEntityMetadata(AiFunction):
    def __init__(self, obj_id:str):
        super().__init__(obj_id)
        
    prompt = lambda cls: f"""
    Based on the following recent news about the entity "{cls.obj_id}":
        1. Generate a list of keywords that can be used to identify the entity:
            - Consider what commonly appears in tweets and discussions about this entity.
            - Include names & nicknames the entity is known by/ commonly refered to as
            - If a name has a common transliterated spelling, include both the Anglicized and transliterated spellings
            - If a name is spelled in a non-English language using Latin script (e.g., French, Spanish, Portuguese), include both the Anglicized and native spellings
        2. Get the url to the entity's wikipedia article:
            - In the case of events, if it is both recurring and dated, return the Wikipedia article for that specific iteration, if it is not dated and/or not recurring, return the general article.
            - Give it in the format: 'en.wikipedia.org/wiki/ARTICLE_NAME'
        3. Get the url to the entity's twitter handle:
            - If the entity is a country/state/territory or organisation that does not directly have a Twitter/X handle, use the handle of the current government/governing body
            - Once you find the handle (username), construct the full Twitter/X URL using the format: 'x.com/handle'
            - If you are unable to find a Twitter/X handle, consider possibilities from Google search results when searching 'twitter' + the entity's name, as well as news results
            - If you still cannot find a handle, whether that be because the entity, or its government/governing body, doesn't have one, return null. This should be your absolute last resort, and avoided if possible

        In the case of an entity being referred to solely by their last name, or a name that could apply to two or more possible candidates, use Google Trends data, alongside the fact that the topic relates to current western Politics to work out specifically who/what is being referred to.
        In the case of a living politician and a living celebrity sharing a name, if unsure who the topic is referring to, assume it's the politician.
        Filter out descriptors, EXCEPT when the entity is an 'idea,' 'concept,' or 'rumor.' In these cases, the descriptor is a key part of the entity's identity.
        An 'idea,' 'concept,' or 'rumor' entity is typically a phrase that represents a belief, theory, or allegation, especially one that is being discussed or debated in the context of western politics.

    Once you have all these, return them in a json string representing a python dictionary, with the 

    Response Structure: {'{"keywords": ["ENTITY_KEYWORD_1", "ENTITY_KEYWORD_2", "ENTITY_KEYWORD_3", ...], "wiki_url": "en.wikipedia.org/wiki/ENTITY_ARTICLE_NAME", "handle_url": "x.com/ENTITY_HANDLE"}'}
    """