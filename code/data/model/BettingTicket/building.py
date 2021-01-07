# coding: utf-8

from setting import *
from model_setting import *
from read_df import df_from_csv
from model import balance_target
from model import plot_helper

## 入出力
dt_now = datetime.datetime.now().strftime('%Y%m%d%H%M')
log_path = resource_path /'model_build/logs/bt' /dt_now
os.makedirs(log_path/'image', exist_ok=True)

## 購入閾値検索

def get_return(df, col, vmax=1, step=0.01, over=True, plot_min=0.8):
    df_ret = pd.DataFrame(columns=['対象数', '回収率'])
    if over:
        op = '>'
    else:
        op = '<'
    max_ret = -10000
    max_th = -1
    max_len = -1
    for th in np.arange(0, vmax, step):
        th = round(th, 2)
        tmp = df.query(col + op + str(th))
        ret = round((tmp.query('acc_flg==1').odds.sum()/tmp.shape[0]), 3)
        if ret > max_ret:
            max_ret = ret
            max_th = th
            max_len = len(tmp)
        df_ret.loc[th] = [tmp.shape[0], ret]
    print(f'対象カラム: {col}, 最大回収率: {max_ret}, 閾値: {max_th}, 対象数: {max_len}, 対象率: {round(max_len/df.shape[0], 3)}')
    
    df_ret['対象率'] = df_ret.対象数 / df.shape[0]
    
#     plt.scatter(max_th, max_ret, s=100, c='none', edgecolors='blue')
    df_ret.回収率.plot()
    plt.plot([0,vmax], [1,1])
    plt.ylim(plot_min, )
    plt.ylabel('回収率')
    plt.xlabel(col)
    plt.twinx()
    df[col].hist(bins=20, alpha=.1, color='c', grid=False, range=(0, vmax))
    plt.ylabel('件数')
    plt.savefig(log_path/'image/return_plot.png', pad_inches=0.05, bbox_inches='tight')
    df_ret.to_csv(log_path/'閾値検索.csv', encoding='utf-8-sig')
    # plt.show()
    return df_ret, max_th

X_cols = [
    'odds',
    'score1',
    'score2',
    's_diff',
    'EV',
    'EV_diff',
    's_diff_rate',
    'weather_int_2',
    'weather_int_3',
    'condition_int_2',
    'condition_int_3'
]


file_sampling = log_path / 'df_sampling.csv'

def main():
    file_input = resource_path /f'model_build/logs/wh/202012130029/bt_features.csv'
    df_train = df_from_csv(file_input)

    df_train.dropna(inplace=True)
    ## 購入モデル
    print('len(X_cols): ', len(X_cols))
    print('df_train.shape: ', df_train.shape)
    target_col = 'acc_flg'
    s_rate, df_train, df_test, _df_no_use = balance_target.balanced_data(df_train, X_cols, target_col, file_sampling)

    X_train = df_train[X_cols]
    X_test = df_test[X_cols]
    y_train = df_train[target_col]
    y_test = df_test[target_col]

    ### 学習
    clf = LogisticRegression(random_state=0)
    clf.fit(X_train, y_train)

    ### 予測
    y_pred_prob = clf.predict_proba(X_test)[:, 1]
    prob2 = balance_target.adjusted_prob(y_pred_prob, s_rate)

    plot_helper.plot_calibration(y_test, prob2, file_output=log_path/'image/calibration_plot.png')
    plot_helper.plot_roc(y_test, y_pred_prob, file_output=log_path/'image/roc_plot.png')
    AUC = roc_auc_score(y_test, y_pred_prob)
    print('AUC: ', AUC)

    ### 閾値検索
    df_test['pred'] = prob2
    df_ret, max_th = get_return(df_test, 'pred', 1, 0.01, over=True, plot_min=0.8)

    pd.Series(clf.coef_[0], X_train.columns).to_frame().to_csv(log_path/'coef.csv')
    pickle.dump(clf,open(log_path/'model.pickle', 'wb'))
    with open(log_path/'model_config.json', 'w') as f:
        json.dump({
                'X_cols': X_cols,
                's_rate': s_rate,
                'AUC':AUC
            },
            f,
            indent=4
        )

