import datetime as dt
from app.models import dataframe as adf

from_date = dt.date(2023, 10, 1)
to_date = dt.date(2023, 10, 31)
activity_file = r"/Users/ekoresawa/project/dashboard3.1/dvlp_files/202310_activity.xlsx"

df = adf.read_activity(activity_file, from_date, to_date)
df = df.get_kpi()
print(df)
