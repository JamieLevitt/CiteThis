from google import genai
from google.genai import types, errors

from structs.ai import AiFunction
from core.config import collection_config as config

import json, re

# Retrieve the Google AI API key from configuration
_google_ai_api_key: str = config.google_genai_key

# Initialize the Google AI client
_client = genai.Client(api_key=_google_ai_api_key)

# Define the model to be used
_model: str = "gemini-2.0-flash-exp"

# AI can use Google search
_tools = [types.Tool(google_search=types.GoogleSearch())]

# Set AI generation configuration
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
    response_mime_type = "application/json",
)

class AiRequest:
    """
    Handles AI function requests by calling the Google AI API and parsing the response.
    """
    
    def __init__(self, func: AiFunction):
        """
        Initializes an AI request with a given function and executes it.
        
        :param func: An instance of AiFunction containing the request parameters.
        """
        self.__func: AiFunction = func
        self.__call()
    
    def __call(self) -> None:
        """
        Sends the request to the AI model and processes the response.
        """
        request_contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=self.__func.stringed())],
            )
        ]
        
        try:
            resp: str | None = _client.models.generate_content(
                model=_model,
                config=_ai_config,
                contents=request_contents
            ).text
        except errors.APIError:
            resp = None
        
        self.__parse_resp(resp)

    def __parse_resp(self, resp: str | None) -> None:
        """
        Parses the response from the AI model.
        
        :param resp: The raw response string from the AI model.
        """
        if resp is None:
            self.request_succesful = False
            self.response = None
        else:
            self.request_succesful = True
            self.response = json.loads(re.search(r'\{.*\}', resp, re.DOTALL).group(0))

    @property
    def request_succesful(self) -> bool:
        return self.__request_succesful
    @request_succesful.setter
    def request_succesful(self, was_success: bool) -> None:
        self.__request_succesful = was_success

    @property
    def response(self) -> dict | None:
        return self.__response
    @response.setter
    def response(self, resp: dict | None) -> None:
        if self.request_succesful:
            self.__response = resp