import datetime as dt
import numpy as np


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