from google import genai
from google.genai import types, errors

from structs.ai import AiFunction

from core.config import collection_config as config

import json, re

_google_ai_api_key = config.google_genai_key
print(_google_ai_api_key)

_client = genai.Client(api_key = _google_ai_api_key)
_model = "gemini-2.0-flash-exp"

_tools = [types.Tool(google_search=types.GoogleSearch())]

_ai_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    top_k = 40,
    max_output_tokens = 8192,
    safety_settings = [
        types.SafetySetting(
            category = "HARM_CATEGORY_CIVIC_INTEGRITY",
            threshold = "OFF",
        ),
    ],
    tools = _tools,
    response_mime_type = "application/json")

class AiRequest:
    def __init__(self, func:AiFunction):
        self.__func = func
        self.__call()

    def __call(self):
        request_contents = [
            types.Content(
                role = "user",
                parts = [types.Part.from_text(text = self.__func.stringed())]),]
        
        try:
            resp = _client.models.generate_content(
                model = _model,
                config = _ai_config,
                contents = request_contents
            ).text
        except errors.APIError:
            resp = None
        
        self.__parse_resp(resp)

    def __parse_resp(self, resp:str):
        if resp is None:
            self.request_succesful = False
            self.response = None
        else: 
            self.request_succesful = True
            self.response = json.loads(re.search(r'\{.*\}', resp, re.DOTALL)
                                                    .group(0))

    @property
    def request_succesful(self) -> bool:
        return self.__request_succesful
    @request_succesful.setter
    def request_succesful(self, was_success: bool):
        self.__request_succesful = was_success

    @property
    def response(self) -> dict:
        return self.__response
    @response.setter
    def response(self, resp):
        if self.request_succesful: self.__response = resp