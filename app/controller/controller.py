import datetime as dt
import os
import pandas as pd

from app.models import dataframe as mdf
from app.models import process as ps

import settings

close_file = os.path.join(settings.FILES_PATH, settings.TODAYS_CLOSE_FILE)
activity_file = os.path.join(settings.FILES_PATH, settings.TODAYS_ACTIVITY_FILE)

def make_html_performance() -> None:
    """個人別パフォーマンスのとシフト、業務ステータスのDataFrameを作成する。"""

    rdf = mdf.read_todays_reporter(close_file)
    df_acw_att_cph = rdf.get_kpi(addition=True, sum=True, hms=True)

    # シフトファイルとメンバーリストファイルから、シフトと指標のDataFrameを作成する。
    member_list_file = os.path.join(settings.FILES_PATH, settings.MEMBER_LIST)
    df_member_list = pd.read_excel(member_list_file)
    
    df_shift = read_today_shift_file()
    df_shift.index = df_shift.index.map(df_member_list.set_index('Sweet')['氏名'].to_dict())

    df_join = df_acw_att_cph.join(df_shift, how='left').fillna('未設定')
    df_join = df_join[['シフト', 'ACW', 'ATT', 'CPH', 'クローズ']]
    df_sorted = df_join.sort_values(by=['クローズ', 'シフト'], ascending=[False, True])
    print(df_sorted)

def make_html_kpi() -> None:
    """KPIのDataFrameを作成する。"""

    rdf = mdf.read_todays_activity(activity_file)
    df_kpi = rdf.get_kpi()
    pdf = mdf.read_pending_case(activity_file)
    df_pending = pdf.get_over_pending()

    print(df_kpi)
    print(df_pending)

def read_today_shift_file():
    # シフトのCSVファイルからシフトデータを読み込み、名前をインデックスに設定する。

    date_str = dt.date.today().strftime("%d")

    # CSVファイルを読み込む。ヘッダーは3行目（0-indexed）にある。
    shift_df = pd.read_csv(os.path.join(settings.SHIFT_PATH, settings.TODAYS_SHIFT_FILE), skiprows=2, header=1, index_col=1, quotechar='"', encoding='shift_jis')
    # 最後の1列を削除
    shift_df = shift_df.iloc[:, :-1]
    # "組織名"、"従業員ID"、"種別" の列を削除
    shift_df = shift_df.drop(columns=["組織名", "従業員ID", "種別"])
    shift_df = shift_df[[date_str]]
    shift_df.columns = ['シフト']

    return shift_df