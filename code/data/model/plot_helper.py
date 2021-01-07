# coding: utf-8
from model_setting import *

def plot_calibration(y_test, prob2, file_output=None):
    prob_true, prob_pred = calibration_curve(
        y_true=y_test,
        y_prob=prob2,
        n_bins=20
    )
    fig, ax1 = plt.subplots()
    ax1.plot(
        prob_pred,
        prob_true,
        marker='s',
        label='calibration plot',
        color='skyblue'
    )
    ax1.plot([0, 1], [0, 1], linestyle='--', label='ideal', color='limegreen')
    ax1.legend(bbox_to_anchor=(1.12, 1), loc='upper left')
    ax2 = ax1.twinx()
    ax2.hist(prob2, bins=20, histtype='step', color='orangered')
    ax1.set_ylabel('accuracy')
    ax1.set_xlabel('score')
    ax2.set_ylabel('frequency')
    if not file_output is None:
        fig.savefig(file_output, bbox_inches='tight', pad_inche=.05)


def plot_roc(y_test, y_pred_prob, file_output=None):
    fpr_all, tpr_all, _thresholds_all = roc_curve(y_test, y_pred_prob, drop_intermediate=False)
    fig, ax = plt.subplots()
    ax.plot(fpr_all, tpr_all, marker='o', markersize=.01)
    ax.plot([0,1],[0,1], color='red', linewidth=.5)
    ax.set_xlabel('FPR: False positive rate')
    ax.set_ylabel('TPR: True positive rate')
    ax.grid()
    if not file_output is None:
        fig.savefig(file_output, bbox_inches='tight', pad_inche=.05)


def get_scores(y_test, prob2):
    df_score = pd.DataFrame(columns=['acc', 'rec', 'prec', 'f1'])
    for th in np.arange(0, 1, 0.05):
        th = round(th, 2)
        tmp = np.where(prob2 < th, 0, 1)
        acc = accuracy_score(y_test, tmp)
        rec = recall_score(y_test, tmp)
        prec = precision_score(y_test, tmp)
        f1 = f1_score(y_test, tmp)
        df_score.loc[th] = [acc, rec, prec, f1]
    df_score.index.name = 'thresh'
    # df_score.to_csv(log_path/'score.csv', encoding='utf-8-sig')
    return df_score


def get_score_plot(df_score, file_output=None):
    df_score.plot()
    plt.legend(bbox_to_anchor=(1, 1))
    plt.ylabel('score')
    if not file_output is None:
        plt.savefig(file_output, pad_inches=.05, bbox_inches='tight')
    