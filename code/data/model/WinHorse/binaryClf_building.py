# coding: utf-8

## 準備

from setting import *
from model_setting import *
from model import balance_target
from model.plot_helper import *
from read_df import df_from_csv
from . import scale_feature

COMMENT = ''
TARGET_VALUE = 3
FILL_VALUE = -2
num_round = 200
params = {
        'objective': 'binary:logistic',
        'silent':0,
        'gamma':10,
        'random_state':0,
        # 学習用の指標 (RMSE)
        'eval_metric': 'logloss',
}

key_cols = ['race_id', 'horse_id', 'race_date', 'arrival']
not_z_col = [
    'weight_null_flg',
    'is_same_place',
    'same_cluster_flg',
    'gender_セ',
    'gender_牝',
    'gender_牡',
    'place_なし',
    'place_地',
    'place_外',
    'place_東',
    'place_西',
    'first_data_flg',
    'is_first_in_prize',
    'last_turf_flg',
    'last_weather_int',
    'last_condition_int',
    'course_num',
    'race_month'
]

## 標準化
ss_col = [
    'weight',
    'weight_change_rate',
    'handy_rate',
    'handy_weight',
    'age',
    'interval_days',
    'distance_diff',
    'last_speed',
    'last_uphill_speed',
    'last_uphill',
    'last_uphill_samecc',
    'last_weight_3_mean',
    'abs_weight_change',
    'last_got_prize'
]

mm_col = [
    'last_arrival',
    'p2_arrival',
    'p3_arrival',
]

X_cols = ss_col + mm_col + not_z_col
print('X_cols: ', len(X_cols))
dt_now = datetime.datetime.now().strftime('%Y%m%d%H%M')

log_path = resource_path /'model_build/logs/wh' /dt_now


def split_data(df_use):
    ## モデル
    valid_id = np.random.choice(df_use.race_id.unique(), size=int(df_use.race_id.nunique() * 0.1), replace=False)
    print('valid_id len: ',len(valid_id))

    df_test = df_use.query('race_id in @valid_id')
    print('df_test:  shape/race_id num', df_test.shape, df_test.race_id.nunique())
    df_train = df_use.query('race_id not in @valid_id')
    print('df_train: shape/race_id num', df_train.shape, df_train.race_id.nunique())

    target_size = df_train.target.sum()
    df_train_0 = df_train[df_train.target==0]
    df_train_use = df_train_0.sample(target_size, random_state=0)
    df_train_use = pd.concat([df_train_use, df_train[df_train.target==1]])

    df_sampling = balance_target.get_df_sampling(df_train_use['target'], df_test['target'], 'target')
    df_sampling.loc['test', 'num_id'] = len(valid_id)
    df_sampling.loc['All', 'num_id'] = df_use.race_id.nunique()
    df_sampling.to_csv(log_path/'data_num.csv', encoding='utf-8-sig')
    return df_train_use, df_test


def build_model(df_train):
    X_train = df_train[X_cols]
    y_train = df_train['target']
    dtrain = xgb.DMatrix(X_train, label=y_train)
    # dvalid = xgb.DMatrix(X_test, label=y_test)
    # watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
    model = xgb.train(
        params,
        dtrain,#訓練データ
        num_round,#設定した学習回数
        # early_stopping_rounds=20,
        # evals=watchlist,
    )
    return model


def output_model(model, y_test, prob2, s_rate, AUC):
    pickle.dump(model,open(log_path/'model.pickle', 'wb'))
    model.trees_to_dataframe().to_csv(log_path/'model_trees.csv', encoding='utf-8-sig', index=False)

    xgb.plot_importance(
        model,
    #     cls_rdn.best_estimator_,
        importance_type='gain',
        show_values=False,
        max_num_features=40
    )
    plt.savefig(log_path/'image/feature_importance.png', pad_inches=.05, bbox_inches='tight')

    get_score_plot(get_scores(y_test, prob2), log_path/'image/score_by_th.png')
    plot_calibration(y_test, prob2, log_path/'image/calibration_plot.png')
    plot_roc(y_test, prob2, log_path/'image/roc_plot.png')
    with open(log_path/'model_config.json', 'w') as f:
        json.dump({
                'ss_col': ss_col, 
                'mm_col': mm_col,
                'not_z_col':not_z_col,
                'TARGET_VALUE': TARGET_VALUE,
                'FILL_VALUE': FILL_VALUE,
                'params': params,
                'num_round': num_round,
                's_rate': s_rate
            },
            f,
            indent=4
        )
    with open(log_path/'AUC.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n') # 行末は改行
        writer.writerow([dt_now, AUC, TARGET_VALUE, COMMENT])



def predict(model, s_rate, df_test, df_use):
    dtest = xgb.DMatrix(df_test[X_cols])
    prob2 = balance_target.adjusted_prob(model.predict(dtest), s_rate)
    df_test['pred_prob'] = prob2
    df_test[['arrival', 'horse_id', 'race_id', 'pred_prob']].to_csv(log_path/f'{dt_now}.csv', index=False)

    prob3 = balance_target.adjusted_prob(model.predict(xgb.DMatrix(df_use[X_cols])), s_rate)
    df_use['pred_prob'] = prob3
    df_use[['arrival', 'horse_id', 'race_id', 'pred_prob']].to_csv(log_path/f'{dt_now}_all.csv', index=False)
    return prob2
 

def main(filename):
    file_input = resource_path/f'model_build/features/WinHorse_all_{filename}.csv'
    df_main = df_from_csv(file_input)
    df_main.race_date = pd.to_datetime(df_main.race_date)
    df_main['race_month'] = df_main.race_date.dt.month
    df_main['age_ss'] = df_main['age'].copy()
    df_use = scale_feature.scale_by_race_id(df_main, ss_col, mm_col, key_cols+not_z_col)
    df_use['target'] = 0
    df_use.loc[df_use.arrival<=TARGET_VALUE, 'target'] = 1
    
    df_use.fillna(FILL_VALUE, inplace=True)
    df_train, df_test = split_data(df_use)
    y_test = df_test['target']
    
    s_rate = balance_target.get_srate(y_test)
    model = build_model(df_train)
    os.makedirs(log_path/'image', exist_ok=True)
    prob2 = predict(model, s_rate, df_test, df_use)
    AUC = roc_auc_score(y_test, prob2)
    print('AUC: ', AUC)
    print('出力フォルダ: ', log_path)
    output_model(model, y_test, prob2, s_rate, AUC)
