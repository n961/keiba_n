from model_setting import *

def balanced_data(df, X_cols, target_col, file_sampling=None):
    # target
    df.reset_index(drop=True, inplace=True)
    df_train, df_test = train_test_split(df)

    # 不均衡データ調整
    target_size = (df_train[target_col]==1).sum()

    df_train_0 = df_train[df_train[target_col]==0]
    df_train_use = df_train_0.sample(target_size, random_state=0)
    df_train_use = pd.concat([df_train_use, df_train[df_train[target_col]==1]])
    df_no_use = df_train.loc[df_train.index.isin(df_train_use.index)]

    get_df_sampling(df_train_use[target_col], df_test[target_col], target_col, file_output=file_sampling)
    s_rate = get_srate(df_test[target_col])
    return s_rate, df_train, df_test, df_no_use

def get_df_sampling(y_train, y_test, target_col, file_output=None):
    tmp = y_train.to_frame()
    tmp['種類'] = 'train'
    tmp2 = y_test.to_frame()
    tmp2['種類'] = 'test'
    tmp3 = pd.concat([tmp, tmp2])
    df_sampling = pd.crosstab(tmp3.種類, tmp3[target_col], margins=True)
    if not file_output is None:
        df_sampling.to_csv(file_output, encoding='utf-8-sig')
    return df_sampling

def get_srate(y_test):
    return y_test.sum() / len(y_test)

def adjusted_prob(prob, s_rate):
    prob2 = prob / (prob + (1 - prob) / s_rate)
    return prob2