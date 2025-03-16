import functools, datetime

class QueueMethod(object):
    def __init__(self, interval:int):
        self.__interval = interval #time in hours between calls
        self.__last_called = None
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            self.__last_called = datetime.datetime.now()
            return res
        wrapper._queue_method_instance = self
        return wrapper
    
    @property
    def last_called(self) -> datetime:
        return self.__last_called
    
    @property
    def interval(self) -> int:
        return self.__interval