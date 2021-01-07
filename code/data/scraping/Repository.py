from setting import resource_path
from Scraper import Scraper
import pandas as pd


# 開催日ごとのレース一覧ファイル操作クラス
class RaceInWeekRepository:

    def __init__(self):
        self.scraper = Scraper()

    def create(self, date):
        """
        開催日ごとに、レース一覧を出力する。
        出力パスは'/resource/common/raw_result/race_data_in_week_{日付}.csv'

        Parameters
        ----------
        date : list of str
            レース一覧を取得する開催日のリスト。yyyymmdd形式。
        """
        df_list = []
        for d in date:
            df = self.scraper.get_race_in_day(d)
            df['race_date'] = d
            df_list.append(df)
        df_all = pd.concat(df_list)
        df_all.to_csv(resource_path/ f'scoring/race_data_in_week_{date[0]}.csv', index=False)

    def read(self, date):
        """
        指定された開催日の、レース一覧ファイルをDataFrameで返却する。

        Parameters
        ----------
        date : str
            レース一覧を取得する開催日。yyyymmdd形式。

        Returns
        -------
            race_list : DataFrame
                指定された開催日の、レース一覧

        Raises
        ------
        FileNotFoundError
            該当開催日のレース一覧ファイルが存在しない場合。
        """

        return pd.read_csv(resource_path/f'common/raw_result/race_data_in_week_{date}.csv')


# 出走予定馬及びレース情報ファイル操作クラス
class HorsesInRaceRepository:

    def __init__(self):
        self.scraper = Scraper()
        self.race_in_week_repository = RaceInWeekRepository()
    
    def create(self, date):
        """
        指定された日付リスト毎に、出走予定馬の一覧を出力する。  
        出力パスは'/resource/common/raw_result/race_data_in_week_{最初の日付}.csv'。

        Parameters
        ----------
        date : list of str
            レース一覧を取得する開催日のリスト。yyyymmdd形式。

        Raises
        ------
        FileNotFoundError
            該当開催日のレース一覧ファイルが存在しない場合。
        """

        df_horses = pd.DataFrame()
        df_info = pd.DataFrame()
        for d in date:
            df_race = self.race_in_week_repository.read(d)
            race_ids = df_race['race_id']

            for race_id in race_ids:
                df1, df2 = self.scraper.getHoursesInRace(race_id)

                if len(df_horses) == 0:
                    df_horses = df1
                else:
                    df_horses = pd.concat([df_horses,df1], axis=0)

                if len(df_info) == 0:
                    df_info = df2
                else:
                    df_info = pd.concat([df_info,df2], axis=0)
    
        df_horses.to_csv(resource_path/f'scoring/horse_list_{date[0]}.csv', index=False)
        df_info.to_csv(resource_path/f'scoring/race_info_before_{date[0]}.csv', index=False)


# レース直前情報ファイル操作クラス
class HorseDataBeforeRaceRepository:

    def __init__(self):
        self.scraper = Scraper()
    
    def create(self, race_id):
        """
        指定されたレースIDの出走馬情報を出力する。
        出力パスは'/resource/common/raw_result/horse_data_before_race_{race_id}}.csv'。

        Parameters
        ----------
        race_id : str
            レースID。
        """

        df_horse, df_info = self.scraper.get_horse_data_before_race(race_id)
        df_horse.to_csv(resource_path/f'scoring/{race_id}/horse_data_before_race.csv', index=False)
        df_info.to_csv(resource_path/f'scoring/{race_id}/race_info_before_race.csv', index=False)


# レース結果ファイル操作クラス
class RaceResultAndInfoRepository:

    def __init__(self):
        self.scraper = Scraper()
        self.race_in_week_repository = RaceInWeekRepository()
    
    # 週ごとに、
    def create(self, date):
        """
        指定された日付リスト毎に、開催されたレース結果一覧と、開催されたレース情報一覧を出力する
        出力パスは
            レース結果: '/resource/common/raw_result/race_data_in_week_{最初の日付}.csv'    
            レース情報: '/resource/common/raw_result/race_data_in_week_{最初の日付}.csv'    

        Parameters
        ----------
        date : list of str
            レース情報及び結果を取得する開催日のリスト。yyyymmdd形式。
        """

        df_result = pd.DataFrame()
        df_info = pd.DataFrame()

        for d in date:
            df_race = self.race_in_week_repository.read(d)
            race_ids = df_race['race_id']

            for race_id in race_ids:
                df_result_tmp, df_info_tmp = self.scraper.get_race_result_and_info(race_id)

                if len(df_result) == 0:
                    df_result = df_result_tmp
                else:
                    df_result = pd.concat([df_result,df_result_tmp], axis=0)

                if len(df_info) == 0:
                    df_info = df_info_tmp
                else:
                    df_info = pd.concat([df_info,df_info_tmp], axis=0)
        
        df_result.to_csv(resource_path/f'common/raw_result/race_result_{date[0]}.csv', index=False)
        df_info.to_csv(resource_path/f'common/raw_result/race_info_{date[0]}.csv', index=False)