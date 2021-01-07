# coding: utf-8

## 変数
from setting import *
from read_df import df_from_csv
from . import transaction_parser
from . import race_master_parser
from . import search_from_master
from . import odds_parser
# import transaction_parser
# import race_master_parser
# import search_from_master


## レース結果
    # 不要カラム削除
    # df.dropna(how='all', axis=1, inplace=True)
    # df.drop('ﾀｲﾑ指数', axis=1, inplace=True)


## レース情報
### 整形

def extract_obstacle(df, obstacle_race_id):
    # for transaction
    ## 障害
    # レース結果から障害を抜く
    print(df.shape)
    df_obstacle_transaction = df.loc[df.race_id.isin(obstacle_race_id)]
    print(df_obstacle_transaction.shape)
    df = df.loc[~df.race_id.isin(obstacle_race_id)]
    print(df.shape)
    return df


## 出力
# df.to_csv(FILE_PARSED_transaction, index=False)# for transaction
# df.to_csv(FILE_PARSED_INFO, index=False)
# df_obstacle_transaction.to_csv(FILE_OBSTACLE_transaction, index=False)# for transaction
# df_obstacle.to_csv(FILE_OBSTACLE_INFO, index=False)

mode_dict = {
    'scoring_preparation': 0,
    'scoring': 1,
    'update': 2,
    'renewal': 3
}

trans_out_cols = [
    'race_id',
    'gender',
    'age',
    'weight',
    'weight_change',
    'abs_weight_change',
    'place'
    '着順',
    '枠番',
    '馬番',
    '馬名',
    '性齢',
    '斤量',
    '騎手',
    'タイム',
    '着差',
    '通過',
    '上り',
    '単勝',
    '人気',
    '馬体重',
    '調教師',
    '馬主',
    '賞金(万円)',
]

info_out_cols = [
    'race_id',
    'race_date',
    'race_title',
    'race_class',
    'course_name',
    'course_type',
    'course_direction',
    'course_distance',
    'condition',
    'weather',
    'condition_int',
    'weather_int',
    'race_class_prize'
 ]


def parse_before(filename):
    ## 読み込み
    file_horse = scoring_path / f'horse_in_race_{filename}.csv'
    file_info = scoring_path / f'race_info_before_{filename}.csv'
    file_date = scoring_path / f'race_data_in_week_{filename}.csv'
    df_horse = df_from_csv(file_horse, usecols=['race_id', '馬名', '性齢'])
    df_info = df_from_csv(file_info, usecols=[
        'race_id',
        'race_title',
        'race_class',
        'course_name',
        'course_type',
        'course_direction',
        'course_distance',
    ])
    df_date = df_from_csv(file_date, usecols=['race_id', 'race_date'])
    df_info = df_info.merge(df_date, how='left', on='race_id')
    turf_id = df_info.query('course_type == "芝"').race_id
    df_horse = df_horse.loc[df_horse.race_id.isin(turf_id)]
    df_info = df_info.loc[df_info.race_id.isin(turf_id)]
    if len(df_info) == 0:
        raise Exception('スコアリング対象データがありませんけど？')

    df_info_parsed = race_master_parser.parse_before(df_info)
    df_horse_parsed = transaction_parser.parse_before(df_horse)
    df_horse_out = search_from_master.main(df_horse_parsed)
    # print(df_info_parsed.isnull().sum())
    assert (df_info_parsed.isnull().sum().sum() == 0)

    file_info_parsed = scoring_path / f'race_info_parsed_{filename}.csv'
    file_horse_parsed = scoring_path / f'horse_parsed_{filename}.csv'
    df_info_parsed[[
        'race_id',
        'course_name',
        'course_type',
        'course_direction',
        'course_distance',
        'race_date',
        'race_class_prize'
    ]].to_csv(file_info_parsed, index=False)
    df_horse_out[['race_id', 'gender','age', 'horse_id', '馬名']].to_csv(file_horse_parsed, index=False)


def parse_today(race_id):
    race_id = str(race_id)
    file_info = scoring_path / race_id / 'race_info_before_race.csv'
    file_horse = scoring_path / race_id / 'horse_data_before_race.csv'
    df_info = df_from_csv(file_info, usecols=['race_id', 'weather', 'condition'])
    df_info_parsed = race_master_parser.parse_today(df_info)
    df_horse = df_from_csv(file_horse, usecols=['race_id', '馬名', '馬番', '斤量', '馬体重', '厩舎'])
    df_horse_parsed = transaction_parser.parse_today(df_horse)

    file_info_parsed = scoring_path / race_id / 'race_info_today_parsed.csv'
    file_horse_parsed = scoring_path / race_id / 'horse_today_parsed.csv'
    df_info_parsed.to_csv(file_info_parsed, index=False)
    df_horse_parsed.to_csv(file_horse_parsed, index=False)

    file_srp_odds = scoring_path / race_id / 'sanrenpuku_odds.csv'
    file_srp_odds_parsed = scoring_path / race_id / 'sanrenpuku_odds_parsed.csv'
    odds_parser.parse_sanrenpuku(file_srp_odds, file_srp_odds_parsed)
    
    if df_info_parsed.condition_int.values[0] == 4:
        return False
    elif df_info_parsed.weather_int.values[0] == 4:
        return False
    return True


def add_result(file_info, file_result, update=True, filename=None):
    df_info = df_from_csv(file_info)
    df_result = df_from_csv(file_result)
    obstacle_id = df_info.query('course_type == "障"').race_id
    print('障害数 :', len(obstacle_id))
    df_info = df_info.loc[~df_info.race_id.isin(obstacle_id)]
    print('df_info.shape :', df_info.shape)
    df_info_parsed = race_master_parser.parse_all(df_info)
    print('df_info_parsed.shape :', df_info_parsed.shape)

    df_result = df_result.loc[~df_result.race_id.isin(obstacle_id)]
    print('df_result.shape :', df_result.shape)
    df_result_parsed = transaction_parser.parse_after(df_result)
    print('df_result_parsed.shape :', df_result_parsed.shape)
    df_result_parsed2 = search_from_master.main(df_result_parsed)
    print('df_result_parsed2.shape :', df_result_parsed2.shape)

    if not filename is None:
        # for WH features
        df_info_parsed.to_csv(scoring_path / f'race_info_parsed_{filename}.csv')
        df_result_parsed2.to_csv(scoring_path / f'horse_parsed_{filename}.csv')

    if update:
        # result update
        df_info_parsed = pd.concat([
            df_from_csv(file_race_master),
            df_info_parsed
        ], ignore_index=True
        ).drop_duplicates()

        df_result_parsed2 = pd.concat([
            df_from_csv(file_race_transaction),
            df_result_parsed2
        ], ignore_index=True
        ).drop_duplicates()

    df_info_parsed.to_csv(file_race_master, index=False)
    df_result_parsed2.to_csv(file_race_transaction, index=False)
    print('transactionとmasterを更新しました')
