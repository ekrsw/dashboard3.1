import datetime as dt
import logging
import os
import pandas as pd
import string

from app.models import dataframe as mdf
from app.models import process as mp

import settings

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOGLEVEL)
close_file = os.path.join(settings.FILES_PATH, settings.TODAYS_CLOSE_FILE)
activity_file = os.path.join(settings.FILES_PATH, settings.TODAYS_ACTIVITY_FILE)
now = dt.datetime.now()


def df_to_html():

    # 動的ファイルのログを読み込み正常に更新されているかどうかを判定
    last_log_timestamp = read_update_log()
    if is_within_last_five_minutes(last_log_timestamp):
        is_updated = "正常"
        logger.info("動的ファイルは正常に更新されています。")
    else:
        is_updated = "更新されていません"
        logger.error("動的ファイルが更新されていません。")
    
    df_performance = make_df_performance()
    df_kpi_count = make_df_kpi()
    
    # 第2G合計のACW, ATT, CPHを取得する。
    dep_acw = df_performance.loc['合計', 'ACW']
    dep_att = df_performance.loc['合計', 'ATT']
    dep_cph = df_performance.loc['合計', 'CPH']
    
    # KPIの件数のDataFrameから、直受け率、20分以内率のDataFrameを作成する。
    df_kpi_ratio = mp.calc_ratio_20_40(df_kpi_count)

    # 直受け率
    ratio_direct_2g = df_kpi_ratio.loc['第2G', '直受け率']
    ratio_direct_3g = df_kpi_ratio.loc['第3G', '直受け率']
    ratio_direct_n = df_kpi_ratio.loc['長岡', '直受け率']
    ratio_direct_other = df_kpi_ratio.loc['その他', '直受け率']
    ratio_direct_all = df_kpi_ratio.loc['総計', '直受け率']

    # 20分以内率
    ratio_20_2g = df_kpi_ratio.loc['第2G', '20分以内率']
    ratio_20_3g = df_kpi_ratio.loc['第3G', '20分以内率']
    ratio_20_n = df_kpi_ratio.loc['長岡', '20分以内率']
    ratio_20_other = df_kpi_ratio.loc['その他', '20分以内率']
    ratio_20_all = df_kpi_ratio.loc['総計', '20分以内率']

    # 40分以内率
    ratio_40_2g = df_kpi_ratio.loc['第2G', '40分以内率']
    ratio_40_3g = df_kpi_ratio.loc['第3G', '40分以内率']
    ratio_40_n = df_kpi_ratio.loc['長岡', '40分以内率']
    ratio_40_other = df_kpi_ratio.loc['その他', '40分以内率']
    ratio_40_all = df_kpi_ratio.loc['総計', '40分以内率']

    # 直受け件数
    count_direct_2g = df_kpi_count.loc['第2G', '直受け']
    count_direct_3g = df_kpi_count.loc['第3G', '直受け']
    count_direct_n = df_kpi_count.loc['長岡', '直受け']
    count_direct_other = df_kpi_count.loc['その他', '直受け']
    count_direct_all = df_kpi_count.loc['総計', '直受け']

    # 20分以内件数
    count_20_2g = df_kpi_count.loc['第2G', '20分以内']
    count_20_3g = df_kpi_count.loc['第3G', '20分以内']
    count_20_n = df_kpi_count.loc['長岡', '20分以内']
    count_20_other = df_kpi_count.loc['その他', '20分以内']
    count_20_all = df_kpi_count.loc['総計', '20分以内']

    # 40分以内件数
    count_40_2g = df_kpi_count.loc['第2G', '40分以内']
    count_40_3g = df_kpi_count.loc['第3G', '40分以内']
    count_40_n = df_kpi_count.loc['長岡', '40分以内']
    count_40_other = df_kpi_count.loc['その他', '40分以内']
    count_40_all = df_kpi_count.loc['総計', '40分以内']

    # 電話対応数（直受け率の分母）
    count_direct_all_2g = df_kpi_count.loc['第2G', '電話対応数']
    count_direct_all_3g = df_kpi_count.loc['第3G', '電話対応数']
    count_direct_all_n = df_kpi_count.loc['長岡', '電話対応数']
    count_direct_all_other = df_kpi_count.loc['その他', '電話対応数']
    count_direct_all_all = df_kpi_count.loc['総計', '電話対応数']

    # 指標集計対象 + 20分超滞留中（20分以内率の分母）
    count_all_2g_20 = df_kpi_count.loc['第2G', '指標集計対象'] + df_kpi_count.loc['第2G', '20分超滞留中']
    count_all_3g_20 = df_kpi_count.loc['第3G', '指標集計対象'] + df_kpi_count.loc['第3G', '20分超滞留中']
    count_all_n_20 = df_kpi_count.loc['長岡', '指標集計対象'] + df_kpi_count.loc['長岡', '20分超滞留中']
    count_all_other_20 = df_kpi_count.loc['その他', '指標集計対象'] + df_kpi_count.loc['その他', '20分超滞留中']
    count_all_all_20 = df_kpi_count.loc['総計', '指標集計対象'] + df_kpi_count.loc['総計', '20分超滞留中']

    # 指標集計対象 + 40分超滞留中（40分以内率の分母）
    count_all_2g_40 = df_kpi_count.loc['第2G', '指標集計対象'] + df_kpi_count.loc['第2G', '40分超滞留中']
    count_all_3g_40 = df_kpi_count.loc['第3G', '指標集計対象'] + df_kpi_count.loc['第3G', '40分超滞留中']
    count_all_n_40 = df_kpi_count.loc['長岡', '指標集計対象'] + df_kpi_count.loc['長岡', '40分超滞留中']
    count_all_other_40 = df_kpi_count.loc['その他', '指標集計対象'] + df_kpi_count.loc['その他', '40分超滞留中']
    count_all_all_40 = df_kpi_count.loc['総計', '指標集計対象'] + df_kpi_count.loc['総計', '40分超滞留中']

    # モニター用のACW, ATT, CPHを取得する。
    monitor_acw = mp.convert_time_format(dep_acw)
    monitor_att = mp.convert_time_format(dep_att)

    # 個人別パフォーマンスのテーブルを作成、HTMLに変換する。
    df_performance_html = df_performance.copy()
    df_performance_html = df_performance_html.drop('合計')
    df_performance_html['氏名'] = df_performance_html.index
    df_performance_html = df_performance_html[['氏名', 'SV', 'シフト', 'ACW', 'ATT', 'CPH', 'クローズ']]
    html_table = df_performance_html.to_html(index=False, classes="styled-table")
    html_table = html_table.replace(' style="text-align: right;"', '')
    html_table = html_table.replace('dataframe styled-table', 'styled-table')

    # 各種Bufferの計算
    buffer_direct = mp.get_buffer(settings.KPI_DIRECT, count_direct_all, count_direct_all_all)
    buffer_20 = mp.get_buffer(settings.KPI_20, count_20_all, count_all_all_20)
    buffer_40 = mp.get_buffer(settings.KPI_40, count_40_all, count_all_all_40)

    # ダッシュボード用のテンプレート読込み
    formatten_datetime = now.strftime('%Y/%m/%d %H:%M:%S')
    with open(r'templates\templates_dashboard.txt', 'r') as template_file:
        t_dashboard = string.Template(template_file.read())
    
    html_to_dashboard = t_dashboard.substitute(is_updated=is_updated,
                                formatten_datetime=formatten_datetime,
                                dep_acw=dep_acw,
                                dep_att=dep_att,
                                dep_cph=dep_cph,
                                ratio_direct_2g=ratio_direct_2g,
                                ratio_direct_3g=ratio_direct_3g,
                                ratio_direct_n=ratio_direct_n,
                                ratio_direct_other=ratio_direct_other,
                                ratio_direct_all=ratio_direct_all,
                                ratio_20_2g=ratio_20_2g,
                                ratio_20_3g=ratio_20_3g,
                                ratio_20_n=ratio_20_n,
                                ratio_20_other=ratio_20_other,
                                ratio_20_all=ratio_20_all,
                                ratio_40_2g=ratio_40_2g,
                                ratio_40_3g=ratio_40_3g,
                                ratio_40_n=ratio_40_n,
                                ratio_40_other=ratio_40_other,
                                ratio_40_all=ratio_40_all,
                                count_direct_2g=count_direct_2g,
                                count_direct_3g=count_direct_3g,
                                count_direct_n=count_direct_n,
                                count_direct_other=count_direct_other,
                                count_direct_all=count_direct_all,
                                count_20_2g=count_20_2g,
                                count_20_3g=count_20_3g,
                                count_20_n=count_20_n,
                                count_20_other=count_20_other,
                                count_20_all=count_20_all,
                                count_40_2g=count_40_2g,
                                count_40_3g=count_40_3g,
                                count_40_n=count_40_n,
                                count_40_other=count_40_other,
                                count_40_all=count_40_all,
                                count_direct_all_2g=count_direct_all_2g,
                                count_direct_all_3g=count_direct_all_3g,
                                count_direct_all_n=count_direct_all_n,
                                count_direct_all_other=count_direct_all_other,
                                count_direct_all_all=count_direct_all_all,
                                count_all_2g_20=count_all_2g_20,
                                count_all_3g_20=count_all_3g_20,
                                count_all_n_20=count_all_n_20,
                                count_all_other_20=count_all_other_20,
                                count_all_all_20=count_all_all_20,
                                count_all_2g_40=count_all_2g_40,
                                count_all_3g_40=count_all_3g_40,
                                count_all_n_40=count_all_n_40,
                                count_all_other_40=count_all_other_40,
                                count_all_all_40=count_all_all_40,
                                buffer_direct=buffer_direct,
                                buffer_20=buffer_20,
                                buffer_40=buffer_40)
    
    with open(os.path.join(settings.DASHBOARD_PATH, 'dashboard.html'), 'w') as f:
        f.write(html_to_dashboard)
    
    # モニター用テンプレートの読込み
    with open(r'templates\templates_monitor.txt', 'r') as template_file:
        t_monitor = string.Template(template_file.read())
    
    html_to_monitor = t_monitor.substitute(formatten_datetime=formatten_datetime,
                               dep_acw=monitor_acw,
                               dep_att=monitor_att,
                               dep_cph=dep_cph,
                               ratio_direct_all=ratio_direct_all,
                               ratio_20_all=ratio_20_all,
                               ratio_40_all=ratio_40_all)
    
    with open(os.path.join(settings.MONITOR_PATH, 'monitor.html'), 'w') as f_monitor:
        f_monitor.write(html_to_monitor)
    
    # パフォーマンス用テンプレートの読込み
    with open(r'templates\templates_performance.txt', 'r') as template_file:
        t_performance = string.Template(template_file.read())

    html_to_performance = t_performance.substitute(formatten_datetime=formatten_datetime,
                               html_table=html_table)
    
    with open(os.path.join(settings.PERFORMANCE_PATH, 'index.html'), 'w') as f:
        f.write(html_to_performance)

