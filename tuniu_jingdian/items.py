# -*- coding: UTF-8 -*-
#Author：Yinli

import scrapy

'''
areaItem:保存地区信息的item
包含地区名字、地区id、景点数目、想去人数、评论数目、
评分、商场数目、游记数目以及地区的url
'''
class areaItem(scrapy.Item):
    name = scrapy.Field()
    id = scrapy.Field()
    attractions_number = scrapy.Field()
    wanting_number = scrapy.Field()
    comments_number = scrapy.Field()
    score = scrapy.Field()
    mall_number = scrapy.Field()
    travel_notes_number = scrapy.Field()
    url = scrapy.Field()

'''
attractionItem:保存景点信息的item
包含所属地区id、所属地区名字、景点id、景点名字、
景点地址、游玩用时参考、景点简介以及景点url
'''
class attractionItem(scrapy.Item):
    id = scrapy.Field()
    area = scrapy.Field()
    area_id = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    time_cost = scrapy.Field()
    introduction = scrapy.Field()
    url = scrapy.Field()