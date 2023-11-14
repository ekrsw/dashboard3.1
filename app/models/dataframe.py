import datetime as dt
import numpy as np
import os

import pandas as pd

from app.models.reporter import Reporter
from app.models import process as p

import settings


class BaseDataFrame(pd.DataFrame):
    @staticmethod
    def _load_member_list():
         # メンバーリストを読込む。インスタンスが作成されていなくても機能させるため@staticmethodにする。
        file_path = os.path.join(settings.FILES_PATH, settings.MEMBER_LIST)
        try:
            member_list = pd.read_excel(file_path).fillna('')
            member_list = member_list[['レポータ', '氏名', 'グループ', '役職']]
            member_list['グループ'] = member_list['グループ'].astype(int)
            return member_list
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
        
    def __init__(self, df, closefile, from_date, to_date, addition, *args, **kwargs):
        super().__init__(df, *args, **kwargs)
        self.from_date = from_date
        self.to_date = to_date
        self.addition = addition
        self._convert_reporter_names()
        self.rename_axis('氏名', inplace=True)
        close_df = self._read_close_file(closefile, from_date, to_date)
        join_df = self.join(close_df, how='outer').fillna(0)
        self.update_self(join_df)
    
    def get_kpi(self, addition=False, sum=False, hms=False, digits=2):
        if sum:
            self.loc['合計'] = self.sum()
        kpi_df = p.create_acw_att_cph_columns(self, addition)
        if hms:
            kpi_df[['ACW','ATT']] = kpi_df[['ACW','ATT']].applymap(p.float_to_hms)
        kpi_df[['CPH']] = kpi_df[['CPH']].round(digits)
        kpi_df[['クローズ']] = kpi_df[['クローズ']].astype(int)
        return kpi_df[['ACW', 'ATT', 'CPH', 'クローズ']]


class ActivityDataFrame(BaseDataFrame):
    def __init__(self, df, *args, **kwargs):
        super().__init__(df, *args, **kwargs)

        # 受付けタイプ「直受け」「折返し」「留守電」のみ残す
        df = df[(df['受付タイプ (関連) (サポート案件)'] == '直受け') | (df['受付タイプ (関連) (サポート案件)'] == '折返し') | (df['受付タイプ (関連) (サポート案件)'] == '留守電')]

         # メンバーリストを読込み、'氏名'、'グループ'のカラムのみにする。
        df_member_group = self._load_member_list()

        # 活動DataFrameとメンバーリストDataFrameを'所有者'と'氏名'をキーにしてマージ
        merged_df = df.merge(df_member_group, left_on='所有者 (関連) (サポート案件)', right_on='氏名', how='left')
        merged_df['グループ'] = merged_df['グループ'].fillna(0).astype(int)

        # 案件番号、登録日時でソート
        merged_df.sort_values(by=['案件番号 (関連) (サポート案件)', '登録日時'], inplace=True)

        # 同一案件番号の最初の活動のみ残して他は削除  
        merged_df.drop_duplicates(subset='案件番号 (関連) (サポート案件)', keep='first', inplace=True)
        
        # サポート案件の登録日時と、活動の登録日時をPandas Datetime型に変換して、差分を'時間差'カラムに格納、NaNは０変換
        merged_df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(merged_df['登録日時 (関連) (サポート案件)'])
        merged_df['登録日時'] = pd.to_datetime(merged_df['登録日時'])
        merged_df['時間差'] = (merged_df['登録日時'] - merged_df['登録日時 (関連) (サポート案件)']).abs()
        merged_df.reset_index(drop=True, inplace=True)
        self.update_self(merged_df)
    
    def get_kpi(self) -> pd.DataFrame:
        """KPIを計算してDataFrameで返す。
        column: '指標集計対象', '20分以内', '40分以内'
        index: 'グループ'
        
        return:
            df(pd.DataFrame): KPIを計算したDataFrame"""

        df = p.create_kpi_df(self)
        return df
    
    def get_kpi_ts(self):
        pass
    
    def get_direct_kpi(self) -> pd.DataFrame:
        """直受率を計算してDataFrameで返す。
        column: '指標集計対象', '20分以内', '40分以内'
        index: 'グループ'
        
        return:
            df(pd.DataFrame): KPIを計算したDataFrame"""
        
        df = p.create_direct_kpi_df(self)
        return df
    
    def get_direct_kpi_ts(self):
        pass


