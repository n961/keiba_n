# -*- coding: utf-8 -*-
# -

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.options.display.max_columns = 100
pd.options.display.max_rows = 100
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.family'] = 'Yu mincho'

import os
import gc
import sys
import glob
import tqdm
import pickle
import json
import pathlib
import datetime
import configparser
import warnings
warnings.simplefilter('ignore')

# +
# config_path = '../settings/config.ini'
# assert os.path.exists(config_path), f'"{config_path}" is not exists'

# def get_config(MODE):
#     config = configparser.SafeConfigParser()
#     config.read(config_path)
#     return config[MODE]
# -

# MODE = "SCORING"
# MODE = "UPDATE_RESULT"
# MODE = "UPDATE_MODEL"
# MODE = 'RENEWAL_RESULT'

# config = get_config(MODE)



resource_path = pathlib.Path('../../resource')
assert os.path.exists(resource_path), 'resourceフォルダがないよ'
common_path = resource_path / 'common'
scoring_path = resource_path / 'scoring'
file_horse_master = common_path / 'horse_master.csv'
file_race_transaction = common_path / 'race_result_transaction.csv'
file_race_master = common_path / 'race_info_master.csv'
file_course_cluster = resource_path / 'model_build/course_data_cluster.csv'
dt_now = datetime.datetime.now().strftime('%y%m%d%H%M')

file_sanrenpuku_odds = common_path / 'sanrenpuku_odds.csv'


# + active=""
# # inter
# FILE_RESULT_INTER = data_path / config[MODE].get('INTER_RESULT')
# FILE_INFO_INTER = data_path / config[MODE].get('INTER_INFO')
# FILE_OBSTACLE_RESULT = data_path / config[MODE].get('OBSTACLE_RESULT')
# FILE_OBSTACLE_INFO = data_path / config[MODE].get('OBSTACLE_INFO')

# + active=""
# FILE_SCRAPED_RESULT = list(data_path.glob(config[MODE].get("SCRAPED_RESULT")))
# FILE_SCRAPED_INFO = list(data_path.glob(config[MODE].get("SCRAPED_INFO")))
# FILE_PARSED_RESULT = data_path / config[MODE].get("PARSED_RESULT")
# FILE_PARSED_INFO = data_path / config[MODE].get("PARSED_INFO")

# + active=""
# FILE_WINHOURSE_FEATURE = data_path / config[MODE].get("WINHOURSE_FEATURE")
# FILE_WINHOURSE_SCORE = data_path / config[MODE].get("WINHOURSE_SCORE")
# FILE_BETTINGTICKET_SCORE = data_path / config[MODE].get("BETTINGTICKET_SCORE")
