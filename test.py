import datetime
import time
from operator import eq

t = ['월', '화', '수', '목', '금', '토', '일']
n = time.localtime().tm_wday
day = '2018-03-19 08:00:00'
day2 = '2018-04-17'
subject = 'GCJ18'
day.replace('-','')
day2.strip('-')


print(day)
#월요일이 1
#tran_day = datetime.datetime.strptime(day,"%Y-%m-%d").date().isoweekday()
print(datetime.datetime.strptime(day2,"%Y-%m-%d").date()==datetime.date.today())
print(str(datetime.date.today()))
#print(tran_day)
