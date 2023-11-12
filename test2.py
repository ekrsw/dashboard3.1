import os
import datetime as dt

from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings


from_date = dt.date(2021, 10, 1)
to_date = dt.date(2021, 10, 31)

activity_file = os.path.join(r'/Users/ekoresawa/project/dashboard3.1/dvlp_files', '202310_activity.xlsx')

df = adf.read_activity(activity_file, from_date, to_date)
df = df.get_kpi()
print(df)

