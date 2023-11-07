import datetime as dt
import numpy as np
import os
import pandas as pd

import settings


def time_to_days(time_str) -> float:
    """hh:mm:ss 形式の時間を1日を1としたときの時間に変換する関数
    Args:
        time_str(str): hh:mm:ss 形式の時間
    
    return:
        float: 1日を1としたときの時間"""
    

    t = dt.datetime.strptime(time_str, "%H:%M:%S")

    return (t.hour + t.minute / 60 + t.second / 3600) / 24

