import pymysql
import datetime
import time

cour=None
conn=None

conn = pymysql.connect(host='211.253.8.64',user='root',password='goehddl',db='haedong4',charset='utf8')
working_day = '2019-01-08'
day = datetime.datetime.strptime(working_day,"%Y-%m-%d").date()
tday = day - datetime.timedelta(days =1)
print(tday)
print(day.weekday())
query = " select count(*)from GCG19 where working_day = '%s'" % working_day
print(query)
with conn.cursor() as cour:
    count = cour.execute(query)
    count12 = cour.fetchone()
print(count12)