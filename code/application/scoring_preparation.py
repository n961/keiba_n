# coding: utf-8


from setting import *
from scraping.Repository import RaceInWeekRepository
from scraping.Repository import HorsesInRaceRepository
from scheduler.set_scheduler import SetScheduler
from myparser import data_parser
from model.WinHorse import binaryClf_preparation_before
# import check_race


# get race_id_list

## scraping_for_preparation
# input: race_id
# output: scoring/race_id/horse_list.csv

## search_from_master
# input: scraped/scoring/horse_list.csv, inter/horse_master.csv
# output: inter/scoring/race_id/use_horse_id.csv, (inter/horse_master.csv)
# 

## winhorsepre_before
# input: inter/scoring/race_id/use_horse_id.csv, inter/parsed/race_result_parsed.csv
# for race_id in race_id_list:
    # output:inter/scoring/race_id/WinHorse/feature_before.csv


def main(days_list):
    # scraping
    filename = days_list[0]
    print(filename)
    # RaceInWeekRepository().create(days_list)
    # HorsesInRaceRepository().create(days_list)
    data_parser.parse_before(filename)
    binaryClf_preparation_before.main(filename, update=False)

    SetScheduler().set(filename)


if __name__ == '__main__':
    sys.argv.pop(0)
    days_list = sys.argv
    print(days_list)
    main(days_list)
