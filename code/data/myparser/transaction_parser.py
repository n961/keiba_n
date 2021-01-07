# coding: utf-8
import pandas as pd
import numpy as np


trans_use_cols_all = [
    'race_id',
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


trans_use_cols_scoring = [
    'race_id',
    '枠番',
    '馬番',
    '馬名',
    # '性齢',
    '斤量',
    # '騎手',
    '単勝',
    # '人気',
    '馬体重',
    # '調教師',
    # '馬主',
    # '賞金(万円)',
]


def get_trans_use_cols(mode_int):
    if mode_int == 1:
        return trans_use_cols_scoring
    return trans_use_cols_all


def extract_arrival(df):
    # for transaction
    # 着順
    df.着順 = df.着順.astype(str)
    df = df.loc[~df.着順.isin({'取', '中', '除', '失'})]
    df.着順 = df.着順.str.replace(r'\(降\)', '').str.replace(r'\(再\)', '')
    df.着順 = df.着順.astype(np.int64)
    return df


def split_age_gender(df):
    # for transaction
    # 性齢
    df['gender'] = df['性齢'].str[0]
    df['age'] = df['性齢'].str[1:].astype(np.int16)
    return df


def extract_weight(df):
    # for transaction
    # 馬体重
    df['weight'] = df.馬体重.str.extract(r'(\d+)\(.*?\d+\)').astype(np.float)
    df['weight_change'] = df.馬体重.str.extract(r'\d+\((.*?\d+)\)').astype(np.float)
    df['abs_weight_change'] = abs(df.weight_change)
    return df


def extract_place(df):
    # for transaction
    # 東とか西とか
    df['place'] = df.調教師.str.extract(r'\[(.+)\].+')
    # print(df.place.value_counts())
    return df

def extract_place_today(df):
    df['place'] = df.厩舎.str[0:2].replace({
        '栗東': '西',
        '美浦': '東',
        '地方': '地'
    })
    return df

def rename_cols(df):
    rename_dict = {
        '斤量':'handy_weight',
        '馬番':'course_num',
        '着順':'arrival',
        '上り':'uphill',
        '賞金(万円)':'got_prize',
        '単勝':'odds',
        'オッズ':'odds'
    }
    use = {k:v for k,v in rename_dict.items() if k in df.columns}
    df.rename(columns=use, inplace=True)
    return df


def parse_before(df):
    df = split_age_gender(df)
    df = rename_cols(df)
    return df


def parse_today(df):
    df = extract_weight(df)
    df = extract_place_today(df)
    df = rename_cols(df)
    return df


def parse_after(df):
    df = extract_arrival(df)
    df = extract_arrival(df)
    df = extract_weight(df)
    df = extract_place(df)
    df = rename_cols(df)
    df = split_age_gender(df)
    return df