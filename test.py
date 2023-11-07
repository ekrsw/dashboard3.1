import datetime as dt
import os

import pandas as pd
from app.models.process_dataframe import ProcessActivity
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings


close_file = os.path.join(settings.FILES_PATH, settings.TODAYS_CLOSE_FILE)  

df = adf.read_reporter(close_file, dt.date.today(), dt.date.today())

print(df)