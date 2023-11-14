import os
from pprint import pprint
import datetime as dt

from app.models.process_dataframe import ProcessDataframe as pdf
import app.models.dataframe as adf

import settings

date_obj = dt.date(2023, 10, 13)

from_date = dt.date(2023, 10, 1)
to_date = dt.date(2023, 10, 31)

date_str = from_date.strftime('%Y%m')
file_name = f'{date_str}_activity.xlsx'

# activity_file = os.path.join(settings.FILES_PATH, 'todays_activity.xlsm')
activity_file = os.path.join(settings.ACTIVITY_FILES_PATH, file_name)

df = adf.read_activity(activity_file, from_date, to_date)
df.to_excel('test.xlsx', index=False)
pprint(df.get_kpi())
pprint(df.get_direct_kpi())
