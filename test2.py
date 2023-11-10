import os
import datetime as dt

import pandas as pd
from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings


activity_file = os.path.join(os.path.join(settings.FILES_PATH, settings.TODAYS_ACTIVITY_FILE))

df = pd.read_excel(activity_file)
df = df.iloc[:, 3:]
# '登録日時（関連）（サポート案件）'列を日付型に変換
df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])
df.set_index('登録日時 (関連) (サポート案件)', inplace=True)

print(df.head())