class PendingDataFrame(BaseDataFrame):
    def __init__(self, df, *args, **kwargs):
        super().__init__(df, *args, **kwargs)

        # 受付けタイプ「直受け」「折返し」「留守電」のみ残す
        df = df[(df['受付タイプ (関連) (サポート案件)'] == '直受け') | (df['受付タイプ (関連) (サポート案件)'] == '折返し') | (df['受付タイプ (関連) (サポート案件)'] == '留守電')]
        
        # 指標に含めないが「いいえ」のもののみ残す
        df = df[df['指標に含めない (関連) (サポート案件)'] == 'いいえ']

        df = df[(df['顛末コード (関連) (サポート案件)'] == '対応中') | (df['顛末コード (関連) (サポート案件)'] == '対応待ち')]

        # 件名に「【受付】」が含まれているもののみ残す。
        contains_df = df[df['件名'].str.contains('【受付】', na=False)]
        uncontains_df = df[~df['件名'].str.contains('【受付】', na=False)]

        only_contains_df = pd.merge(contains_df, uncontains_df, on='案件番号 (関連) (サポート案件)', how='outer', indicator=True)
        result = only_contains_df[only_contains_df['_merge'] == 'left_only']
        s = result['案件番号 (関連) (サポート案件)'].unique()
        df = df[df['案件番号 (関連) (サポート案件)'].isin(s)]

         # メンバーリストを読込み、'氏名'、'グループ'のカラムのみにする。
        df_member_group = self._load_member_list()

        # 活動DataFrameとメンバーリストDataFrameを'所有者'と'氏名'をキーにしてマージ
        merged_df = df.merge(df_member_group, left_on='所有者 (関連) (サポート案件)', right_on='氏名', how='left')
        merged_df['グループ'] = merged_df['グループ'].fillna(0).astype(int)

        # 案件番号、登録日時でソート
        merged_df.sort_values(by=['案件番号 (関連) (サポート案件)', '登録日時'], inplace=True)

        # 同一案件番号の最初の活動のみ残して他は削除  
        merged_df.drop_duplicates(subset='案件番号 (関連) (サポート案件)', keep='first', inplace=True)
        
        # サポート案件の登録日時と、活動の登録日時をPandas Datetime型に変換して、差分を'時間差'カラムに格納、NaNは０変換
        merged_df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(merged_df['登録日時 (関連) (サポート案件)'])
        merged_df['お待たせ時間'] = (dt.datetime(2023, 11, 14, 18, 34) - merged_df['登録日時 (関連) (サポート案件)']).abs()
        merged_df.reset_index(drop=True, inplace=True)
        self.update_self(merged_df)
    
    def get_over_pending(self) -> pd.DataFrame:
        df = p.create_pending_case_df(self)
        return df
    

def read_reporter(close_file, from_date, to_date) -> ReporterDataFrame:
    """指定した範囲のReporterDataFrameを作成する。
    
    Args:
        close_file(str): クローズデータのファイル名
        from_date(date): 集計期間のfrom
        to_date(date): 集計期間のto
    
    return:
        df(ReporterDataFrame): テーブルをReporterDataFrameに変換し、'クローズ'カラムを追加したもの。"""
    
    reporter = Reporter(headless_mode=settings.HEADLESS_MODE)
    df = reporter.get_table_as_dataframe(settings.REPORTER_TEMPLATE, from_date, to_date)
    return ReporterDataFrame(df, close_file, from_date, to_date, False)

def read_todays_reporter(close_file) -> ReporterDataFrame:
    """本日のReporterDataFrameを作成する。
    
    Args:
        close_file(str): クローズデータのファイル名
    
    return:
        df(ReporterDataFrame): テーブルをReporterDataFrameに変換し、'クローズ'カラムを追加したもの。"""
    
    date_obj = dt.date.today()
    rdf = read_reporter(close_file, date_obj, date_obj)
    return rdf

def read_activity(filename, from_date, to_date) -> ActivityDataFrame:
    """'登録日時 (関連) (サポート案件)'が指定した範囲のActivityDataFrameを作成する。
    
    Args:
        filename(str): 活動データのファイル名
        from_date(date): 集計期間のfrom
        to_date(date): 集計期間のto
        
    return:
        df(ActivityDataFrame): テーブルをActivityDataFrameに変換したもの。"""

    df = pd.read_excel(filename)
    df = df.iloc[:, 3:]
    
    # '登録日時（関連）（サポート案件）'列を日付型に変換
    df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])
    df.index = df['登録日時 (関連) (サポート案件)']
    df.index = df.index.date

    # from_dateからto_dateの範囲のデータを抽出
    df = df[(df.index >= from_date) & (df.index <= to_date)]
    df.reset_index(drop=True, inplace=True)
    return ActivityDataFrame(df)

def read_todays_activity(filename) -> ActivityDataFrame:
    """本日のActivityDataFrameを作成する。
    
    Args:
        filename(str): 活動データのファイル名
    
    return:
        df(ActivityDataFrame): テーブルをActivityDataFrameに変換したもの。"""
    
    date_obj = dt.date.today()
    adf = read_activity(filename, date_obj, date_obj)
    return adf

def read_pending_case(filename) -> PendingDataFrame:
    date_obj = dt.date.today()
    df = pd.read_excel(filename)
    df = df.iloc[:, 3:]
    
    # '登録日時（関連）（サポート案件）'列を日付型に変換
    df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])
    df.index = df['登録日時 (関連) (サポート案件)']
    df.index = df.index.date

    # from_dateからto_dateの範囲のデータを抽出
    df = df[(df.index >= date_obj) & (df.index <= date_obj)]
    df.reset_index(drop=True, inplace=True)
    return PendingDataFrame(df)