# -*- coding: utf-8 -*-
from __module import ModuleClass
from constant import *
import db_manager


class DBInsert(ModuleClass):
    db_manager = None

    def __init__(self):
        super(DBInsert, self).__init__()
        self.db_manager = db_manager.DBManager()
        self.db_manager.connect()

    def get_last_date_in_DB(self):
        pass

    def insert_data(self, subject_code, data):

        pass

    def exist_table(self, subject_code):
        query = "show tables in haedong like '%s'" % subject_code
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

    def get_name(self):
        return str(self.__class__.__name__)

    def print_status(self):
        print(self.__getattribute__())