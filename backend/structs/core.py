from __future__ import annotations
from typing import Callable
import functools

from datetime import datetime, timedelta

from core.server import server_time

class QueueMethod(object):
    def __init__(self, condition: Callable[[datetime], bool], last_call_override:datetime | timedelta = None):
        self.condition = condition
        self.last_call_override = last_call_override
        if not last_call_override: self.__last_call = None
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(instance):
            if self.__ready:
                if not self.__last_call_override:
                    self.last_call = server_time() #Don't collect last call
                return func(instance)
            else:
                return None
        # Attach a reference to this QueueMethod instance
        wrapper._queue_method_instance = self
        return wrapper

    @property
    def __ready(self) -> bool:
        if self.__last_call_override:
            return self.condition(self.__last_call) #ignore last_call

        if self.__last_call is None: return True  # Always ready on the first call
        return self.condition(self.__last_call)

    @property
    def last_call(self) -> datetime:
        return self.__last_call
    @last_call.setter
    def last_call(self, time: datetime):
        self.__last_call = time
    
    @property
    def last_call_override(self) -> datetime:
        return self.__last_call_override
    @last_call_override.setter
    def last_call_override(self, override: datetime):
        self.__last_call_override = override

    @property
    def condition(self) -> Callable[[datetime], bool]:
        return self.__condition
    @condition.setter
    def condition(self, con: Callable[[datetime], bool]):
        self.__condition = con