# -*- coding: utf-8 -*-
import datetime

from __module import ModuleClass
from constant import *
import db_manager
from log_manager import LogManager

#DB 넣는건 프로그램이 시작된 날(D-day) 이전 영업일(D-1)을 넣는것이다. 일반적으로 월요일을 제외한 날에 DB에 저장된 working_day값은 D-2의 값이된다.
class DBInsert(ModuleClass):
    db_manager = db_manager.DBManager()
    log, res, err_log = None, None, None

    def __init__(self):
        super(DBInsert, self).__init__()
        self.db_manager.connect()
        self.log, self.res, self.err_log = LogManager.__call__().get_logger()

    def get_last_working_day(self, subject_code):
        query = """
        select max(working_day) as last_working_day from %s
        """ % subject_code

        if not self.exist_table(subject_code): return '2000-01-01'

        result = self.db_manager.exec_query(query, fetch_type=FETCH_ONE)
        if result[0] == None:
            return '2000-01-01'

        return str(result[0])

    def check_first_input(self, subject_code,working_day):
        query = """
        select date from %s where working_day =\'%s\' limit 1
        """ % (subject_code, working_day)

        result = self.db_manager.exec_query(query, fetch_type=FETCH_ONE)
        if result == None:
            return 'err'
        return result

    def check_last_input(self, subject_code, working_day):
        query = """
           select date from %s where working_day =\'%s\' order by id desc limit 1
           """ % (subject_code, working_day)

        result = self.db_manager.exec_query(query, fetch_type=FETCH_ONE)
        if result == None:
            return 'err'
        return result

    #18로 되어있는 월물중에 working_day가 유효한지 판단
    def check_subject_code(self, subject_code, working_day):
        query = """
        select date from %s where working_day =\'%s\'
        """ % (subject_code, working_day)

        result = self.db_manager.exec_query(query, fetch_type=FETCH_ONE)
        return result

    def get_subject_code(self):
        result_list=[]
        query = """
        show tables like \"%%%s%%\"
        """%  str(datetime.date.today().year).replace('20','')
        return self.db_manager.exec_query(query, fetch_type=FETCH_ALL)


    def insert_data(self, subject_code, data):
        try:
            query = """
            insert into %s 
                        (date, price, volume, working_day)
                        values  
            """ % subject_code
            query = query + "(%s, %s, %s, %s)"


            if not self.exist_table(subject_code):
                self.create_table(subject_code)

            self.log.info("%s 종목 데이터 수[%s], 처음 데이터 %s" % (subject_code, len(data), data[0]))
            '''
            while len(data) > 0:
                if len(data) > 1000:
                    self.db_manager.exec_query_many(query, data[:1000])
                    data = data[1000:]
                else:
                    self.db_manager.exec_query_many(query, data)
                    break
            '''
            self.db_manager.exec_query_many(query, data)

        except Exception as err:
            print(err)

    def exist_table(self, subject_code):
        query = "show tables like '%s'" % subject_code
        row = self.db_manager.exec_query(query, FETCH_ONE)

        if row is None:
            return False

        return True

    def drop_table(self, table_name):
        query = "drop table %s" % table_name
        return self.db_manager.exec_query(query)

    def create_table(self, table_name):
        query = """
        CREATE TABLE `%s` (
                            `id` INT(11) NOT NULL AUTO_INCREMENT,
                            `date` TIMESTAMP NULL DEFAULT NULL,
                            `price` FLOAT NULL DEFAULT NULL,
                            `volume` SMALLINT(6) NULL DEFAULT NULL,
                            `working_day` DATE NULL DEFAULT NULL,
                            PRIMARY KEY (`id`),
                            INDEX `date` (`date`),
                            INDEX `working_day` (`working_day`)
                        )
        """
        return self.db_manager.exec_query(query % table_name)

    def get_table(self, table_name):
        query = 'select date, price, working_day from %s' % table_name
        return self.db_manager.exec_query(query, fetch_type=FETCH_ALL)

    def get_table_list(self, subject_symbol, start_date, end_date):
        query = "show tables where substr(Tables_in_haedong, 1, %s) = '%s'\
         and substr(Tables_in_haedong, (select char_length(Tables_in_haedong))\
          - 7, 8) between '%s' and '%s'" % (len(subject_symbol), subject_symbol, start_date, end_date)
        return self.db_manager.exec_query(query, fetch_type=FETCH_ALL)

    def is_empty_table(self, table_name):
        query = """
        select count(*) from %s
        """ % table_name

        if not self.exist_table(table_name): return True

        result = self.db_manager.exec_query(query, fetch_type=FETCH_ONE)
        if result[0] > 0: return False
        return True

    def get_name(self):
        return str(self.__class__.__name__)

    def print_status(self):
        print(self.__getattribute__())

    def check_nomal_data(self,table_name):
        query = 'select * from  %s order by id desc limit 1' % table_name
        return self.db_manager.exec_query(query, fetch_type=FETCH_ONE)

    # 당일데이터 삭제
    def del_err_data(self,table_name):
        #query = "select date from %s where working_day =\'%s\'" % table_name, working_day
        query = "delete from %s where working_day >= '%s'" % (table_name, str(datetime.date.today()))
        print(query)
        result = self.db_manager.exec_query(query, fetch_type=FETCH_ONE)

    def chk_count_row(self, table_name, date):
        query = " select count(*) from %s where working_day = '%s'" % (table_name, date)
        print(query)
        return self.db_manager.exec_query(query, fetch_type=FETCH_ONE)