# coding: utf-8

from read_df import df_from_csv

def is_rain(file_input):
    df_info = df_from_csv(file_input)
    if df_info.weather_int == 4:
        return True
    if df_info.condition_int == 4:
        return True
    return False

def is_obstacle(df_info):
    if df_info.course_type == '障':
        return True
    return False