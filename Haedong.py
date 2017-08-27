# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/config')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/constant')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/logs')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/manager')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/modules')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/utils')

from log_manager import LogManager
import kiwoom

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
        #start_date = input()
        #kw = kiwoom.Api(start_date)
        kw = kiwoom.Api()

if __name__ == "__main__":
    headong = Haedong()
    headong.run()