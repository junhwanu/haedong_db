import datetime
import time
from operator import eq

t = ['월', '화', '수', '목', '금', '토', '일']
n = time.localtime().tm_wday
day = '2018-03-19'
day2 = '2018-03-27'
day.replace('-','')
day2.strip('-')
#월요일이 1
tran_day = datetime.datetime.strptime(day2,"%Y-%m-%d").date().isoweekday()
print(datetime.datetime.strptime(day2,"%Y-%m-%d").date()==datetime.date.today())
print(t[n])
print(tran_day)

if (n !=4):
    print(datetime.date.today()-datetime.timedelta(days =1))
    print(eq(tran_day,datetime.date.today()))