def make_df_performance() -> pd.DataFrame:
    """個人別パフォーマンスのとシフト、業務ステータスのDataFrameを作成する。"""

    rdf = mdf.read_todays_reporter(close_file)
    df_acw_att_cph = rdf.get_kpi(addition=True, sum=True, hms=True)

    # シフトファイルとメンバーリストファイルから、シフトと指標のDataFrameを作成する。
    member_list_file = os.path.join(settings.FILES_PATH, settings.MEMBER_LIST)
    df_member_list = pd.read_excel(member_list_file)
    df_member_list.index = df_member_list['氏名']
    
    df_shift = read_today_shift_file()
    df_shift.index = df_shift.index.map(df_member_list.set_index('Sweet')['氏名'].to_dict())

    df_temp = df_shift.join(df_member_list, how='left').fillna('')
    df_join = df_acw_att_cph.join(df_temp, how='left').fillna('未設定')
    df_join = df_join[['SV', 'シフト', 'ACW', 'ATT', 'CPH', 'クローズ']]
    df_sorted = df_join.sort_values(by=['クローズ', 'シフト'], ascending=[False, True])
    return df_sorted

def make_df_kpi() -> pd.DataFrame:
    """KPIのDataFrameを作成する。"""

    rdf = mdf.read_todays_activity(activity_file)
    df_kpi = rdf.get_kpi()
    df_direct_kpi = rdf.get_direct_kpi()
    pdf = mdf.read_pending_case(activity_file)
    df_pending = pdf.get_over_pending()

    df_join = df_kpi.join(df_direct_kpi, how='left').fillna(0)
    df_join = df_join.join(df_pending, how='left').fillna(0)
    
    return df_join

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

def read_update_log():
    """動的ファイルの更新プログラムのログファイルを読み込む。"""

    with open(settings.UPDATE_LOGFILE, 'r') as f:
        log_entries = f.read()
    
    last_log_entry = log_entries.strip().split('\n')[-1]
    last_log_timestamp = last_log_entry.split(' - ')[0]

    last_log_timestamp
    return last_log_timestamp

from datetime import datetime, timedelta

def is_within_last_five_minutes(timestamp):
    """
    timestampが現在時刻から5分以内かどうかを判定する。

    Args:
    timestamp (str): str型 "YYYY-MM-DD HH:MM:SS,fff"

    Returns:
    bool: timestampが現在時刻から5分以内ならTrue、そうでなければFalse
    """
    
    current_time = now

    timestamp_format = "%Y-%m-%d %H:%M:%S,%f"
    timestamp_datetime = dt.datetime.strptime(timestamp, timestamp_format)

    return timestamp_datetime >= current_time - dt.timedelta(minutes=5)


