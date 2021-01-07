# coding: utf-8

## import
from setting import *
from read_df import df_from_csv

hue_col = 'horse_id'
horse_usecols = ['race_id', 'horse_id', 'gender', 'age', '馬名']

race_usecols = [
    'race_id',
    'race_date',
    'race_class_prize',
    'course_type',
    'course_distance',
    'course_name',
    # 'place',
]

output_cols = [
    'race_id',
    'horse_id',
    '馬名',
    'race_date',
    'age',
    'gender',
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
    # 'is_same_place',
    'last_got_prize',
    'last_got_prize_sum',
    'course_name',
    'race_class_prize',
    'abs_distance_diff',
    'last_got_prize_sum',
    'last_got_prize_sum_rank',
    'last_uphill_rank',
    'interval_days_diff',
    'interval_days_diff_rank'
]



def extract_data(df_main, df_info, filename):
    file_info_parsed = scoring_path / f'race_info_parsed_{filename}.csv'
    file_horse_parsed = scoring_path / f'horse_parsed_{filename}.csv'

    df_horse = df_from_csv(file_horse_parsed)
    print('df_horse.shape: ', df_horse.shape)
    TARGET_ID = set(df_horse.race_id.unique())
    print('対象レース数: ', len(TARGET_ID))
    
    df_main = df_main.loc[df_main[hue_col].isin(df_main[hue_col])]
    df_main = pd.concat([df_main, df_horse], ignore_index=True)
    print('transaction追加済数', df_main.duplicated(subset=horse_usecols).sum())
    df_main = df_main.drop_duplicates(subset=['race_id', 'horse_id'])
    df_now_info = df_from_csv(file_info_parsed)
    df_info = pd.concat([df_now_info, df_info], ignore_index=True)
    df_info = df_info.drop_duplicates(subset=['race_id'])
    return df_main, df_info, TARGET_ID


def parse_data(df_main):
    df_main.race_date = pd.to_datetime(df_main.race_date)
    return df_main


def add_first_flg(df_main):
    # データ中初登場フラグ
    df_main.sort_values('race_date', inplace=True)
    df_main.reset_index(drop=True, inplace=True)
    df_main['first_data_flg'] = 0
    df_main.loc[df_main.groupby(hue_col).head(1).index, 'first_data_flg'] = 1
    return df_main


### 3項間移動平均
def add_n_mean(df_main, col, role_num=3):
    mean_col = f'{col}_{role_num}_mean'
    last_mean_col = f'last_{mean_col}'
    df_main.sort_values('race_date', inplace=True)

    v_list = []
    for k,v in df_main.groupby(hue_col):
        v[mean_col] = v[col].rolling(window=role_num).mean()
        v[last_mean_col] = v[mean_col].shift(1)
        v_list.append(v)

    df_main = pd.concat(v_list, ignore_index=True)
    return df_main


def add_sum(df_main, col):
    sum_col = f'{col}_sum'
    last_sum_col = f'last_{sum_col}'
    df_main.sort_values('race_date', inplace=True)

    v_list = []
    for k,v in df_main.groupby(hue_col):
        v[sum_col] = v[col].fillna(0).cumsum()
        v[last_sum_col] = v[sum_col].shift(1)
        v_list.append(v)

    df_main = pd.concat(v_list, ignore_index=True)
    return df_main


def add_last_value(df_main, col_list, n=1):
    df_main.sort_values('race_date', inplace=True)
    if n == 1:
        m = ''
    else:
        m = '_' + str(n)

    for col in col_list:
        new_col = f'last{m}_{col}'
        df_main[new_col] = df_main.groupby(hue_col)[col].shift(n)
    return df_main


### 前回の情報（中央競馬のみ）
def add_last_race_info(df_main):
    df_main = add_last_value(df_main, ['race_date', 'course_type', 'got_prize'], n=1)
    df_main['last_turf_flg'] = 0
    df_main.loc[df_main.last_course_type=='芝', 'last_turf_flg'] = 1

    #### 前回のレースからの日数
    df_main['interval_days'] = (df_main.race_date - df_main.last_race_date).dt.days
    df_main['interval_days_diff'] = abs(df_main.interval_days - 20)
    df_main['interval_days_diff_rank'] = df_main.groupby('race_id').interval_days_diff.rank(method='max')

    #### 前回と今回の距離の差
    df_main['distance_diff'] = df_main.groupby(hue_col).course_distance.diff()
    df_main['abs_distance_diff'] = abs(df_main['distance_diff'])
    return df_main


#### ※以下、芝のみ

# 前回の芝の天気とコンディション
def add_last_turf_info(df_main):
    df_main = add_last_value(df_main, ['weather_int', 'condition_int', 'race_class_prize'], n=1)
    # 前回とクラスが異なるか否か
    df_main['is_first_in_prize'] = 0
    df_main.loc[(df_main.race_class_prize != df_main.last_race_class_prize), 'is_first_in_prize'] = 1

    # prize
    df_main = add_sum(df_main, 'got_prize')
    df_main['last_got_prize_sum'] = df_main['last_got_prize_sum'].fillna(0)
    df_main['last_got_prize_sum_rank'] = df_main.groupby('race_id').last_got_prize_sum.rank(ascending=False, method='min')
    return df_main


