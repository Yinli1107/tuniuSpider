# -*- coding: UTF-8 -*-
#Author：Yinli

import json
from tuniu_jingdian.items import attractionItem,areaItem
import pymysql

'''
storeToLocalPipeline:将item保存到本地磁盘json文件中
'''
class storeToLocalPipeline(object):
    # 初始化打开文件
    def __init__(self):
        self.areaFile = open('../tuniu_jingdian/area.json','w',encoding='utf-8')
        self.attractionFile = open('../tuniu_jingdian/attractions.json', 'w', encoding='utf-8')

    # 将item序列化为json字符串，然后写入对应的文件中
    def process_item(self, item, spider):
        if(isinstance(item,areaItem)):
            line = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.areaFile.write(line)
        elif(isinstance(item,attractionItem)):
            line = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.attractionFile.write(line)
        return item

    # 当爬虫关闭时关闭文件
    def spider_closed(self):
        self.areaFile.close()
        self.attractionFile.close()

'''
storeToMysqlPipeline:将item保存到服务器mysql数据库中
'''
class storeToMysqlPipeline(object):
    # 与数据库建立链接并重置area表和attraction表
    def __init__(self):
        # 连接数据库
        self.conn = pymysql.connect(host='114.116.43.151', user='root', passwd='sspku02!',db='tuniu')
        print("————————————————连接数据库成功————————————————")
        # 重置area表
        self.cur = self.conn.cursor()
        self.cur.execute('drop table if exists area')
        # 创建area表并检查是否创建成功
        create_area_sql = """CREATE TABLE area (id INT, name CHAR(20), url CHAR(50), attractions_number CHAR(10),
        wanting_number CHAR(10), comments_number CHAR(10), score CHAR(5), mall_number char(10),
        travel_notes_number CHAR(10)) default charset='utf8'
        """
        self.cur.execute(create_area_sql)
        self.cur.execute("show tables")
        if('area' in list(map(lambda x:x[0],self.cur.fetchall()))):
            print("————————————————创建表area成功————————————————")

        # 重置attraction表
        self.cur.execute('drop table if exists attraction')
        # 创建attraction表并检查是否创建成功
        create_attraction_sql = """CREATE TABLE attraction (id CHAR(20),area_name CHAR(20),area_id INT, name CHAR(20), 
        url CHAR(50), address text, time_cost CHAR(10), introduction text) default charset='utf8'
        """
        self.cur.execute(create_attraction_sql)
        self.cur.execute("show tables")
        if('attraction' in list(map(lambda x:x[0],self.cur.fetchall()))):
            print("————————————————创建表attraction成功————————————————")

    # 将item的信息存到数据库中
    def process_item(self, item, spider):
        # 如果是areaItem则存到area表中去
        if (isinstance(item, areaItem)):
            insert_sql = """
            insert into area (id,name,url,attractions_number,wanting_number,comments_number
            ,score,mall_number,travel_notes_number) value (%s,'%s','%s','%s','%s','%s','%s','%s','%s')
            """
            self.cur.execute(insert_sql%(item['id'], item['name'],item['url'],item['attractions_number'],
                                         item['wanting_number'],item['comments_number'],item['score'],
                                         item['mall_number'],item['travel_notes_number']))
        # 如果是attractionItem则存到attraction表中去
        elif (isinstance(item, attractionItem)):
            insert_sql = """
            insert into attraction (id,name,url,area_name,area_id,address,time_cost,introduction) 
            values ('%s','%s','%s','%s','%s','%s','%s','%s')
            """
            self.cur.execute(insert_sql%(item['id'],item['name'],item['url'],item['area'],item['area_id'],
                                         item['address'],item['time_cost'],item['introduction']))
        # 提交上传数据
        self.conn.commit()
        return item

    # 关闭爬虫时关闭与数据库的连接
    def spider_closed(self):
        self.cur.close()
        self.conn.close()
        print("————————————————爬完了————————————————")