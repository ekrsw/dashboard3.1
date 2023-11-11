import datetime as dt
from app.models import dataframe as adf

from_date = dt.date(2023, 10, 5)
to_date = dt.date(2023, 10, 15)
activity_file = r"/Users/ekoresawa/project/dashboard3.1/dvlp_files/202310_activity.xlsx"

df = adf.read_activity(activity_file, from_date, to_date)
c_20_2g, c_30_2g, c_40_2g, c_60_2g, c_60over, not_included_2g = df.get_count(2)
c_20_3g, c_30_3g, c_40_3g, c_60_3g, c_60over, not_included_3g = df.get_count(3)
c_20_n, c_30_n, c_40_n, c_60_n, c_60over, not_included_n = df.get_count(4)
c_20_other, c_30_other, c_40_other, c_60_other, c_60over, not_included_other = df.get_count(5)

print(c_20_2g, c_30_2g, c_40_2g, c_60_2g, c_60over, not_included_2g)
print(c_20_3g, c_30_3g, c_40_3g, c_60_3g, c_60over, not_included_3g)
print(c_20_n, c_30_n, c_40_n, c_60_n, c_60over, not_included_n)
print(c_20_other, c_30_other, c_40_other, c_60_other, c_60over, not_included_other)