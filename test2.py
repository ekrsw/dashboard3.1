import os
import datetime as dt

import pandas as pd
from app.models.process_dataframe import ProcessDataframe as pdf
from app.models.excel import ReadExcel
import app.models.dataframe as adf

import settings


activity_file = os.path.join(os.path.join(settings.FILES_PATH, settings.TODAYS_ACTIVITY_FILE))

df = adf.read_activity(activity_file, dt.date(2023, 10, 15), dt.date(2023, 10, 15))
print(df)