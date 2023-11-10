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
df = adf.read_activity(os.path.join(settings.FILES_PATH, settings.ACTIVITY_FILE), dt.date(2023, 10, 15), dt.date(2023, 10, 15))

print(df)