# 前回のレースの着順
def add_last_arrival(df_main):
    df_main = add_last_value(df_main, ['arrival'], n=1)
    # 同じクラスの芝での、2回前と3回前の着順
    df_main.sort_values('race_date', inplace=True)
    df_main['p2_arrival'] = df_main.groupby([hue_col, 'race_class_prize']).arrival.shift(2)
    df_main['p3_arrival'] = df_main.groupby([hue_col, 'race_class_prize']).arrival.shift(3)
    return df_main


def add_last_speed(df_main):
    ## 前回のスピード
    # 今回のスピード、上り
    base_time = pd.to_datetime('00:00.0', format='%M:%S.%f')
    df_main.タイム = (pd.to_datetime(df_main.タイム, format=('%M:%S.%f')) - base_time).dt.microseconds
    df_main['speed'] = df_main['タイム'] / df_main.course_distance

    df_main['uphill_speed'] = df_main.uphill / df_main.speed
    
    # 前回のスピード、上り
    df_main = add_last_value(df_main, ['speed', 'uphill', 'uphill_speed'], n=1)
    df_main['last_uphill_rank'] = df_main.groupby('race_id').last_uphill.rank(method='min')
    # df_main['last_speed'] = df_main['last_speed'].dt.microseconds
    # df_main['last_uphill_speed'] = df_main['last_uphill_speed'].dt.microseconds
    return df_main


def add_cluster_info(df_main):
    ## コースごと
    df_cc = pd.read_csv(file_course_cluster)
    # print(df_cc.shape)

    df_cc.rename(columns={'cluster': 'course_cluster'}, inplace=True)
    tmp = df_cc['競馬場'].str.split('_', expand=True)
    tmp.columns = ['course_name', 'v']
    df_cc = pd.concat([df_cc, tmp], axis=1)

    df_cc2 = df_cc[['course_cluster', 'course_name', 'v']].drop_duplicates(['course_cluster', 'course_name']).sort_values('course_cluster')
    df_cc2['v'] = df_cc2.v.replace({'内回り':None})
    df_cc2.drop(12, inplace=True)

    df_main2 = df_main.merge(df_cc2[['course_cluster', 'course_name']], how='left', on='course_name')
    df_main2.loc[(df_main2.course_name=='新潟')&(df_main2.course_direction=='直'), 'course_cluster'] = 5

    # - コースクラスタ
    df_main2 = add_last_value(df_main2, ['course_cluster'], n=1)
    df_main2['last_uphill_samecc'] = df_main2.groupby([hue_col, 'course_cluster']).uphill.shift(1)

    df_main2['same_cluster_flg'] = 0
    df_main2.loc[(df_main2.course_cluster == df_main2.last_course_cluster), 'same_cluster_flg'] = 1
    return df_main2


def get_features(df_main):
    df_main = add_first_flg(df_main)
    df_main = parse_data(df_main)
    df_main = add_n_mean(df_main, 'weight', role_num=3)
    df_main = add_last_race_info(df_main)

    # ダート削除
    df_main = df_main.query('course_type=="芝"')
    
    df_main = add_last_turf_info(df_main)
    df_main = add_last_arrival(df_main)
    df_main = add_last_speed(df_main)
    df_main = add_cluster_info(df_main)
    return df_main


def main(filename=None, update=False):
    df_main = df_from_csv(file_race_transaction)
    df_info = df_from_csv(file_race_master)
    print('df_transaction.shape: ', df_main.shape)
    print('df_race_master.shape: ', df_info.shape)

    if filename == 'new':
        # renewal
        TARGET_ID = set(df_main.race_id.unique())
        print('対象レース数: ', len(TARGET_ID))
    else:
        # update
        # scoring
        df_main, df_info, TARGET_ID = extract_data(df_main, df_info, filename)

    df_main = df_main.merge(df_info, how='left', on='race_id')
    df_main = get_features(df_main)

    if update:
        # model update
        file_output = common_path/f'model/WinHorse/features/before_{filename}.csv'
        df_main.query('race_id in @TARGET_ID')[output_cols].to_csv(file_output, index=False)

    elif filename == 'new':
        # model renewal
        file_output = resource_path/f'model_build/features/WinHorse_before_{filename}.csv'
        # file_output = resource_path/f'model_build/features/WinHorse_before_new.csv'
        df_main[output_cols].to_csv(file_output, index=False)
        print("出力データ数: ", df_main.shape)

    else:
        # scoring
        for race_id in TARGET_ID:
            os.makedirs(scoring_path/str(race_id), exist_ok=True)
            file_output = str(scoring_path / '{}/horse_features_before.csv')
            df_main.query('race_id == @race_id')[output_cols].to_csv(file_output.format(race_id), index=False)
    
    print('前日分特徴量出力完了')
