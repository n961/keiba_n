# -*- coding: utf-8 -*-

from setting import *
from myparser import data_parser

# os.makedirs(data_path/'inter/old', exist_ok=True)
# 既存のtransacfionデータをoldへ移動
# 既存のmasterもoldへ移動
# resourse/common/raw_result/done_parseをraw_resultへ移動
# init-hook="./code" 

# extract_horse
# input: scraped/result, scraped/parsed
# output: inter/horse_master.csv

# parse
# input: scraped/result, scraped/parsed
# output: inter/parsed4ファイル

# input_horse_path = common_path.glob('row_result/race_result*.csv')
# input_info_path = common_path.glob('row_result/race_info*.csv')
# output_path = common_path / 'row_result/use_horse_id.csv'

def add_data():
    print('始まりました')
    file_info = list(resource_path.glob('common/raw_result/info/race_info_20201207.csv'))
    file_result = list(resource_path.glob('common/raw_result/result/race_result_20201207.csv'))
    data_parser.add_result(file_info, file_result, update=True, filename='2020')

def renewal_all():
    print('始まりました')
    file_info = list(resource_path.glob('common/raw_result/info/done_parse/*.csv'))
    file_result = list(resource_path.glob('common/raw_result/result/done_parse/*.csv'))
    data_parser.add_result(file_info, file_result, update=False, filename='new')


if __name__ == '__main__':
    renewal_all()
    # add_data()
