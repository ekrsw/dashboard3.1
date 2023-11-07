import datetime as dt
import os

from app.models.reporter import Reporter
from app.models.process_dataframe import ProcessActivity
from app.models.process_dataframe import ProcessDataframe
from app.models.excel import ReadExcel
import settings


def test_today():
    close_file = os.path.join(settings.FILES_PATH, settings.TODAYS_CLOSE_FILE)
    activity_file = os.path.join(settings.FILES_PATH, settings.TODAYS_ACTIVITY_FILE)
    date_obj = dt.date.today()

    # reporter = Reporter(headless_mode=settings.HEADLESS_MODE)
    process_df = ProcessDataframe()
    exl = ReadExcel()
    
    # df_reporter = reporter.get_table_as_dataframe(settings.REPORTER_TEMPLATE, date_obj, date_obj)
    df_close = exl.read_close_file(close_file, date_obj)
    df_shift = exl.read_shift_file(date_obj)
    df_activity = ProcessActivity.read_excel(r"/Users/ekoresawa/project/dashboard3.1/dvlp_files/202310_activity.xlsx", dt.date(2023, 10, 15))

    # クローズデータとシフトデータ、レポータからスクレイピングしたデータをjoin
    # df_join = df_reporter.join(df_close, how='outer').fillna(0)
    # df_join = df_join.join(df_shift, how='left').fillna("未設定")

    print(df_activity[df_activity['グループ'] == 4])
    # print(my_df[my_df['グループ'] == 2])

    #reporter.close()
