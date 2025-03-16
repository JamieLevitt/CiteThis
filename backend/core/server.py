from flask import current_app
from datetime import datetime, timezone, timedelta
def server_time() -> datetime:
        return datetime.now(timezone.utc)

import time

from .tools import update_trends, update_articles, purge_dead_entries

from structs.core import QueueMethod
from structs.data import TrendStruct

from .config import data_config as config

import inspect

class ServerManager:
    def __init__(self): self.i = 0

    @staticmethod
    def load_topics() -> list[TrendStruct]:
        return TrendStruct.load_all_from_db()
    
    def main_loop(self):
        try:
            print("hi")
            i = 0
            while True:
                print(i)
                i += 1
                self.__process_queue()
                time.sleep(1)
        except KeyboardInterrupt:
            return
        
    def __process_queue(self):
        for method in self.queuemethods: 
            method()

    # @QueueMethod(lambda x: x <= server_time() - timedelta(hours = config.trends_fetch_pause))
    # def _update_trends(self):
    #     print("updating trends")
    #     update_trends()

    @QueueMethod(lambda x: x <= server_time() - timedelta(hours = config.news_fetch_pause))
    def _update_articles(self):
        print("updating articles")
        update_articles()

    @QueueMethod(lambda x: x <= server_time() - timedelta(hours = config.purge_check_pause))
    def _purge_dead_entries(self):
        print("purging")
        purge_dead_entries()

    @property
    def queuemethods(self) -> list: 
        functions = list(reversed(inspect.getmembers(self.__class__,
                                                        predicate = inspect.isfunction)))
        #Returning unreversed leads to methods being called in wrong order
        return [getattr(self, name) for name, func in functions
                    if hasattr(func, "_queue_method_instance")]