# -*- coding: UTF-8 -*-
#Author：Yinli

import scrapy
from tuniu_jingdian.items import areaItem, attractionItem

class spider(scrapy.Spider):
	# 爬虫名字以及起始页面
	name = 'tuniu'
	start_urls = [
		'http://go.tuniu.com/'
	]

	'''
	parse(self, response):
		从http://go.tuniu.com/开始爬，爬每个地区的网站地址，然后送到parseArea进行下一步解析
	Author：Yinli
	'''
	def parse(self, response):
		# 爬取当前页面的各个地区的id、名字以及链接
		area_ids = response.css("div#hot.wrapper.gd-floor.hot-floor div.module.Jmodule.clearfix")[0]\
			.css("dd").xpath("a/@data-code").extract()
		area_names= response.css("div#hot.wrapper.gd-floor.hot-floor div.module.Jmodule.clearfix")[0]\
			.css("dd").xpath("a/@data-name").extract()
		area_urls = response.css("div#hot.wrapper.gd-floor.hot-floor div.module.Jmodule.clearfix")[0]\
			.css("dd").xpath("a/@data-url").extract()
		# 对每个地区的网址进行下一步解析
		for i in range(len(area_ids)):
			# 先对每个地区初始化一个对应item并存储相关id、name和url信息
			item = areaItem()
			item['id'] = int(area_ids[i])
			item['name'] = area_names[i]
			item['url'] = area_urls[i]
			# 再将item和网址一起送到下一个解析函数中去
			yield scrapy.Request(url=area_urls[i], meta={'item':item}, callback=self.parseArea)

	'''
	parseArea(self,response):
		解析地区网站，爬地区景点个数，想去人数，评论数，评分，购物商场个数以及游记数目
		如果该地区有景点，再把景点列表网站解析出来，送到parseAttractionPage进一步解析
	Author：Yinli
	'''
	def parseArea(self, response):
		# 爬取页面中的想去人数、景点个数、评论数、评分、商场数量以及游记数量并存入item中
		item = response.meta['item']
		item['wanting_number'] = int(response.css("span.count::text").extract_first())

		if(response.css("div.module.module1.fl div.summary.off a b::text").extract() == []):
			item['attractions_number'] = 'NULL'
		else:
			item['attractions_number'] = int(response.css("div.module.module1.fl div.summary.off a b::text").extract_first())

		if(response.css("div.module.module3.fr div.summary.off a b::text").extract() == []):
			item['mall_number'] = 'NULL'
		else:
			item['mall_number'] = int(response.css("div.module.module3.fr div.summary.off a b::text").extract_first())

		if(response.css("div.middle p.title span::text").extract() == []):
			item['comments_number'] = 0
		else:
			item['comments_number'] = int(response.css("div.middle p.title span::text").extract_first())

		if(response.css("div.score.fl").xpath("p//text()").extract() == []):
			item['score'] = 'NULL'
		else:
			item['score'] = response.css("div.score.fl").xpath("p//text()").extract_first()

		if(response.css("div.note.wrapper div.summary a.info span::text").extract() == []):
			item['travel_notes_number'] = 0
		else:
			item['travel_notes_number'] = int(response.css("div.note.wrapper div.summary a.info span::text").extract_first())

		# 将item送入pipeline
		yield item

		# 如果此地区有景点列表，那么将景点列表页解析出来送去parseAttractionPage解析
		if(item['attractions_number'] != 'NULL'):
			# 先把该地区的id和名字提取出来，和景点列表的url一起送去下一个解析函数
			area_name = item['name']
			area_id = item['id']
			attractions_page = 'http://www.tuniu.com'+response.\
				css("div.module.module1.fl div.summary.off").xpath("a/@href").extract_first()
			yield scrapy.Request(url=attractions_page,meta={'area_name':area_name,'area_id':area_id}
			                     ,callback=self.parseAttractionPage)

	'''
	parseAttractionPage(self, response):
		解析出每个景点的网站链接，送到parseAttraction进一步解析
		如果有下一页就解析出下一页的链接，重复调用自身
	Author：Yinli
	'''
	def parseAttractionPage(self, response):
		# 获取景点所在地区的id和名字以及景点id和名字以及链接
		area_name = response.meta['area_name']
		area_id = response.meta['area_id']
		attraction_names = response.css("div.wrapper div.allSpots ul li a.pic div.name::text").extract()
		attraction_links = response.css("div.wrapper div.allSpots ul li").xpath("a/@href").extract()
		attraction_ids = list(map(lambda x:x.split('/')[1], response.css("div.wrapper div.allSpots ul li")
		                          .xpath("a/@href").extract()))
		# 分别爬取每个景点
		for i in range(len(attraction_ids)):
			# 初始化一个对应的item，并保存相关信息
			item = attractionItem()
			item['area'] = area_name
			item['area_id'] = area_id
			item['id'] = attraction_ids[i]
			item['name'] = attraction_names[i]
			item['url'] = 'http://www.tuniu.com'+attraction_links[i]
			# 将item和对应链接一同送入下一个解析函数
			yield scrapy.Request(url='http://www.tuniu.com'+attraction_links[i],
			                     meta={'item':item}, callback=self.parseAttraction)

		# 如果当前景点列表页有下一页的话，那么获取下一页的链接并重复调用自身进行解析
		if('下一页' in response.css("div.wrapper div.pagination div.page-bottom a::text").extract()):
			index = response.css("div.wrapper div.pagination div.page-bottom a::text").extract().index('下一页')
			next_page = response.css("div.wrapper div.pagination div.page-bottom").xpath("a/@href").extract()[index]
			yield scrapy.Request(url='http://www.tuniu.com'+next_page,
			                     meta={'area_name':area_name,'area_id':area_id}, callback=self.parseAttractionPage)

	'''
	pasreAttraction(self, response):
		解析景点网站，爬景点地址、评论列表、游玩用时参考和简介
	Author：Yinli
	'''
	def parseAttraction(self, response):
		item = response.meta['item']
		# 如果有景点简介则爬下来保存到item，否则记为NULL
		if(response.css("div#view_bar.details div.coat p.description::text").extract() == []):
			item['introduction'] = 'NULL'
		else:
			item['introduction'] = response.css("div#view_bar.details div.coat p.description::text").extract_first()

		# 如果有地址信息则爬下来保存到item，否则记为NULL
		if ('地址' in response.css("div#view_bar.details div.route div.content").xpath(
				"//div[@class='left']/text()|//div[@class='right']/text()").extract()):
			index = response.css("div#view_bar.details div.route div.content").xpath(
				"//div[@class='left']/text()|//div[@class='right']/text()").extract().index('地址')
			item['address'] = response.css("div#view_bar.details div.route div.content").xpath(
				"//div[@class='left']/text()|//div[@class='right']/text()").extract()[index + 1]
		else:
			item['address'] = 'NULL'

		# 如果有游玩用时参考则爬下来保存到item，否则记为NULL
		if ('游玩用时参考' in response.css("div#view_bar.details div.route div.content").xpath(
				"//div[@class='left']/text()|//div[@class='right']/text()").extract()):
			index = response.css("div#view_bar.details div.route div.content").xpath(
				"//div[@class='left']/text()|//div[@class='right']/text()").extract().index('游玩用时参考')
			item['time_cost'] = response.css("div#view_bar.details div.route div.content").xpath(
				"//div[@class='left']/text()|//div[@class='right']/text()").extract()[index + 1]
		else:
			item['time_cost'] = 'NULL'
		# 将item送去pipeline
		yield item
