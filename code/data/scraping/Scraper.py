# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
import os


class Scraper:

    def __init__(self):
        # Chromeを操作
        options = Options()
        driver_path = open(os.environ['DRIVERPATH'], 'r').read()
        self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)

    # 開催日のレース一覧
    # params
    # date_str : yyyyMMdd (ex. 20201212)
    def get_race_in_day(self, date_str):
        try:
            url = f"https://race.netkeiba.com/top/race_list.html?&kaisai_date={date_str}"

            self.driver.get(url)

            assert self.driver.title[0] != '｜'

            race_data_list = self.driver.find_elements_by_class_name('RaceList_DataItem')
            columns = ['race_id', 'race_time']
            data = []
            for race_data in race_data_list:
                link_str = race_data.find_elements_by_tag_name('a')[0].get_attribute('href')
                if not link_str:
                    continue
                race_id = link_str.replace('&rf=race_list', '') \
                    .replace('https://race.netkeiba.com/race/shutuba.html?race_id=', '')

                # 下記はテスト用。
                # race_id = link_str.replace('&rf=race_list', '')
                # .replace('https://race.netkeiba.com/race/result.html?race_id=', '')

                race_time = race_data.find_element_by_class_name('RaceList_Itemtime').text
                data.append([race_id, race_time])

            return pd.DataFrame(columns=columns, data=data)
        except Exception as e:
            print(e)
            print(f"Error Race Id = {race_id}")
            raise Exception

    # レース直前の出走馬情報を取得する
    # 厩舎が全レースデータと表記が異なるので注意が必要（ex, 当データ：美浦戸田→全レースデータ：[東] 戸田）
    # 　→(美浦=東、栗東=西、地方=地、それ以外は入らないはず。)
    def get_horse_data_before_race(self, race_id):
        try:
            url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"

            self.driver.get(url)

            assert self.driver.title[0] != '｜'

            horse_rows = self.driver.find_elements_by_class_name('HorseList')
            columns = ['race_id', '枠', '馬番', '馬名', '性齢', '斤量', '騎手', '厩舎', '馬体重', 'オッズ', '人気']
            data = []

            for horseRow in horse_rows:
                frame = horseRow.find_elements_by_tag_name('td')[0].text
                number = horseRow.find_elements_by_tag_name('td')[1].text
                name = horseRow.find_element_by_class_name('HorseInfo').text
                sex_age = horseRow.find_element_by_class_name('Barei').text
                jockey = horseRow.find_element_by_class_name('Jockey').text
                aditional_weight = horseRow.find_elements_by_tag_name('td')[5].text
                trainer = horseRow.find_element_by_class_name('Trainer').text
                weight = horseRow.find_element_by_class_name('Weight').text
                odds = horseRow.find_element_by_class_name('Popular').text
                popular = horseRow.find_element_by_class_name('Popular_Ninki').text
                data.append(
                    [race_id, frame, number, name, sex_age, aditional_weight, jockey, trainer, weight, odds, popular])

            df_info = self.parse_race_info_from_shutuba(race_id)
            return pd.DataFrame(columns=columns, data=data), df_info

        except Exception as e:
            print(e)
            print(f"Error Race Id = {race_id}")
            raise Exception

    # 出走予定馬の一覧
    # 該当レース出走予定馬の馬名・性・年齢をCSVにして返す
    def getHoursesInRace(self, race_id):
        try:
            url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
            self.driver.get(url)

            assert self.driver.title[0] != '｜'

            horseRows = self.driver.find_elements_by_class_name('HorseList')

            columns = ['race_id', '馬名', '性齢']
            data = []

            for horseRow in horseRows:
                try:
                    if len(horseRow.find_elements_by_class_name('Cancel_Txt')) != 0:
                        continue

                    name = horseRow.find_element_by_class_name('HorseInfo').text
                    sex_age = horseRow.find_element_by_class_name('Barei').text
                    data.append([race_id, name, sex_age])
                except Exception:
                    print("Error!" + str(race_id))
                    raise Exception

            df_race_info = self.parse_race_info_from_shutuba(race_id)

            return (pd.DataFrame(columns=columns, data=data), df_race_info)
        except Exception as e:
            print(e)
            print(f"Errored Race Id = {race_id}")
            raise Exception

    # 終了したレースの結果を取得するメソッド
    # レース結果のDataFrameと、レース情報のrowを返却する
    def get_race_result_and_info(self, race_id):
        try:
            url = f"https://db.netkeiba.com/race/{race_id}/"
            self.driver.get(url)

            assert self.driver.title[0] != '｜'

            html = self.driver.page_source
            df = pd.read_html(html)
            race_result = df[0]
            race_result['race_id'] = race_id

            df_race_info = self.parse_race_info_from_result(race_id)
            return race_result, df_race_info
        except Exception as e:
            print(e)
            print(f"Error Race Id = {race_id}")
            raise Exception

    def parse_race_info_from_result(self, race_id):
        try:
            header_text = self.driver.find_element_by_class_name('data_intro').text
            header_text = header_text.split('\n')
            race_title = header_text[1]
            # 過去の〜〜　リンクの有無によって変わるので
            race_info_index = 4 if header_text[3][0:2] == '過去' else 3
            course_info = header_text[2].split('/')
            course_type = course_info[0][0]
            course_direction = course_info[0][1]
            course_distance = course_info[0][2:6]
            whether = course_info[1].replace(' ', '').replace('：', ':').replace('天候:', '')
            condition = course_info[2].replace(' ', '').replace('：', ':').replace('芝:', '').replace('ダート:', '')
            race_class = header_text[race_info_index].split(' ')[2]
            race_date = header_text[race_info_index].split(' ')[0]
            course_name = re.search('回(.+)\d+.*', header_text[race_info_index].split(' ')[1])[1]

            info_columns = ['race_id', 'race_date', 'race_title', 'race_class', 'course_name', 'course_type',
                            'course_direction', 'course_distance', 'condition', 'whether']
            race_info_data = [[race_id, race_date, race_title, race_class, course_name, course_type, course_direction,
                               course_distance, condition, whether]]
            return pd.DataFrame(columns=info_columns, data=race_info_data)
        except Exception as e:
            print(e)
            print(f"Error Race Id = {race_id}")
            raise Exception

    def parse_race_info_from_shutuba(self, race_id):
        try:
            race_title = self.driver.find_element_by_class_name('RaceName').text

            race_data1_element = self.driver.find_element_by_class_name('RaceData01')
            race_data1_element_span = race_data1_element.find_elements_by_tag_name('span')
            race_data2_element_span = self.driver.find_element_by_class_name('RaceData02').find_elements_by_tag_name(
                'span')

            race_class = race_data2_element_span[3].text + race_data2_element_span[4].text

            if "オープン" in race_class:
                if len(self.driver.find_elements_by_class_name('Icon_GradeType3')) > 0:
                    race_title = f"{race_title}(G3)"
                if len(self.driver.find_elements_by_class_name('Icon_GradeType2')) > 0:
                    race_title = f"{race_title}(G2)"
                if len(self.driver.find_elements_by_class_name('Icon_GradeType1')) > 0:
                    race_title = f"{race_title}(G1)"

            course_name = race_data2_element_span[1].text
            course_type = race_data1_element_span[0].text[0]
            if "(右" in race_data1_element.text:
                course_direction = "右"
            elif "(左" in race_data1_element.text:
                course_direction = "左"
            elif "(直" in race_data1_element.text:
                course_direction = "直"
            else:
                course_direction = ""
            course_distance = race_data1_element_span[0].text[1:5]

            if "晴" in race_data1_element.text:
                weather = "晴"
            elif "曇" in race_data1_element.text:
                weather = "雲"
            elif "小雨" in race_data1_element.text:
                weather = "小雨"
            elif "雨" in race_data1_element.text:
                weather = "雨"
            elif "大雨" in race_data1_element.text:
                weather = "大雨"
            elif "小雪" in race_data1_element.text:
                weather = "小雪"
            elif "雪" in race_data1_element.text:
                weather = "雪"
            elif "大雪" in race_data1_element.text:
                weather = "大雪"
            else:
                weather = ""

            if len(self.driver.find_elements_by_class_name('Item03')) > 0:
                condition = self.driver.find_element_by_class_name('Item03').text.replace('/ 馬場:', '')
            elif len(self.driver.find_elements_by_class_name('Item04')) > 0:
                condition = self.driver.find_element_by_class_name('Item04').text.replace('/ 馬場:', '')
            else:
                condition = ""

            info_columns = ['race_id', 'race_title', 'race_class', 'course_name', 'course_type', 'course_direction',
                            'course_distance', 'weather', 'condition']
            race_info_data = [
                [race_id, race_title, race_class, course_name, course_type, course_direction, course_distance, weather,
                 condition]]
            return pd.DataFrame(columns=info_columns, data=race_info_data)
        except Exception as e:
            print(e)
            print(f"Errored Race Id = {race_id}")
            raise Exception
