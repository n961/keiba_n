import subprocess
from scraping.Repository import RaceInWeekRepository
import os
import glob


class SetScheduler:
    def set(self, date):
        self.delete_all_bat()
        df = RaceInWeekRepository().read(date)
        df.map(lambda row: self.register_task(row))

    def register_task(self, row):
        race_id = row['race_id']
        date = row['race_date']
        time = row["time"] + ':00'

        # pipenv runのバッチファイル作成
        # コマンドからタスク登録する際、pipenvの実行ディレクトリを指定する方法がなかったため、
        # バッチファイルを絶対パス指定で登録する方式にした
        bat_file_name = f'scoring{race_id}.bat'
        bat_path = f'C:/users/nishina/workspace/keiba_y/keiba/code/scheduler/scripts/{bat_file_name}'
        script = f'cd C:/users/nishina/workspace/keiba_y/keiba \n pipenv run scoring {race_id}'
        f = open(f'scripts/{bat_file_name}', 'w')
        f.write(f'{script}')
        f.close()

        # タスクスケジューラへのタスク登録
        cmd = f'schtasks /create /sc Once /sd {date} /st {time} /tn scoring /tr {bat_path} /rl highest /F'
        code = subprocess.run(cmd, shell=True).returncode
        if code != 0:
            print("タスクの登録に失敗しました")

    def delete_all_bat(self):
        # バッチファイルを全て削除する
        for file in glob.glob('scripts/*.bat'):
            os.remove(file)