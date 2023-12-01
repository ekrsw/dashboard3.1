import datetime as dt
import numpy as np

import pandas as pd


def time_to_days(time_str) -> float:
    """hh:mm:ss 形式の時間を1日を1としたときの時間に変換する関数
    Args:
        time_str(str): hh:mm:ss 形式の時間
    
    return:
        float: 1日を1としたときの時間"""
    

    t = dt.datetime.strptime(time_str, "%H:%M:%S")

    return (t.hour + t.minute / 60 + t.second / 3600) / 24

def float_to_hms(value):
    '''1日を1としたfloat型を'hh:mm:ss'形式の文字列に変換'''
    
    # 1日が1なので、24を掛けて時間単位に変換
    hours = value * 24

    # 時間の整数部分
    h = int(hours)

    # 残りの部分を分単位に変換
    minutes = (hours - h) * 60

    # 分の整数部分
    m = int(minutes)

    # 残りの部分を秒単位に変換
    seconds = (minutes - m) * 60

    # 秒の整数部分
    s = int(seconds)

    return f"{h:02}:{m:02}:{s:02}"

def create_acw_att_cph_columns(df, addition):
    '''スクレイピングした指標から、ACW, ATT, CPHを計算してdfにカラムを追加して返す
    0除算を避けるために、0の場合はいったん1にreplaceしている'''
    
    # 実際の計算
    df['ACW'] = (df['ワークタイムの合計'] + df['着信後処理時間の合計'] + df['発信後処理時間の合計'] + df['事前準備時間の合計'] + df['転送可時間の合計'] + df['一時離席時間の合計']) / df['クローズ'].replace(0, 1)
    df.loc[df['クローズ']==0, 'ACW'] = 0
    df['ATT'] = (df['着信通話時間の合計(外線)'] + df['発信通話時間の合計(外線)']) / df['クローズ'].replace(0, 1)
    df.loc[df['クローズ']==0, 'ATT'] = 0
    
    if addition:
        _tmp = (df['着信通話時間の合計'] + df['発信通話時間の合計'] + df['ワークタイムの合計'] + df['着信後処理時間の合計'] + df['発信後処理時間の合計'] + df['離席時間の合計'] + df['事前準備時間の合計'] + df['一時離席時間の合計']) * 24
    else:
        _tmp = (df['ログオン時間'] - (df['待機時間'] + df['昼休憩時間の合計'] + df['研修/会議時間の合計'] + df['別作業中時間の合計'] + df['他者支援時間の合計'] + df['開発資料確認時間の合計'] + df['資料作成時間の合計'])) * 24
    df['CPH'] = np.where(
        _tmp == 0,
        0,
        df['クローズ'] / _tmp
    )
    
    df = df.replace(np.inf, 0)

    return df

def convert_to_num_of_cases_by_per_time(df):
    """DataFrameを以下のルールで振分けて、件数を返す
        c_20: 20分以内
        c_30: 20分超、30分以内
        c_40: 30分超、40分以内
        c_60: 40分超、60分以内 かつ '指標に含める'
        c_60plus: 60分超 かつ '指標に含める'
        not_included: 指標に含めない(40分超、60分以内 かつ 60分超)

    Args:
        df(pd.DataFrame): DataFrame
        
    return:
        c_20(int): 20分以内の件数
        c_30(int): 20分超、30分以内の件数
        c_40(int): 30分超、40分以内の件数
        c_60(int): 40分超、60分以内 かつ '指標に含める'の件数
        c_60over(int): 60分超 かつ '指標に含める'の件数"""

    c_20 = df[df['時間差'] <= pd.Timedelta(minutes=20)].shape[0]
    c_30 = df[(pd.Timedelta(minutes=20) < df['時間差']) & (df['時間差'] <= pd.Timedelta(minutes=30))].shape[0]
    c_40 = df[(pd.Timedelta(minutes=30) < df['時間差']) & (df['時間差'] <= pd.Timedelta(minutes=40))].shape[0]
    c_60 = df[(pd.Timedelta(minutes=40) < df['時間差']) & (df['時間差'] <= pd.Timedelta(minutes=60)) & (df['指標に含めない (関連) (サポート案件)'] == 'いいえ')].shape[0]
    not_included = df[(pd.Timedelta(minutes=40) < df['時間差']) & (df['時間差'] <= pd.Timedelta(minutes=60)) & (df['指標に含めない (関連) (サポート案件)'] == 'はい')].shape[0]
    c_60over = df[(df['時間差'] > pd.Timedelta(minutes=60)) & (df['指標に含めない (関連) (サポート案件)'] == 'いいえ')].shape[0]
    not_included = not_included + df[(df['時間差'] > pd.Timedelta(minutes=60)) & (df['指標に含めない (関連) (サポート案件)'] == 'はい')].shape[0]
    
    return c_20, c_30, c_40, c_60, c_60over, not_included

