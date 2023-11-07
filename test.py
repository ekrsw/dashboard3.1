import datetime as dt
import os

import pandas as pd
from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings


close_file = os.path.join(settings.FILES_PATH, settings.TODAYS_CLOSE_FILE)  

df = adf.read_reporter(close_file, dt.date.today(), dt.date.today())
# df_2 = adf.read_activity(r"\\mjs.co.jp\datas\CSC共有フォルダ\第47期 東京CSC第二グループ\47期SV共有\ダッシュボードアイテム\files\activity_files\202310_activity.xlsx", dt.date(2023, 10, 15))

df.test()
