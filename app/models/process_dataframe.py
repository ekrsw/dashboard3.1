import datetime as dt
import os
import pandas as pd

import settings

class ProcessDataframe(object):
    def __init__(self):
        member_list = os.path.join(settings.FILES_PATH, settings.MEMBER_LIST)
        self.df_member_list = pd.read_excel(member_list)
    
    def convert_reporter_names(self, df) -> pd.DataFrame:
        """member_list.xlsxから、レポータの名前を正式な氏名のフォーマットに変換
        Args:
            df(pd.DataFrame): レポータからスクレイピングしたDataFrame
        
        return:
            df(pd.DataFrame): 名前を正式な氏名のフォーマットに変換したDataFrame"""
        

        index_dict_reporter = self.df_member_list.set_index('レポータ')['氏名'].to_dict()
        df.index = df.index.map(index_dict_reporter)
        
        return df

    def convert_shift_names(self, df) -> pd.DataFrame:
        """member_list.xlsxファイルから、シフト名前を正式な氏名のフォーマットに変換
        Args:
            df(pd.DataFrame): シフト表をDataFrameで読み込んだもの
        
        return:
            df(pd.DataFrame): 名前を正式な氏名のフォーマットに変換したDataFrame"""


        index_dict_reporter = self.df_member_list.set_index('Sweet')['氏名'].to_dict()
        df.index = df.index.map(index_dict_reporter)
        
        return df

class ProcessActivity(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super(ProcessActivity, self).__init__(*args, **kwargs)
        # メンバーリストを読込み、'氏名'、'グループ'のカラムのみにする。
        member_list = pd.read_excel(os.path.join(settings.FILES_PATH, settings.MEMBER_LIST))
        df_member_group = member_list[['氏名', 'グループ']]
        print("Reading member list:")
        print(df_member_group.head())

        # 活動DataFrameとメンバーリストDataFrameを'所有者'と'氏名'をキーにしてマージ
        merged_df = self.merge(df_member_group, left_on='所有者 (関連) (サポート案件)', right_on='氏名', how='left')
        print("After merge:")
        print(merged_df.head())

        # マージされたデータで元のデータフレームを更新
        self.__dict__.update(merged_df.__dict__)
        print("After updating self:")
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
        self['登録日時 (関連) (サポート案件)'] = pd.to_datetime(self['登録日時 (関連) (サポート案件)'])
        self['時間差'] = (self['登録日時'] - self['登録日時 (関連) (サポート案件)']).abs()
        self.fillna(0, inplace=True)

    @classmethod
    def read_excel(cls, file_name, date_obj, *args, **kwargs):
        df = pd.read_excel(file_name, *args, **kwargs)
        df = df.iloc[:, 3:]

        # '登録日時（関連）（サポート案件）'列を日付型に変換
        df['登録日時 (関連) (サポート案件)'] = pd.to_datetime(df['登録日時 (関連) (サポート案件)'])

        # date_objと同じ日付の行のみを残す
        df = df[df['登録日時 (関連) (サポート案件)'].dt.date == date_obj]
        df.reset_index(drop=True, inplace=True)

        return cls(df)