def convert_to_pending_num(df):
    c_20over = df[df['お待たせ時間'] >= pd.Timedelta(minutes=20)].shape[0]
    c_40over = df[df['お待たせ時間'] >= pd.Timedelta(minutes=40)].shape[0]

    return c_20over, c_40over

def create_kpi_df(df) -> pd.DataFrame:
    """KPIを計算してDataFrameで返す。
    column: '指標集計対象', '20分以内', '40分以内'
    index: 'グループ'
        
    return:
        df(pd.DataFrame): KPIを計算したDataFrame"""

    df_1g, df_2g, df_3g, df_n, df_other = split_by_group(df)

    c_20_2g, c_30_2g, c_40_2g, c_60_2g, c_60over_2g, not_included_2g = convert_to_num_of_cases_by_per_time(df_2g)
    c_20_3g, c_30_3g, c_40_3g, c_60_3g, c_60over_3g, not_included_3g = convert_to_num_of_cases_by_per_time(df_3g)
    c_20_n, c_30_n, c_40_n, c_60_n, c_60over_n, not_included_n = convert_to_num_of_cases_by_per_time(df_n)
    c_20_other, c_30_other, c_40_other, c_60_other, c_60over_other, not_included_other = convert_to_num_of_cases_by_per_time(df_other)

    # データを作成
    data = {
        '指標集計対象': [df_2g.shape[0] - not_included_2g, df_3g.shape[0] - not_included_3g, df_n.shape[0] - not_included_n, df_other.shape[0] - not_included_other],
        '20分以内': [c_20_2g, c_20_3g, c_20_n, c_20_other],
        '40分以内': [c_20_2g + c_30_2g + c_40_2g, c_20_3g + c_30_3g + c_40_3g, c_20_n + c_30_n + c_40_n, c_20_other + c_30_other + c_40_other]
    }
    # カラム名とインデックスを指定してDataFrameを作成
    kpi_df = pd.DataFrame(data, columns=['指標集計対象', '20分以内', '40分以内'], index=['第2G', '第3G', '長岡', 'その他'])

    # 総計行を追加
    kpi_df.loc['総計'] = kpi_df.sum()
    return kpi_df

def create_direct_kpi_df(df) -> pd.DataFrame:

    df_1g, df_2g, df_3g, df_n, df_other = split_by_group(df)

    # グループごとの直受け数を抽出
    count_direct_ratio_1g = df_1g[df_1g['受付タイプ (関連) (サポート案件)']=='直受け'].shape[0]
    count_direct_ratio_2g = df_2g[df_2g['受付タイプ (関連) (サポート案件)']=='直受け'].shape[0]
    count_direct_ratio_3g = df_3g[df_3g['受付タイプ (関連) (サポート案件)']=='直受け'].shape[0]
    count_direct_ratio_n = df_n[df_n['受付タイプ (関連) (サポート案件)']=='直受け'].shape[0]
    count_direct_ratio_other = df_other[df_other['受付タイプ (関連) (サポート案件)']=='直受け'].shape[0]

    # データを作成
    data = {
        '電話対応数': [df_2g.shape[0], df_3g.shape[0], df_n.shape[0], df_other.shape[0]],
        '直受け': [count_direct_ratio_2g, count_direct_ratio_3g, count_direct_ratio_n, count_direct_ratio_other]
    }

    # カラム名とインデックスを指定してDataFrameを作成
    df = pd.DataFrame(data, columns=['電話対応数', '直受け'], index=['第2G', '第3G', '長岡', 'その他'])

    # 総計行を追加
    df.loc['総計'] = df.sum()

    return df

def create_pending_case_df(df):
    df_1g, df_2g, df_3g, df_n, df_other = split_by_group(df)

    c_20over_2g, c_40over_2g = convert_to_pending_num(df_2g)
    c_20over_3g, c_40over_3g = convert_to_pending_num(df_3g)
    c_20over_n, c_40over_n = convert_to_pending_num(df_n)
    c_20over_other, c_40over_other = convert_to_pending_num(df_other)

     # データを作成
    data = {
        '20分超滞留中': [c_20over_2g, c_20over_3g, c_20over_n, c_20over_other],
        '40分超滞留中': [c_40over_2g, c_40over_3g, c_40over_n, c_40over_other],
    }
    # カラム名とインデックスを指定してDataFrameを作成
    kpi_df = pd.DataFrame(data, columns=['20分超滞留中', '40分超滞留中'], index=['第2G', '第3G', '長岡', 'その他'])

    # 総計行を追加
    kpi_df.loc['総計'] = kpi_df.sum()

    return kpi_df


def split_by_group(df):
    # グループごとのDataFrameに分割
    df_1g = df[df['グループ'] == 1]
    df_2g = df[df['グループ'] == 2]
    df_3g = df[df['グループ'] == 3]
    df_n = df[df['グループ'] == 4]
    df_other = df[df['グループ'] <= 1]

    return df_1g, df_2g, df_3g, df_n, df_other

