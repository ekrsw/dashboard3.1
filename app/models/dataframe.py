import datetime as dt
import os

import pandas as pd

from app.models.reporter import Reporter
from app.models.excel import ReadExcel

import settings


class BaseDataFrame(pd.DataFrame):

    @staticmethod
    def _load_member_list():
         # メンバーリストを読込む。インスタンスが作成されていなくても機能させるため@staticmethodにする。
        file_path = os.path.join(settings.FILES_PATH, settings.MEMBER_LIST)
        try:
            member_list = pd.read_excel(file_path)
            return member_list[['氏名', 'グループ']]
        except Exception as exc:
            print(f"Error loading member list: {exc}")
            raise exc
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update_data(self, new_data):
        for column in new_data.columns:
            self[column] = new_data[column]


class CloseDataFrame(pd.DataFrame):
        
    def __init__(self, template, from_date, to_date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        merged_df = self.merge()

    def __time_to_days(self, time_str) -> float:
        """hh:mm:ss 形式の時間を1日を1としたときの時間に変換する関数
        Args:
            time_str(str): hh:mm:ss 形式の時間
        
        return:
            float: 1日を1としたときの時間"""
        

        t = dt.datetime.strptime(time_str, "%H:%M:%S")

        return (t.hour + t.minute / 60 + t.second / 3600) / 24
        

class ActivityDataFrame(BaseDataFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # メンバーリストを読込み、'氏名'、'グループ'のカラムのみにする。
        df_member_group = self._load_member_list()

        # 活動DataFrameとメンバーリストDataFrameを'所有者'と'氏名'をキーにしてマージ
        merged_df = self.merge(df_member_group, left_on='所有者 (関連) (サポート案件)', right_on='氏名', how='left')
        print("After merge:")
        print(merged_df.head())

        self.update_data(merged_df)
        print(self.head())

        # 案件番号、登録日時でソート
        self.sort_values(by=['案件番号 (関連) (サポート案件)', '登録日時'], inplace=True)

        # 同一案件番号の最初の活動のみ残して他は削除  
        print("Before drop_duplicates:")
        print(self.head())
        self.drop_duplicates(subset='案件番号 (関連) (サポート案件)', keep='first', inplace=True)
        print("After dropping duplicates:")
        print(self.head())

        # サポート案件の登録日時と、活動の登録日時をPandas Datetime型に変換して、差分を'時間差'カラムに格納、NaNは０変換
        self['登録日時 (関連) (サポート案件)'] = pd.to_datetime(self['登録日時 (関連) (サポート案件)'])
        self['時間差'] = (self['登録日時'] - self['登録日時 (関連) (サポート案件)']).abs()
        self.fillna(0, inplace=True)

        self.reset_index(drop=True, inplace=True)

def read_kpi(close_file_name, from_date, to_date) -> CloseDataFrame:
    reporter = Reporter(headless_mode=settings.HEADLESS_MODE)
    df = reporter.get_table_as_dataframe(settings.REPORTER_TEMPLATE, from_date, to_date)
    
    return CloseDataFrame(df)

def read_activity(filename, date_obj, *args, **kwargs) -> ActivityDataFrame:
    df = pd.read_excel(filename, *args, **kwargs)
    df = df.iloc[:, 3:]
    # '登録日時（関連）（サポート案件）'列を日付型に変換
    df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])
    # date_objと同じ日付の行のみを残す
    df = df[df['登録日時 (関連) (サポート案件)'].dt.date == date_obj]
    df.reset_index(drop=True, inplace=True)

    return ActivityDataFrame(df)