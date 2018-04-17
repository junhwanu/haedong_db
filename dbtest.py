import pymysql
import datetime
import time

cour=None
conn=None

conn = pymysql.connect(host='211.253.10.91',user='root',password='goehddl',db='haedong4',charset='utf8')

query = " select date from GCM18 where working_day = '2018-04-16'"
with conn.cursor() as cour:
    count = cour.execute(query)
    count12 = cour.fetchone()
print(count12)

