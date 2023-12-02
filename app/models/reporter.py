import datetime as dt
import glob
import os
import pandas as pd
import shutil
import time

# Webスクレイピング関係ライブラリ
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from app.models import process
import settings


class Reporter(object):
    """Base scraping model.
    
    method:
        get_table_as_dataframe
        get_csv_DL
    """
    def __init__(self, headless_mode=True) -> None:
        self.url = settings.REPORTER_URL
        self.id = settings.REPORTER_ID
        self.headless_mode = headless_mode

        options = Options()

        # ブラウザを表示させない。
        if headless_mode:
            options.add_argument('--headless')
        
        # コマンドプロンプトのログを表示させない。
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # headlessモードでもダウンロードできるようにする設定
        options.add_experimental_option('prefs', {'download.prompt_for_download': False})

        # headlessモードでもダウンロードできるようにする設定
        self.download_path = 'C:\\Users\\{}\\Downloads'.format(os.getlogin())
        self.driver = webdriver.Chrome(options=options)
        self.should_close = True

        self.driver.command_executor._commands["send_command"] = (
            'POST',
            '/session/$sessionId/chromium/send_command'
        )
        self.driver.execute(
            'send_command',
            params={
                'cmd': 'Page.setDownloadBehavior',
                'params': {'behavior': 'allow', 'downloadPath': self.download_path}
            }
        )

        self.driver.implicitly_wait(5)

        self._login()
    
    def close(self) -> None:
        """ドライバーをclose"""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def _login(self) -> None:
        """レポータに接続してログイン"""
        self.driver.get(self.url)
        self.driver.find_element(By.ID, 'logon-operator-id').send_keys(self.id)
        self.driver.find_element(By.ID, 'logon-btn').click()
    
    def _call_template(self, TEMPLATE, from_date, to_date) -> None:
        """テンプレート呼び出し、指定の集計期間を表示"""

        # テンプレート呼び出し
        self.driver.find_element(By.ID, 'template-title-span').click()
        el = self.driver.find_element(By.ID, 'template-download-select')
        s = Select(el)
        s.select_by_value(TEMPLATE)
        self.driver.find_element(By.ID, 'template-creation-btn').click()

        # 集計期間のfromをクリアしてfrom_dateを送信
        self.driver.find_element(By.ID, 'panel-td-input-from-date-0').send_keys(Keys.CONTROL + 'a')
        self.driver.find_element(By.ID, 'panel-td-input-from-date-0').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'panel-td-input-from-date-0').send_keys(from_date.strftime('%Y/%m/%d'))

        # 集計期間のtoをクリアしてto_dateを送信
        self.driver.find_element(By.ID, 'panel-td-input-to-date-0').send_keys(Keys.CONTROL + 'a')
        self.driver.find_element(By.ID, 'panel-td-input-to-date-0').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'panel-td-input-to-date-0').send_keys(to_date.strftime('%Y/%m/%d'))

        # レポート作成
        self.driver.find_element(By.ID, 'panel-td-create-report-0').click()
        time.sleep(5)

    def get_table_as_dataframe(self, TEMPLATE, from_date, to_date) -> pd.DataFrame:
        """テンプレートを表示して、tableを2次元配列で取得
        hh:mm:ss形式の時間を1日を1とした時のfloatに変換

        Args:
            TEMPLATE(str): テンプレート名
            from_date(datetime): 集計期間のfrom
            to_date(datetime): 集計期間のto

        return:
            df(DataFrame): テーブルをDataFrameに変換したもの
        """
        self._call_template(TEMPLATE, from_date, to_date)

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'lxml')

        data_table = []

        # headerのリストを作成
        header_table = soup.find(id='normal-list1-dummy-0-table-head-table')
        xmp = header_table.thead.tr.find_all('xmp')
        header_list = [i.string for i in xmp]
        data_table.append(header_list)

        # bodyのリストを作成
        body_table = soup.find(id='normal-list1-dummy-0-table-body-table')
        tr = body_table.tbody.find_all('tr')
        for td in tr:
            xmp = td.find_all('xmp')
            row = [i.string for i in xmp]
            data_table.append(row)
        
        # テーブルをDataFrameに変換
        df = pd.DataFrame(data_table[1:], columns=data_table[0])
        df.set_index(df.columns[0], inplace=True)
        
        # hh:mm:ss形式の時間を1日を1とした時のfloatに変換
        df = df.applymap(process.time_to_days)

        return df


    def get_csv_DL(self, TEMPLATE, from_date, to_date, save_path, file_name) -> None:
        """テンプレートで表示された内容をダウンロード
        
        Args:
            TEMPLATE(str): テンプレート名
            from_date(datetime): 集計期間のfrom
            to_date(datetime): 集計期間のto
            save_path(str): ダウンロードしたファイルを保存するパス
            file_name(str): ダウンロードしたファイルの名前
        
        return:
            None
        """

        self._call_template(TEMPLATE, from_date, to_date)

        # ダウンロードボタンからCSVをダウンロード  
        now = dt.datetime.now()
        self.driver.find_element(By.ID, 'top-download').click()
        num = int(now.strftime('%Y%m%d%H%M%S'))
        
        time.sleep(1)

        # ダウンロードしたファイルを指定の場所へ移動
        while True:
            download_file_name = '{}-{}.csv'.format(file_name, str(num))
            download_file = os.path.join(self.download_path, download_file_name)
            if glob.glob(download_file):
                # ファイルを移動
                shutil.move(download_file, save_path)

                # ファイル名を変更。既に同一ファイル名があれば削除。
                new_file_name = '{}_{}.csv'.format(to_date.strftime('%Y%m%d') ,file_name)
                new_file_path = os.path.join(save_path, new_file_name)
                old_file_path = os.path.join(save_path, download_file_name)
                if os.path.exists(new_file_path):
                    os.remove(new_file_path)
                os.rename(old_file_path, new_file_path)
                break
            num += 1
    
    def __del__(self) -> None:
        """ドライバーをclose"""
        if self.should_close:
            self.close()
