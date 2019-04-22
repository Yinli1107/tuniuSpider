import pymysql

conn = pymysql.connect(host='114.116.43.151', user='root', passwd='sspku02!',db='tuniu')
cur = conn.cursor()
cur.execute('insert into area(id) value(456)')
#print('test' in list(map(lambda x:x[0],cur.fetchall())))
#cur.close()
conn.commit()
#conn.close()