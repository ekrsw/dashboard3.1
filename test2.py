import os
import datetime as dt

import pandas as pd
from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings

today = dt.date.today()

from_date = today
to_date = today

activity_file = os.path.join(settings.FILES_PATH, settings.TODAYS_ACTIVITY_FILE)

df = adf.read_activity(activity_file, from_date, to_date)
df = df.get_kpi()
print(df)

