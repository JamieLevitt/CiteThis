from _pytrends.request import TrendReq

pytrends = TrendReq(hl="en-US", tz=360)

print(pytrends.categories())