# -*- coding: utf-8 -*-
import pymysql
from constant import *
from __manager import ManagerClass


class DBManager(ManagerClass):
    curs = None
    conn = None
    is_connected = False

    def __init__(self):
        super(DBManager, self).__init__()

    def connect(self):
        self.conn = pymysql.connect(host=DB_SERVER_ADDR, user=DB_USER_ID, password=DB_USER_PWD, db=DB_NAME, charset=DB_CHARSET)
        self.curs = self.conn.cursor()
        self.is_connected = True

    def disconnect(self):
        self.conn.close()

    def exec_query(self, query, fetch_type=None, fetch_count=None, cursor_type=CURSOR_TUPLE):
        if not self.is_connected:
            self.connect()

        if cursor_type == CURSOR_DICT:
            self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        elif cursor_type == CURSOR_TUPLE:
            self.curs = self.conn.cursor()

        result = self.curs.execute(query)
        self.conn.commit()

        if fetch_type == FETCH_ONE:
            return self.curs.fetchone()
        elif fetch_type == FETCH_ALL:
            return self.curs.fetchall()
        elif fetch_type == FETCH_MANY:
            return self.curs.fetchmany(fetch_count)
        else:
            return result

    def exec_query_many(self, query, data, fetch_type=None, fetch_count=None, cursor_type=CURSOR_TUPLE):
        if not self.is_connected:
            self.connect()

        if cursor_type == CURSOR_DICT:
            self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        elif cursor_type == CURSOR_TUPLE:
            self.curs = self.conn.cursor()

        result = self.curs.executemany(query, data)
        self.conn.commit()

        if fetch_type == FETCH_ONE:
            return self.curs.fetchone()
        elif fetch_type == FETCH_ALL:
            return self.curs.fetchall()
        elif fetch_type == FETCH_MANY:
            return self.curs.fetchmany(fetch_count)
        else:
            return result

    def get_name(self):
        return str(self.__class__.__name__)

    def print_status(self):
        print(self.__getattribute__())
