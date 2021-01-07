# coding: utf-8


from setting import *
from model_setting import *
from read_df import df_from_csv
from . import scale_feature
from model import balance_target

output_cols = [
    'race_id',
    'horse_id',
    # '単勝',
    'pred_prob'
]

def main(file_input, file_output):
    ## 読み込み
    df_main = df_from_csv(file_input)
    wh_config = json.load(open(file_winhorse_config, 'r'))

    ss_col = wh_config['ss_col']
    mm_col = wh_config['mm_col']
    not_z_col = wh_config['not_z_col']
    keep_cols = [col for col in df_main.columns if not col in set(ss_col)|set(mm_col)]
    df_main['age_ss'] = df_main['age'].copy()
    df_use = scale_feature.scale(df_main, ss_col, mm_col, keep_cols)

    FILL_VALUE = wh_config['FILL_VALUE']

    print(df_use.isnull().sum()/df_use.shape[0])
    df_use.fillna(FILL_VALUE, inplace=True)

    X_cols = wh_config['X_cols']
    # dscoring = xgb.DMatrix(df_use[X_cols])
    model = pickle.load(open(file_winhorse_model, 'rb'))

    y_pred_prob = model.predict_proba(df_use[X_cols])[:, 1]
    s_rate = wh_config['s_rate']
    prob2 = balance_target.adjusted_prob(y_pred_prob, s_rate)

    df_use['pred_prob'] = prob2
    df_use[output_cols].to_csv(file_output)
