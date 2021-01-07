# coding: utf-8

from setting import *
from read_df import df_from_csv
# from . import transaction_parser
# from . import race_master_parser

judge_cols = [
    '馬名',
    # 'gender',
    'born_year'
]
output_cols = ['race_id', 'horse_id', '馬名']
gender_dict = {'セ':'牡'}


# 加工
def processed_data(df_horse):
    # race_idの年部分から、馬の生まれ年を付与する
    df_horse['born_year'] = df_horse['race_id'].astype(str).str[0:4].astype(np.int64) - df_horse['age'].astype(np.float64)
    return df_horse.drop_duplicates(subset=judge_cols)[['馬名', 'born_year']]


# マスタ作成
def make_master(df_horse):

    df_horse = df_horse[judge_cols]
    df_horse_dupl = df_horse.loc[
        df_horse.duplicated('馬名', keep=False)
    ].sort_values(['馬名', 'born_year'])

    df_horse = df_horse.loc[~df_horse.馬名.isin(df_horse_dupl.馬名)]

    print('重複数: ', df_horse_dupl.shape[0])
    if len(df_horse_dupl) > 0:
        check_master(df_horse_dupl)

    df_horse_master = pd.concat(
        [df_horse, df_horse_dupl],
        ignore_index=True
    )

    print('マスター件数: ', df_horse_master.shape[0])

    df_horse_master.reset_index(drop=True, inplace=True)
    df_horse_master['horse_id'] = df_horse_master.index + 1
    return df_horse_master[['horse_id', '馬名', 'born_year']]


# 同名の馬が、同じ馬か否か判別
def check_master(df_horse_dupl):
    df_horse_dupl['born_year_diff'] = df_horse_dupl.groupby('馬名').born_year.diff()
    try:
        assert df_horse_dupl.born_year_diff.min() > 3, '同名の馬の年齢が近すぎません？'
    except AssertionError as e:
        print(e)
        print(df_horse_dupl)
    df_horse_dupl.drop('born_year_diff', axis=1, inplace=True)


# マスタ更新
def update_master(df_horse_merged):
    df_horse_master = df_from_csv(file_horse_master)

    df_horse_tmp = df_horse_merged[judge_cols].merge(
        df_horse_master,
        how='left',
        on=judge_cols
    )

    df_horse_new = df_horse_tmp.loc[df_horse_tmp.horse_id.isnull()]
    print('新しい子の数: ', df_horse_new.shape[0])
    df_horse_new.reset_index(drop=True, inplace=True)
    df_horse_new['horse_id'] = df_horse_master.horse_id.max() + df_horse_new.index + 1
    df_horse_master = pd.concat([df_horse_master, df_horse_new[df_horse_master.columns]], ignore_index=True)
    check_master(df_horse_master)
    print('馬マスター件数: ', df_horse_master.shape)
    assert df_horse_master.shape[0] == df_horse_master.horse_id.nunique(), 'horse_idが間違っている'
    return df_horse_master[['horse_id', '馬名', 'born_year']]


def main(df_horse):
    # 馬の生まれ年を付与
    df_horse_use = processed_data(df_horse)

    print('馬名数: ', df_horse.馬名.nunique())

    if not os.path.exists(file_horse_master):
        print('馬マスター新規作成')
        df_horse_master = make_master(df_horse_use)
    else:
        print('馬マスターアップデート')
        df_horse_master = update_master(df_horse_use)

    df_horse_out = df_horse.merge(
        df_horse_master,
        how='left',
        on=judge_cols
    )
    assert df_horse_out.shape[0] == df_horse.shape[0], '結合ミス'

    # ----テストのためコメントアウト----
    # df_horse_out[output_cols].to_csv(output_path, index=False)
    df_horse_master.to_csv(file_horse_master, index=False)
    # ----テストのためコメントアウト----

    return df_horse_out
