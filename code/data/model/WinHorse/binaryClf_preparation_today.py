# coding: utf-8

## import
from setting import *
from read_df import df_from_csv


def make_weight_col(df_main):
    ## 加工
    # weight欠損埋める
    df_main['weight_null_flg'] = 0
    df_main.loc[df_main.weight.isnull(), 'weight_null_flg'] = 1
    df_main.weight = df_main.weight.fillna(df_main.last_weight_3_mean)
    df_main['weight_change_rate'] = df_main.weight / df_main.last_weight_3_mean
    df_main['handy_rate'] = df_main.handy_weight / df_main.weight
    df_main['abs_weight_change_rate'] = abs(df_main['weight_change_rate']-1)
    df_main['abs_weight_change_rate_rank'] = df_main.groupby('race_id').abs_weight_change_rate.rank(method='min')
    return df_main


def get_dummie_col(df_main):
    df_main.place = df_main.place.fillna('なし')
    df_main = pd.get_dummies(df_main, columns=['gender', 'place'], drop_first=False)
    df_main = pd.concat([df_main, pd.get_dummies(df_main['race_class_prize'], prefix='race_class_prize')], axis=1)
    dummied_cols = [
        'gender_セ',
        'gender_牝',
        'gender_牡',
        'place_なし',
        'place_地',
        'place_外',
        'place_東',
        'place_西',
        'race_class_prize_1勝クラス',
        'race_class_prize_2勝クラス',
        'race_class_prize_3勝クラス', 
        'race_class_prize_未勝利'
    ]
    for col in dummied_cols:
        if not col in df_main.columns:
            df_main[col] = 0
    return df_main


input_horse_cols = [
    'race_id',
    '馬名',
    # 'horse_id',
    'course_num',
    'weight',
    'handy_weight',
    'place',
    'abs_weight_change',
]


output_cols = [
    'race_id',
    'horse_id',
    'race_date',
    'age',
    # 'gender',
    'first_data_flg',
    'last_weight_3_mean',
    'interval_days',
    'last_turf_flg',
    'distance_diff',
    'last_weather_int',
    'last_condition_int',
    'is_first_in_prize',
    'last_arrival',
    'p2_arrival',
    'p3_arrival',
    'last_speed',
    'last_uphill',
    'last_uphill_speed',
    'last_uphill_samecc',
    'same_cluster_flg',
    'is_same_place',
    'last_got_prize',
    'last_got_prize_sum',
    'course_num',
    'weight',
    'abs_weight_change',
    'weight_null_flg',
    'weight_change_rate',
    'handy_weight',
    'handy_rate',
    'abs_distance_diff',
    'last_got_prize_sum',
    'last_got_prize_sum_rank',
    'abs_weight_change_rate',
    'abs_weight_change_rate_rank',
    'last_uphill_rank',
    'interval_days_diff',
    'interval_days_diff_rank',
    'm_rate',
    'gender_セ',
    'gender_牝',
    'gender_牡',
    'place_なし',
    'place_地',
    'place_外',
    'place_東',
    'place_西',
    'race_class_prize_1勝クラス',
    'race_class_prize_2勝クラス',
    'race_class_prize_3勝クラス',
    'race_class_prize_未勝利',
]

use_class = [
    '未勝利',
    '1勝クラス',
    '2勝クラス',
    '3勝クラス'
]

def only_learn_row(df_main):
    df_main = df_main.query('(weather_int != 4) and (condition_int != 4)')

    # 2012年6月以降のデータはok
    df_main = df_main.loc[df_main.race_date >= pd.Timestamp('2012-06-01')]

    df_main = df_main.query('race_class_prize in @use_class')
    return df_main


