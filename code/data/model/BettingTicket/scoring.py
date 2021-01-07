# coding: utf-8

from setting import *
from model_setting import *
from read_df import df_from_csv
from model import balance_target

def main(file_input, file_output):
    df_main = df_from_csv(file_input)
    bt_config = json.load(open(file_bettingticket_config, 'r'))

    clf = pickle.load(open(file_bettingticket_model, 'r'))
    X_cols = bt_config['X_cols']
    s_rate = bt_config['s_rate']

    y_pred_prob = clf.predict_proba(df_main[X_cols])[:, 1]
    prob2 = balance_target.adjusted_prob(y_pred_prob, s_rate)
    df_main['pred'] = prob2
    df_main.to_csv(file_output)