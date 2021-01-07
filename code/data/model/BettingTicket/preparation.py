# coding: utf-8

from setting import *
from model_setting import *
from read_df import df_from_csv

horse_use_cols = ['race_id', 'horse_id','馬名', 'odds', 'course_num']

def get_pred(file_wh_score, file_horse_parsed, horse_use_cols):
    ## 読み込み
    df_pred = df_from_csv(
        file_wh_score,
        usecols=['race_id', 'horse_id', 'pred_prob'],
        # encoding='cp932'
    )
    df_horse = df_from_csv(
        file_horse_parsed,
        usecols=horse_use_cols
    )
    return df_pred.merge(df_horse, how='left', on=['race_id', 'horse_id'])


def add_ss(df_pred):
    data_list = []
    for k,v in df_pred.groupby('race_id'):
        ss = pd.DataFrame(StandardScaler().fit_transform(v[['pred_prob']]), columns=['pred_ss'])
        tmp_data = pd.concat([
            v.reset_index(drop=True),
            ss.reset_index(drop=True)
        ], axis=1)
        data_list.append(tmp_data)

    df_pred = pd.concat(data_list)
    return df_pred


def get_rank(df_pred):
    df_pred['pred_rank'] = df_pred.groupby('race_id').pred_prob.rank(ascending=False, method='min')
    df_pred['odds_rank'] = df_pred.groupby('race_id').odds.rank(ascending=True, method='min')
    return df_pred


def get_pivot(df_pred, value_col, colname=None, n=3):
    if colname is None:
        colname = value_col
    pivot = pd.pivot_table(
        df_pred,
        values=value_col,
        index='race_id',
        columns='pred_rank'
    )
    pivot.columns = [f'{colname}{i}' for i in range(1,n+1)]
    return pivot

import itertools

def make_buy(df_pred):
    set_list = list(itertools.combinations(range(1,6), 3))
    df_list = []
    for use_set in set_list:
        df_tmp = df_pred.query('pred_rank in @use_set').rename(columns={
            'pred_prob': 'score',
            'pred_ss': 'score_ss',
            'course_num': 'cn',
            'odds': 'odds'
        })
        num = len(use_set)

        tmp_all = pd.concat([
            get_pivot(df_tmp, col, n=num) for col in ['score', 'score_ss', 'cn', 'odds']
        ], axis=1)
        tmp_all['pat'] = str(use_set[0]) + str(use_set[1]) + str(use_set[2])

        df_tmp.sort_values(['race_id', 'cn'], inplace=True)
        for k,v in df_tmp.groupby('race_id'):
            key = str(k) + v.cn.astype(str).str.zfill(2).sum()
            tmp_all.loc[k, '三連複_key'] = key

        df_list.append(tmp_all)
    return pd.concat(df_list).reset_index()


def merge_odds(df_ac, file_odds_parsed):
    df_sanrenpuku = df_from_csv(file_odds_parsed)
    df_sanrenpuku.三連複_key = df_sanrenpuku.三連複_key.astype(str)
    df_ac = df_ac.merge(
        df_sanrenpuku[['三連複_key', 'オッズ']],
        how='left',
        on='三連複_key'
    ).rename(columns={'オッズ':'三連複_odds'})
    return df_ac


def get_acc_ids(df_pred):
    acc_list = []
    double_list = []
    for k,v in df_pred.query('arrival <= 3').groupby('race_id'):
        if len(v)>3:
            key = str(k) + v.drop_duplicates('arrival', keep='first').sort_values('course_num').course_num.astype(str).str.zfill(2).sum()
            double_list.append(key)
            key = str(k) + v.drop_duplicates('arrival', keep='last').sort_values('course_num').course_num.astype(str).str.zfill(2).sum()
            double_list.append(key)
        else:
            key = str(k) + v.sort_values('course_num').course_num.astype(str).str.zfill(2).sum()
            acc_list.append(key)
    return acc_list + double_list


def get_features(df_ac, df_pred):
    df_ac['ss_mean'] = df_ac[['score_ss1', 'score_ss2', 'score_ss3']].mean(axis=1)
    df_ac['score_sum'] = df_ac[['score1', 'score2', 'score3']].sum(axis=1)

    score_allsum = df_pred.groupby('race_id').pred_prob.sum().to_frame()
    score_allsum.columns = ['score_allsum']

    df_ac = df_ac.merge(score_allsum, how='left', on='race_id')

    df_ac['score_rate'] = df_ac.score_sum / df_ac.score_allsum
    df_ac['score_diff'] = df_ac.score_allsum - df_ac.score_sum
    return df_ac


def get_info_cols(df_ac, file_input_info):
    df_info = df_from_csv(
        file_input_info,
        usecols=['race_id', 'condition_int', 'weather_int', 'race_class_prize','race_date']
    )
    df_info.race_date = pd.to_datetime(df_info.race_date)
    df_ac = df_ac.merge(df_info, how="left", on=['race_id'])
    df_ac['race_date'] = df_ac.race_date.dt.week
    return df_ac


def sanrenpuku_preparation(race_id):
    file_wh_score = scoring_path/race_id/'wh_score.csv'
    file_horse_parsed = scoring_path/race_id/'horse_parsed.csv'
    file_info_parsed = scoring_path/race_id/'info_parsed.csv'
    file_odds_parsed = scoring_path/race_id/'sanrenpuku_odds_parsed.csv'
    file_output = scoring_path/race_id/'bt_features.csv'
    df_pred = get_pred(file_wh_score, file_horse_parsed, horse_use_cols)
    df_pred = add_ss(df_pred)
    df_pred = get_rank(df_pred)
    df_ac = make_buy(df_pred)
    df_ac = merge_odds(df_ac, file_odds_parsed)
    df_ac = get_features(df_ac, df_pred)
    df_ac = get_info_cols(df_ac, file_info_parsed)
    df_ac.to_csv(file_output)


def sanrenpuku_building_data():
    file_wh_score = resource_path /'model_build/logs/wh/202012130029/wh_score_all.csv'
    df_pred = get_pred(file_wh_score, file_race_transaction, ['arrival']+horse_use_cols)
    df_pred = add_ss(df_pred)
    df_pred = get_rank(df_pred)
    df_ac = make_buy(df_pred)
    df_ac = merge_odds(df_ac, file_sanrenpuku_odds)
    df_ac = get_features(df_ac, df_pred)
    df_ac = get_info_cols(df_ac, file_race_master)
    df_ac['三連複'] = 1
    df_ac.loc[df_ac.race_id.isin(get_acc_ids(df_pred)), '三連複'] = 1
    df_ac.to_csv(resource_path /'model_build/logs/wh/202012130029/bt_features.csv', index=False)
