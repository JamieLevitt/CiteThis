from __future__ import annotations
from typing import Callable

class AiFunction:
    """
    Base class for AI functions, defining the structure for prompts and handling object IDs.
    """
    # Callable attribute returning prompt for AI
    prompt: Callable[[AiFunction], str]
    
    def __init__(self, obj_id: str):
        """
        Initializes the AI function with an object identifier.
        
        :param obj_id: The identifier for the AI function instance.
        """
        self.obj_id = obj_id

    def stringed(self) -> str:
        """
        Generates a string representation of the function's prompt.
        
        :return: The generated prompt string.
        """
        return self.prompt()
    
    @property
    def obj_id(self) -> str:
        """
        Returns the object identifier.
        """
        return self.__obj_id 
    @obj_id.setter
    def obj_id(self, id: str) -> None:
        """
        Sets the object identifier.
        
        :param id: The new object identifier.
        """
        self.__obj_id = id