import os
from pprint import pprint
import datetime as dt

from app.models.process_dataframe import ProcessDataframe as pdf
import app.models.dataframe as adf

import settings


date_obj = dt.date(2023, 12, 1)

from_date = date_obj
to_date = date_obj

date_str = from_date.strftime('%Y%m')
file_name = f'{date_str}_activity.xlsx'

# activity_file = os.path.join(settings.FILES_PATH, 'todays_activity.xlsm')
activity_file = os.path.join(r"\\mjs.co.jp\datas\CSC共有フォルダ\第47期 東京CSC第二グループ\47期SV共有\ダッシュボードアイテム\files", "todays_activity.xlsx")

df = adf.read_activity(activity_file, from_date, to_date)
pending_df = adf.read_pending_case(activity_file)

pprint(df.get_kpi())
print(df.get_direct_kpi())
pprint(pending_df.get_over_pending())

df.to_excel("test_activity.xlsx")
pending_df.to_excel("test_pending.xlsx")