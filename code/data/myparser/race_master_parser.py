# coding: utf-8
import pandas as pd
import numpy as np

def separate_obstacle(df):
    # 障害分ける
    df_obstacle = df.loc[df.course_type=='障']
    df = df.loc[df.course_type!='障']
    # print(df_obstacle.shape)
    # df_obstacle.head(2)
    return df, df_obstacle


def format_date(df):
    # 開催日
    try:
        df.race_date = pd.to_datetime(df.race_date, format=('%Y年%m月%d日'))
    except:
        try:
            df.race_date = pd.to_datetime(df.race_date, format=('%Y%m%d'))
        except:
            df.race_date = pd.to_datetime(df.race_date, format=('%Y-%m-%d'))
    return df


def format_course_name(df):
    # 開催地のゆれ
    df.course_name = df.course_name.str.replace('1', '')
    # print(df.course_name.value_counts())
    return df


def format_course_distance(df):
    # 距離おかしいとこ
    df.course_distance = df.course_distance.astype(str).replace({
        ' 外16': '1600',
        ' 外18': '1800',
        '線100': '1000',
        ' 外20': '2000',
        ' 外14': '1400',
        ' 外12': '1200',
        ' 内2周': '3600',
        ' 外24': '2400',
        ' 外30': '3000',
        ' 外22': '2200',
        ' 外32': '3200',
        ' 外26': '2600'
    })
    df.course_distance = df.course_distance.astype(np.int32)
    return df


def converse_to_int(df):
    converse_dict = {
        'condition_int':{
            '良': 1,
            '稍重': 2,
            '重': 3,
            '不良': 4
        },
        'weather_int':{
            '晴': 1,
            '曇': 2,
            '小雨': 3,
            '小雪': 3,
            '雨': 4,
            '雪': 4
        }
    }

    # 馬場状態,天気を数値に変換
    df['condition_int'] = df.condition.copy()
    df['weather_int'] = df.weather.copy()
    df.replace(converse_dict, inplace=True)
    return df


def replace_new_class_prize(race_title, prize):
    if prize == '500万下':
        return '1勝クラス'
    elif prize == '1000万下':
        return '2勝クラス'
    elif prize == '1600万下':
        return '3勝クラス'
    elif prize == 'オープン':
        if 'G1' in race_title:
            return 'G1'
        elif 'G2' in race_title:
            return 'G2'
        elif 'G3' in race_title:
            return 'G3'
    return prize


def format_race_class_prize(df):
    df['race_class_prize'] = df.race_class.str.extract(r'\d+歳[以上]*(.*)', expand=True)

    # 逆！?
    df.race_class_prize = df.race_class_prize.replace({
        '1勝クラス': '500万下',
        '2勝クラス': '1000万下'
    })

    for index in df.index:
        df.loc[index, 'race_class_prize'] = replace_new_class_prize(
            df.loc[index, 'race_title'],
            df.loc[index, 'race_class_prize']
        )
    return df


def parse_before(df):
    df = format_date(df)
    df = format_course_name(df)
    df = format_course_distance(df)
    df = format_race_class_prize(df)
    return df


def parse_today(df):
    df = converse_to_int(df)
    return df


def parse_all(df):
    df = parse_before(df)
    df = converse_to_int(df)
    return df
