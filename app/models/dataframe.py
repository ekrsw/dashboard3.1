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


class ReporterDataFrame(BaseDataFrame):

    @staticmethod
    def _read_close_file(closefile, from_date, to_date) -> pd.DataFrame:
        """クローズデータの動的ファイルを読込み、Dataframeで返す
        Args:
            close_file(str): クローズデータのファイル名
            date_obj(dt.date): 日付
        return:
            df(pd.DataFrame): 指定日のクローズデータ"""


        from_date_str = from_date.strftime("%Y%m%d")
        to_date_str = to_date.strftime("%Y%m%d")

        df = pd.read_excel(closefile)

        # 最初の3列をスキップし、5列目をインデックスとして設定します
        df = df.iloc[:, 3:].set_index(df.columns[5])
        
        df.reset_index(inplace=True)
        df.set_index(['完了日時'], inplace=True)

        # DataFrameのインデックスを日付でソートする
        df.sort_index(inplace=True)

        df = df.loc[from_date_str : to_date_str]
        df.reset_index(inplace=True)
        df.set_index(['所有者'], inplace=True)

        counts = df.index.value_counts()
        df = pd.DataFrame(counts).reset_index()
        df.columns = ['ｵﾍﾟﾚｰﾀ', 'ｸﾛｰｽﾞ']
        df = df.set_index(df.columns[0])

        return df
        
    def __init__(self, df, closefile, from_date, to_date, *args, **kwargs):
        super().__init__(df, *args, **kwargs)
        self.from_date = from_date
        self.to_date = to_date
        
        close_df = self._read_close_file(closefile, from_date, to_date)
        join_df = self.join(close_df, how='outer').fillna(0)

        self.update_data(join_df)

        

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

def read_reporter(close_file, from_date, to_date) -> ReporterDataFrame:
    reporter = Reporter(headless_mode=settings.HEADLESS_MODE)
    df = reporter.get_table_as_dataframe(settings.REPORTER_TEMPLATE, from_date, to_date)
    
    return ReporterDataFrame(df, close_file, from_date, to_date)

def read_activity(filename, date_obj, *args, **kwargs) -> ActivityDataFrame:
    df = pd.read_excel(filename, *args, **kwargs)
    df = df.iloc[:, 3:]
    # '登録日時（関連）（サポート案件）'列を日付型に変換
    df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])
    # date_objと同じ日付の行のみを残す
    df = df[df['登録日時 (関連) (サポート案件)'].dt.date == date_obj]
    df.reset_index(drop=True, inplace=True)

    return ActivityDataFrame(df)