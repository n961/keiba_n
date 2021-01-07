# -*- coding: utf-8 -*-

from setting import *
import model.WinHorse as wh
import model.BettingTicket as bt


# file_winhorse_before = resource_path / 'model_build/logs/xxx.csv'
def main():
    # wh.binaryClf_preparation_before.main(filename='new', update=False)
    wh.binaryClf_preparation_today.main(filename='new', update=False)

    # wh.binaryClf_building.main(filename='new')
    # bt.preparation.building_data()
    # bt.building.main()

if __name__ == '__main__':
    main()
