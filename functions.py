from datetime import datetime
from math import floor

def getTimeDiff(t1: datetime, t2: datetime):
    us = (t1 - t2).microseconds();
    ms = us / 100
    s = 
    h = s / 3600
    m = s / 60

    return '{:02}:{:02}:{:02}.{:02}'.format(int(td.))