import pandas as pd
import types

def df_from_csv(file, usecols=None, encoding=None):
    if not isinstance(file, (types.GeneratorType, list)):
        file = [file]

    df_list = []
    for f in file:
        df_tmp = pd.read_csv(f, usecols=usecols, encoding=encoding)
        df_list.append(df_tmp)
    df = pd.concat(df_list, ignore_index=True)

    return df

# def output_by_race_id(file, outcols=None):
#     if not isinstance(file, (types.GeneratorType, list)):
#         file = [file]