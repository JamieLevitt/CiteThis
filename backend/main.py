# import multiprocessing
# from core import app, serverManager

# if __name__ == "__main__":
#     queue_check_process = multiprocessing.Process(target = serverManager.main_loop)
#     queue_check_process.start()
#     app.run(debug = True)

import pytrends
from pytrends.request import TrendReq

pytrend = TrendReq(hl='en-US', tz=360)

a = pytrend.realtime_trending_searches(cat=14)
print(a)