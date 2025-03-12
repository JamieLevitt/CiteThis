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

# from dataclasses import dataclass, asdict
# from enum import Enum, Flag, auto

# class AIFunction(Enum):
#     TREND_ENTITIES = "get_trend_entities"
#     ENTITY_KEYWORDS = "get_entity_keywords"
#     ENTITY_HANDLE = "get_entity_handle"

#     def __repr__(self): return repr(self.value)

# class AIObjectType(Flag):
#     topic = auto()
#     entity = auto()

# @dataclass
# class AIArg:
#     def stringify(self) -> str: 
#         dicted = asdict(self)
#         for key, val in dicted.items():
#             if type(val) is str: continue

#             if type(val) is list:
#                 for i, obj in enumerate(val):
#                     if isinstance(obj, AIObjectType): val[i] = obj.name
#             else:
#                 if isinstance(val, AIObjectType): val = val.name

#             dicted[key] = val

#         return str(dicted)

# @dataclass
# class AIObject(AIArg):
#     identifier : str
#     datatype : AIObjectType

# @dataclass
# class AIResponseParameter(AIArg):
#     name : str
#     var_type : str
#     description : str
#     instructions : list[str | list[str]]
#     examples : list[str]

# # @dataclass
# # class AIFunction(AIArg):
# #     func_name : str
# #     func_description : str
# #     response_parameters : list[AIResponseParameter]
# #     response_struct : str