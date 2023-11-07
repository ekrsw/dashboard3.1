import os
import datetime as dt

import pandas as pd

from app.models.process_dataframe import ProcessDataframe
import settings


class ReadExcel(object):
    def __init__(self):
        self.process_df = ProcessDataframe()

    def read_close_file(self, close_file, date_obj) -> pd.DataFrame:
        """クローズデータの動的ファイルを読込み、Dataframeで返す
        Args:
            close_file(str): クローズデータのファイル名
            date_obj(dt.date): 日付
        return:
            df(pd.DataFrame): 指定日のクローズデータ"""


        today_str = date_obj.strftime("%Y%m%d")

        df = pd.read_excel(close_file)

        # 最初の3列をスキップし、5列目をインデックスとして設定します
        df = df.iloc[:, 3:].set_index(df.columns[5])
        
        df.reset_index(inplace=True)
        df.set_index(['完了日時'], inplace=True)

        df = df.loc[today_str]
        df.reset_index(inplace=True)
        df.set_index(['所有者'], inplace=True)

        counts = df.index.value_counts()
        df = pd.DataFrame(counts).reset_index()
        df.columns = ['ｵﾍﾟﾚｰﾀ', 'ｸﾛｰｽﾞ']
        df = df.set_index(df.columns[0])

        return df

    def read_shift_file(self, date_obj) -> pd.DataFrame:
        """シフトのCSVファイルからシフトデータを読み込み、名前をインデックスに設定する。
        CSVファイルを読み込む。ヘッダーは3行目にある。
        Args:
            None
        return:
            df(pd.DataFrame): 本日のシフトデータ"""


        shift_file = f"{date_obj.strftime('%Y%m')}_{settings.SHIFT_FILE}"
        date_str = date_obj.strftime("%d")

        shift_file = os.path.join(settings.SHIFT_PATH, shift_file)
        shift_df = pd.read_csv(shift_file, skiprows=2, header=1, index_col=1, quotechar='"', encoding='shift_jis')
        # 最後の1列を削除
        shift_df = shift_df.iloc[:, :-1]
        # "組織名"、"従業員ID"、"種別" の列を削除
        shift_df = shift_df.drop(columns=["組織名", "従業員ID", "種別"])
        shift_df = shift_df[[date_str]]
        shift_df.columns = ['ｼﾌﾄ']
        shift_df = self.process_df.convert_shift_names(shift_df)

        return shift_df
    
    def read_activity_file(self, activity_file, date_obj) -> pd.DataFrame:
        """活動データのの動的ファイルを読込み、date_objと一致する日時のデータをDataframeで返す。
        Args:
            activity_file(str): 活動データのファイル名
            date_obj(dt.date): 日付
        return:
            df(pd.DataFrame): 指定日の活動データ"""


        df = pd.read_excel(activity_file)
        df = df.iloc[:, 3:]

        # '登録日時（関連）（サポート案件）'列を日付型に変換
        df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])

        # date_objと同じ日付の行のみを残す
        df = df[df['登録日時 (関連) (サポート案件)'].dt.date == date_obj]

        return df
    