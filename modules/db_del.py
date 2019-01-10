import pymysql
import datetime
import time

cour=None
conn=None

conn = pymysql.connect(host='211.253.8.64',user='root',password='goehddl',db='haedong4',charset='utf8')

#result = cour.execute('select * from GCG18 where working_day =\'2018-01-09\'')
with conn.cursor() as cour :
    result = cour.execute('show tables like "%19%"')
    result2 = cour.fetchall()
# print(result)

for i in result2 :
    query = "select date from %s where working_day >=\'%s\'" % (i[0], '2019-01-10')
    print(query)
    with conn.cursor() as cour:
        count = cour.execute(query)
        print(count)
    if count>0:
        query1 = "delete from %s where working_day >= '%s'" % (i[0], '2019-01-10')
        with conn.cursor() as cour:
            cour.execute(query1)
            print(query1)
            conn.commit()
    else :
        pass

