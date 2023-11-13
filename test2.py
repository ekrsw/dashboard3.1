import os
import datetime as dt

from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings

date_obj = dt.date(2023, 11, 13)

from_date = date_obj
to_date = date_obj

date_str = from_date.strftime('%Y%m')
file_name = f'{date_str}_activity.xlsx'

activity_file = os.path.join(settings.FILES_PATH, 'todays_activity.xlsm')

df = adf.read_activity(activity_file, from_date, to_date)
df.to_excel('test.xlsx')
print(df.get_kpi())
print(df.get_direct_kpi())
