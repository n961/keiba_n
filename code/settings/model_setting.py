from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve,recall_score, confusion_matrix, accuracy_score, precision_score, f1_score
from sklearn.metrics import roc_auc_score
import xgboost as xgb
import json
import pickle
import csv

from setting import *

file_winhorse_config = common_path / 'model/WinHorse/model_config.json'
file_winhorse_model = common_path / 'model/WinHorse/model.pickle'

file_bettingticket_config = common_path / 'model/BettingTicket/model_config.json'
file_bettingticket_model = common_path / 'model/BettingTicket/model.pickle'