from __future__ import annotations
from typing import Callable

class AiFunction:
    def __init__(self, obj_id:str):
        self.obj_id = obj_id

    prompt : Callable[[AiFunction], str]

    @property
    def obj_id(self) -> str:
        return self.__obj_id
    @obj_id.setter
    def obj_id(self, id:str):
        self.__obj_id = id

    def stringed(self):
        return self.prompt()