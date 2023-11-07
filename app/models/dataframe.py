import datetime as dt
import numpy as np
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
            member_list = pd.read_excel(file_path).fillna('')
            return member_list[['レポータ', '氏名', 'グループ', '役職']]
        except Exception as exc:
            print(f"Error loading member list: {exc}")
            raise exc
    
    def _convert_reporter_names(self) -> pd.DataFrame:
        """member_list.xlsxから、レポータの名前を正式な氏名のフォーマットに変換
        Args:
            df(pd.DataFrame): レポータからスクレイピングしたDataFrame
        
        return:
            df(pd.DataFrame): 名前を正式な氏名のフォーマットに変換したDataFrame"""

        df_member_list = self._load_member_list()

        index_dict_reporter = df_member_list.set_index('レポータ')['氏名'].to_dict()
        self.index = self.index.map(index_dict_reporter)
        
        return self
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update_self(self, new_data):
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
        df.columns = ['氏名', 'クローズ']
        df = df.set_index(df.columns[0])

        return df
        
    def __init__(self, df, closefile, from_date, to_date, additon, *args, **kwargs):
        super().__init__(df, *args, **kwargs)
        self.from_date = from_date
        self.to_date = to_date
        self.addition = additon
        self._convert_reporter_names()
        self.rename_axis('氏名', inplace=True)
        close_df = self._read_close_file(closefile, from_date, to_date)
        join_df = self.join(close_df, how='outer').fillna(0)
        self.update_self(join_df)
        self.loc['合計'] = self.sum()
        added_df = self._create_acw_att_cph_columns()
        self.update_self(added_df)
    
    def test(self):
        print(self[['ワークタイムの合計', 'クローズ']])

    def _create_acw_att_cph_columns(self):
        '''スクレイピングした指標から、ACW, ATT, CPHを計算してselfにカラムを追加して返す
        0除算を避けるために、0の場合はいったん1にreplaceしている'''

        # columns_to_convert = ['着信通話時間の合計','発信通話時間の合計', 'ワークタイムの合計', '着信後処理時間の合計', '発信後処理時間の合計', '離席時間の合計', '事前準備時間の合計', '一時離席時間の合計', '転送可時間の合計', '着信通話時間の合計(外線)', '発信通話時間の合計(外線)', 'クローズ']

        # 計算に使用するカラムの値をfloatに変換
        # for col in columns_to_convert:
        #    self[col] = self[col].astype(float)
        
        # 実際の計算
        self['ACW'] = (self['ワークタイムの合計'] + self['着信後処理時間の合計'] + self['発信後処理時間の合計'] + self['事前準備時間の合計'] + self['転送可時間の合計'] + self['一時離席時間の合計']) / self['クローズ'].replace(0, 1)
        self.loc[self['クローズ']==0, 'ACW'] = 0
        self['ATT'] = (self['着信通話時間の合計(外線)'] + self['発信通話時間の合計(外線)']) / self['クローズ'].replace(0, 1)
        self.loc[self['クローズ']==0, 'ATT'] = 0
        
        if self.addition:
            _tmp = (self['着信通話時間の合計'] + self['発信通話時間の合計'] + self['ワークタイムの合計'] + self['着信後処理時間の合計'] + self['発信後処理時間の合計'] + self['離席時間の合計'] + self['事前準備時間の合計'] + self['一時離席時間の合計']) * 24
        else:
            _tmp = (self['ログオン時間'] - (self['待機時間'] + self['昼休憩時間の合計'] + self['研修/会議時間の合計'] + self['別作業中時間の合計'] + self['他者支援時間の合計'] + self['開発資料確認時間の合計'] + self['資料作成時間の合計'])) * 24
        self['CPH'] = np.where(
            _tmp == 0,
            0,
            self['クローズ'] / _tmp
        )
        
        self = self.replace(np.inf, 0)

        return self


class ActivityDataFrame(BaseDataFrame):
    def __init__(self, df, *args, **kwargs):
        super().__init__(df, *args, **kwargs)

         # メンバーリストを読込み、'氏名'、'グループ'のカラムのみにする。
        df_member_group = self._load_member_list()

        # 活動DataFrameとメンバーリストDataFrameを'所有者'と'氏名'をキーにしてマージ
        merged_df = self.merge(df_member_group, left_on='所有者 (関連) (サポート案件)', right_on='氏名', how='left')
        print("After merge:")
        print(merged_df.head())

        self.update_self(merged_df)
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
    """指定した範囲のReporterDataFrameを作成する。
    
    Args:
        close_file(str): クローズデータのファイル名
        from_date(date): 集計期間のfrom
        to_date(date): 集計期間のto
    
    return:
        df(ReporterDataFrame): テーブルをReporterDataFrameに変換し、'クローズ'カラムを追加したもの。
    """
    reporter = Reporter(headless_mode=settings.HEADLESS_MODE)
    df = reporter.get_table_as_dataframe(settings.REPORTER_TEMPLATE, from_date, to_date)
    return ReporterDataFrame(df, close_file, from_date, to_date, False)

def read_todays_reporter(close_file) -> ReporterDataFrame:
    """本日のReporterDataFrameを作成する。
    
    Args:
        close_file(str): クローズデータのファイル名
    
    return:
        df(ReporterDataFrame): テーブルをReporterDataFrameに変換し、'クローズ'カラムを追加したもの。
    """
    date_obj = dt.date.today()
    reporter = Reporter(headless_mode=settings.HEADLESS_MODE)
    df = reporter.get_table_as_dataframe(settings.REPORTER_TEMPLATE, date_obj, date_obj)
    return ReporterDataFrame(df, close_file, date_obj, date_obj, True)

def read_activity(filename, date_obj, *args, **kwargs) -> ActivityDataFrame:
    df = pd.read_excel(filename, *args, **kwargs)
    df = df.iloc[:, 3:]
    # '登録日時（関連）（サポート案件）'列を日付型に変換
    df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])
    # date_objと同じ日付の行のみを残す
    df = df[df['登録日時 (関連) (サポート案件)'].dt.date == date_obj]
    df.reset_index(drop=True, inplace=True)
    return ActivityDataFrame(df)
