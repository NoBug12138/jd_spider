# -*- coding: utf-8 -*-
import json
import re
import scrapy
from jd_spider.items import JdSpiderItem


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com', '3.cn']
    start_urls = ['https://list.jd.com/list.html?cat=9987,653,655']

    def parse(self, response):

        # 获取详情页url
        url_list = response.xpath('//li[@class="gl-item"]//div[@class="p-name"]/a/@href').extract()
        print(url_list)

        # 获取详情页URL
        for detail_url in url_list:

            yield scrapy.Request(
                url='https:' + detail_url,
                callback=self.detail_parse
            )

        # 获取下一页URL
        next_url = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_url is not None:
            next_url = "https://list.jd.com" + next_url
            yield scrapy.Request(
                url=next_url,
                callback=self.parse
            )

    # 获取详情页所有分类的URL
    def detail_parse(self, response):

        script = response.xpath('//script[@charset="gbk"]/text()').extract()
        classify_list = re.findall(r'colorSize\:(.*)', script[0])
        goods_content = classify_list[0].split('[')[1].split(']')[0]
        skuid_list = re.findall(r'\"skuId\"\:(\d+)', goods_content)
        for skuid in skuid_list:

            # 构建新的请求,请求价格
            yield scrapy.Request(
                url= 'https://item.jd.com/'+ skuid +'.html',
                callback=self.detail_result_parse,
                meta={
                    'skuid':skuid
                }
            )

    # 获取商品标题
    def detail_result_parse(self, response):

        skuid = response.meta['skuid']
        name = response.xpath('//title/text()').extract_first()
        price_url = "https://p.3.cn/prices/mgets?skuIds=J_" + skuid

        yield scrapy.Request(
            url=price_url,
            callback=self.price_parse,
            meta={
                'name':name
            }
        )

    # 解析价格
    def price_parse(self, response):

        result = json.loads(response.text)
        price = result[0]["p"]
        cellphone = JdSpiderItem()
        cellphone["name"] = response.meta['name']
        cellphone["price"] = price
        yield cellphone


