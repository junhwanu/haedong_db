import datetime, time
t = ['월', '화', '수', '목', '금', '토', '일']
n = time.localtime().tm_wday
print(t[n])

if (n not in(5,6)):
    print(datetime.date.today())