def add_m_rate(df_main):
    df_main.race_date = pd.to_datetime(df_main.race_date)
    df_main['race_month'] = df_main.race_date.dt.month.astype(str)
    class_dict = {
        '入門': {'未勝利'},
        '初心者': {'1勝クラス'},
        '見習い':{'2勝クラス', '3勝クラス'},
    #     'プロ':{'オープン','G3','G2','G1'}
    }

    rate_dict = {}
    file_rate_path = str(resource_path/'common/model/WinHorse/gender_rate/{}_rate.csv')
    for k in class_dict.keys():
        rate_dict[k] = pd.read_csv(file_rate_path.format(k), index_col=0)

    df_list = []
    for k,v in class_dict.items():
        df_rate = rate_dict[k]
        for col in df_rate.columns:
            df_use = df_main.loc[(df_main.race_class_prize.isin(v))&(df_main.gender==col)]
            df_use = df_use.merge(df_rate[[col]].rename(columns={col:'m_rate'}), how='left', left_on='race_month', right_index=True)
            df_list.append(df_use)
    return pd.concat(df_list)


def compare_place(df_main):
    ### placeと会場が同じか
    place_dict = {
        '中山': '東',
        '京都': '西', 
        '中京': '西',
        '東京': '東',
        '阪神': '西',
        '福島': '東',
        '新潟': '西',
        '小倉': '西',
        '札幌': '東',
        '函館': '東'
    }
    df_main['_place'] = df_main.course_name.copy().replace(place_dict)
    df_main['is_same_place'] = 0
    df_main.loc[df_main.place==df_main._place, 'is_same_place'] = 1
    return df_main


input_info_cols = [
    'race_id',
    'weather_int',
    'condition_int'
]


def main(race_id=None, filename=None, update=False):
    # 入出力
    if update:
        # filename あり、race_idどちらでもよい、update=False
        # model update, add data
        file_before = common_path/f'model/WinHorse/features/before_{filename}.csv'
        file_info_parsed = scoring_path / f'race_info_parsed_{filename}.csv'
        file_horse_parsed = scoring_path / f'horse_parsed_{filename}.csv'
        file_output = common_path/f'model/WinHorse/features/all_{filename}.csv'
        in_horse_cols = ['arrival'] + input_horse_cols
        out_cols = ['arrival'] + output_cols

    elif filename is not None:
        # filename 必要、race_idなし、update=True
        # renewal
        file_before = resource_path/f'model_build/features/WinHorse_before_{filename}.csv'
        file_info_parsed = file_race_master
        file_horse_parsed = file_race_transaction
        file_output = resource_path/f'model_build/features/WinHorse_all_{filename}.csv'
        in_horse_cols = ['arrival'] + input_horse_cols
        out_cols = ['arrival'] + output_cols

    else:
        # filename なし、race_idあり, update=False
        # scoring
        file_before = scoring_path / race_id / 'horse_features_before.csv'
        file_info_parsed = scoring_path / race_id / 'race_info_today_parsed.csv'
        file_horse_parsed = scoring_path / race_id / 'horse_today_parsed.csv'
        file_output = scoring_path / race_id / 'horse_features_all.csv'
        in_horse_cols = input_horse_cols
        out_cols = output_cols

    df_before = df_from_csv(file_before)
    print('df_before.shape: ', df_before.shape)
    df_horse = df_from_csv(file_horse_parsed, usecols=in_horse_cols)
    df_main = df_before.merge(df_horse, how='left', on=['race_id', '馬名'])
    print('df_main.shape: ', df_main.shape)
    df_info = df_from_csv(file_info_parsed, usecols=input_info_cols)
    df_main = df_main.merge(df_info, how='left', on='race_id')
    df_main.race_date = pd.to_datetime(df_main.race_date)


    df_main = compare_place(df_main)
    df_main = make_weight_col(df_main)
    df_main = add_m_rate(df_main)
    df_main = get_dummie_col(df_main)
    df_main = only_learn_row(df_main)

    df_main[out_cols].to_csv(file_output, index=False)
    # print(out_cols)
    print('全特徴量作成終了')
