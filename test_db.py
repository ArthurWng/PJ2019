import pymysql


conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='test', charset='utf8')
cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

# txt = input('bozhong: ')
cursor.execute("update data set shengjiang='6'")
tee = cursor.execute("select shengjiang from data")
print(tee)
t = cursor.fetchall()
print(t)
print(type(t))

t1='34'
t2='23'
t3='54'
cursor.execute("insert into data(bozhong, shoucheng, shengjiang) values (%s,%s,%s)" %(t1,t2,t3))
conn.commit()

