import pymysql
import datetime
import time

cour=None
conn=None

conn = pymysql.connect(host='211.253.10.91',user='root',password='goehddl',db='haedong4',charset='utf8')

query = "select date from GCM18 where working_day =%s limit 1" % str(datetime.date.today())
print(query)
with conn.cursor() as cour:
    count = cour.execute(query)
    count2 = cour.fetchone()
    if count2 != None:
        print(str(count2[0]))

