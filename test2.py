import os
import datetime as dt

from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings

date_obj = dt.date(2023, 10, 19)

from_date = date_obj
to_date = date_obj

date_str = from_date.strftime('%Y%m')
file_name = f'{date_str}_activity.xlsx'

activity_file = os.path.join(settings.ACTIVITY_FILES_PATH, file_name)

df = adf.read_activity(activity_file, from_date, to_date)
df = df.get_kpi()
print(df)

