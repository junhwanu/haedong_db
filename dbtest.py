import pymysql
import datetime
import time

cour=None
conn=None

conn = pymysql.connect(host='211.253.10.91',user='root',password='goehddl',db='haedong4',charset='utf8')

query = " select date from HSIJ18 where working_day =\'2018-03-28\' limit 1"
with conn.cursor() as cour:
    count = cour.execute(query)
    count12 = cour.fetchone()
print(count12)

query = " select date from HSIJ18 where working_day =\'2018-03-28\' order by id desc limit 1"
with conn.cursor() as cour:
    count = cour.execute(query)
    count2 = cour.fetchone()
print(count2)

print((count2[0]-count12[0]))