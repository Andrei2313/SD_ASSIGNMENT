import os
import math
import time


def compute_ranking(file_path):
    depth = len(os.path.abspath(file_path).split(os.sep)) or 1
    try:
        size = os.path.getsize(file_path)
    except OSError:
        size = 0
    try:
        days_old = (time.time() - os.path.getmtime(file_path)) / 86400
        recency = 1 / (1 + days_old)
    except OSError:
        recency = 0
    return (1.0 / depth) + math.log1p(size) + recency
