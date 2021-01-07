# coding: utf-8

# coding: utf-8

from model_setting import *

def scale_by_race_id(df_main, ss_col, mm_col, keep_cols):
    data_list = []
    for _, v in df_main.groupby('race_id'):
        data_list.append(scale(v, ss_col, mm_col, keep_cols))
    return pd.concat(data_list, axis=0, ignore_index=True)[ss_col+mm_col+keep_cols]


def scale(df, ss_col, mm_col, keep_cols):
    df = df.replace(np.inf, np.nan)
    ss = pd.DataFrame(StandardScaler().fit_transform(df[ss_col]), columns=ss_col)
    mm = pd.DataFrame(MinMaxScaler().fit_transform(df[mm_col]), columns=mm_col)
    tmp_data = pd.concat([
        df[keep_cols].reset_index(drop=True),
        ss.reset_index(drop=True),
        mm.reset_index(drop=True)
    ], axis=1)
    assert tmp_data.race_id.isnull().sum() == 0
    return tmp_data[ss_col+mm_col+keep_cols]
