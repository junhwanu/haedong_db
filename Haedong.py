# -*- coding: utf-8 -*-
import os
import sys
from log_manager import LogManager
import db_insert

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/modules');
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/constant');
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/manager');


class Haedong():
    running_time = 0
    log, res, err_log = None, None, None

    def __init__(self):
        super(Haedong, self).__init__()
        self.log, self.res, self.err_log = LogManager.__call__().get_logger()

    def run(self):
        cmd = input()
        insert_module = db_insert.DBInsert()
        if input is None:
            # 최근 데이터 넣기
            print("DB 기준 이후 날짜부터 어제까지 기록")

        else:
            # 시작 날짜 지정하여 넣기
            print("지정한 날짜부터 어제까지 기록")

if __name__ == "__main__":
    headong = Haedong()
    headong.run()