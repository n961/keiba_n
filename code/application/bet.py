from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
import pandas as pd
import re 
import time
import json
import os


def bet(date, race_id):

    # 買い目ファイルの取得
    json_path = f'../../resource/scoring/{race_id}/scoring.json'

    # 買い目情報の取得
    bet_data = json.load(open(json_path))

    if bet_data['bet'] == 0:
        print("買いません")
        return

    # Chromeのセットアップ
    options = Options()
    options.add_argument('--headless')
    driver_path = open('driver_path.txt', 'r').read()
    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)

    # 購入URL
    url = f"https://race.netkeiba.com/ipat/ipat.html?date={date}&race_id={race_id}"
    
    driver.implicitly_wait(60)

    # ページ取得
    driver.get(url)

    # 単勝を選択
    driver.find_element_by_class_name('shikibetu').find_elements_by_tag_name('dd')[0].click()

    # 馬番を指定
    driver.find_elements_by_class_name('Check01Btn_Off')[int(bet_data['number'])].click()

    # 金額を設定
    driver.find_element_by_name('money').send_keys('1')

    # 追加
    driver.find_element_by_class_name('AddBtn').find_element_by_tag_name('button').click()

    # IPAT投票
    driver.find_element_by_id('ipat_dialog').click()

    # 別タブに移動
    driver.switch_to.window(driver.window_handles[-1])

    # 同意する
    driver.find_element_by_class_name('Agree').click()

    # 加入者番号
    driver.find_elements_by_tag_name('input')[0].send_keys(os.environ['KANYUSHA_BANGO'])

    # 暗証番号
    driver.find_elements_by_tag_name('input')[1].send_keys(os.environ['ANSHO_BANGO'])

    # P-ARS番号
    driver.find_elements_by_tag_name('input')[2].send_keys(os.environ['P_ARS_BANGO'])

    # IPAT入出金メニューに進む
    driver.find_element_by_class_name('SubmitBtn').click()

    # IPAT画面　合計金額の入力
    driver.find_element_by_id('sum').send_keys(driver.find_element_by_class_name('amountDisplay').find_elements_by_tag_name('li')[1].text.replace('円',''))

    # 投票
    driver.find_element_by_class_name('btnGreen').find_element_by_tag_name('a').click()

    # ダイアログ出るまでちょっと待機
    time.sleep(1)

    # ダイアログのOKを選択
    Alert(driver).accept()