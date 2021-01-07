# -*- coding: utf-8 -*-


from setting import *
import model.WinHorse as wh
import model.BettingTicket as bt
# winhorsepre_before
# winhorsepre_today
# winhorse_merge
# winhorsebuild

# bet_prepare
# betbuild

# model_configを自動入れ替え
# パラメータ記録
file_winhorse_before = resource_path / 'model_build/logs/xxx.csv'


if __name__ == '__main__':
    wh.binaryClf_preparation_before.main(filename='2020', update=True)
    wh.binaryClf_preparation_today.main(filename='2020', update=True)

    ## スコアリングしてみたいとき
    filename = '2020'
    file_input = common_path/f'model/WinHorse/features/all_{filename}.csv'
    file_wh_score = common_path/f'model/WinHorse/features/wh_score_{filename}.csv'
    wh.scoring.main(file_input, file_wh_score)

    # bt.preparation.building_data(file_input_info, file_wh_score, file_output)
    # bt.building.main(file_input)
