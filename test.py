import datetime as dt

import pandas as pd
from app.models.process_dataframe import ProcessActivity
import app.models.dataframe as adf

df = adf.read_activity(r"\\mjs.co.jp\datas\CSC共有フォルダ\第47期 東京CSC第二グループ\47期SV共有\ダッシュボードアイテム\files\activity_files\202310_activity.xlsx", dt.date(2023, 10, 16))
print(df[df['グループ'] == 1])
