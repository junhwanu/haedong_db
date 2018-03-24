import datetime
import time
from operator import eq

t = ['월', '화', '수', '목', '금', '토', '일']
n = time.localtime().tm_wday
day = '2018-03-19'
day2 = '2018-03-24'
day.replace('-','')
day2.strip('-')
tran_day = datetime.datetime.strptime(day,"%Y-%m-%d").date()
print(t[n])
print(day)

if (n not in(5,6)):
    print(datetime.date.today()-datetime.timedelta(days =1))
    print(eq(tran_day,datetime.date.today()))

