import os
import datetime as dt

import pandas as pd
from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings


from_date = dt.date(2023, 10, 15)
to_date = dt.date(2023, 10, 17)

activity_file = os.path.join(os.path.join(settings.FILES_PATH, settings.ACTIVITY_FILE))

df = pd.read_excel(activity_file)
df = df.iloc[:, 3:]
# '登録日時（関連）（サポート案件）'列を日付型に変換
df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])
df.index = df['登録日時 (関連) (サポート案件)']
df.index = df.index.date

# from_dateからto_dateの範囲のデータを抽出
df = df[(df.index >= from_date) & (df.index <= to_date)]
df.reset_index(drop=True, inplace=True)

print(df)
