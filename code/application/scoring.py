# coding: utf-8


# from logger import logger
from setting import *
from myparser import data_parser
import model.WinHorse as wh
import model.BettingTicket as bt
from bet import bet
from scraping.Repository import HorseDataBeforeRaceRepository

## scraping_for_scoring
# input: race_id
# output: scraped/scoring/horse_list_today.csv?

## parse
# input: scraped/scoring/horse_list_today.csv
# output: inter/scoring/race_id/parsed.csv

## WinHorsepre_today
# input: inter/scoring/race_id/parsed.csv
# output: inter/scoring/race_id/WinHorse/feature_today.csv

## WinHorsepre_merge
# input:inter/scoring/race_id/WinHorse/feature_today.csv, scoring_path / race_id / 'feature_before.csv'
# output: inter/scoring/race_id/WinHorse/feature_merged.csv


## WinHorse_scoring
# input: inter/scoring/race_id/WinHorse/feature_merged.csv
# output: inter/scoring/race_id/WinHorse/score.csv

## BettingTicket_preparation
# input: inter/scoring/race_id/WinHorse/score.csv, inter/scoring/race_id/parsed.csv
# output: inter/scoring/race_id/BettingTicket/feature.csv

## BettingTicket_scoring
# input: inter/scoring/race_id/BettingTicket/feature.csv
# output: inter/scoring/race_id/BettingTicket/score.csv


def main(race_id):
    # scraping
    # check weather and condition
    # HorseDataBeforeRaceRepository().create(race_id)
    # if not data_parser.parse_today(race_id):
        # print(race_id, '雨だったので終わり')
        # return

    wh.binaryClf_preparation_today.main(race_id=race_id)
    # wh.scoring.main(file_wh_feature, file_wh_score)
    # bt.preparation.sanrenpuku_preparation(race_id)
    # bt.scoring.main(file_bt_feature, file_bt_score)
    # bet(date, race_id)
    # LINE


if __name__ == '__main__':
    race_id = str(sys.argv[1])
    main(race_id)
