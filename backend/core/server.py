from datetime import datetime

def server_time() -> datetime:
        return datetime.now()

from .tools import update_trends, update_articles, purge_dead_entries

from structs.core import QueueMethod
from structs.data import TrendStruct

from .config import data_config as config

import threading, time, inspect

class ServerManager:
    def __init__(self): 
        self.i = 0

    @staticmethod
    def load_topics() -> list[TrendStruct]:
        return TrendStruct.load_all_from_db()
        
    def process_queue(self):
        def queue_runner():
            try:
                while True:
                    for method in self.queuemethods:
                        queue_instance = method._queue_method_instance  # Access the decorator instance
                        last_called = queue_instance.last_called
                        interval = queue_instance.interval
                    
                        # Check if the method is ready to be called
                        if last_called is None or (server_time() - last_called).total_seconds() >= interval * 3600:
                            try:
                                method()  # Call the queued method
                            except Exception as e:
                                print(f"Error while processing {method.__name__}: {e}")
                                return  # Stop execution on failure
                    time.sleep(60)  # Wait before checking again
            except (SystemExit, KeyboardInterrupt):
                print("Shutting down process queue gracefully...")
                return
    
        thread = threading.Thread(target=queue_runner, daemon=True)
        thread.start()

    @QueueMethod(config.trends_fetch_pause)
    def _update_trends(self):
        print("updating trends")
        update_trends()

    @QueueMethod(config.news_fetch_pause)
    def _update_articles(self):
        print("updating articles")
        update_articles()

    @QueueMethod(config.purge_check_pause)
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