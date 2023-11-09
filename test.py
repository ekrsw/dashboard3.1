import datetime as dt
import os

import pandas as pd
from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings


close_file = os.path.join(settings.FILES_PATH, settings.TODAYS_CLOSE_FILE) 
activity_file = os.path.join(os.path.join(settings.FILES_PATH, settings.ACTIVITY_FILE))
# df = adf.read_reporter(close_file, dt.date.today(), dt.date.today())
# df = adf.read_activity(os.path.join(settings.FILES_PATH, settings.ACTIVITY_FILE), dt.date(2023, 10, 15), dt.date(2023, 10, 15))

# from_dateとto_dateをpandasのTimestampに変換
from_date = pd.Timestamp(dt.date(2023, 10, 15))
to_date = pd.Timestamp(dt.date(2023, 10, 15))

df = pd.read_excel(close_file)
df = df.iloc[:, 3:]
# '登録日時（関連）（サポート案件）'列を日付型に変換
df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])

df.sort_values(by='案件番号 (関連) (サポート案件)', inplace=True)
# from_dateからto_dateの範囲のデータを抽出
df = df[(df['登録日時 (関連) (サポート案件)'] >= from_date) & (df['登録日時 (関連) (サポート案件)'] <= to_date)]
df.reset_index(drop=True, inplace=True)


print(activity_file)
