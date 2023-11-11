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