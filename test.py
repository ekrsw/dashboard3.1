import os
from pprint import pprint
import datetime as dt

from app.models.process_dataframe import ProcessDataframe as pdf
import app.models.dataframe as adf

import settings


date_obj = dt.date.today()

from_date = date_obj
to_date = date_obj

date_str = from_date.strftime('%Y%m')
file_name = f'{date_str}_activity.xlsx'

# activity_file = os.path.join(settings.FILES_PATH, 'todays_activity.xlsm')
activity_file = os.path.join(r'\\mjs.co.jp\datas\CSC共有フォルダ\第47期 東京CSC第二グループ\47期SV共有\ダッシュボードアイテム\files\activity_files\比較用', 'todays_activity_copy.xlsm')

df = adf.read_activity(activity_file, from_date, to_date)

pprint(df.get_kpi())
pprint(df.get_direct_kpi())

df.to_excel('dvlp1.xlsx')
