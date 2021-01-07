from .Repository import RaceInWeekRepository
from .Repository import HorseDataBeforeRaceRepository
from .Repository import HorsesInRaceRepository
from .Repository import RaceResultAndInfoRepository

# 今週分
RaceInWeekRepository().create([20201128])
HorsesInRaceRepository().create([20201128]) 

# 当日
# HorseDataBeforeRaceRepository().create([20201128]d)

# 結果
# RaceResultAndInfoRepository().create([20201128])
