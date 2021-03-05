import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NyhederItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class NyhederSpider(scrapy.Spider):
	name = 'nyheder'
	start_urls = ['https://www.vestjyskbank.dk/om-banken/nyheder']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//h4/text()').get()
		title = response.xpath('//div[@class="p p-imagetext col-12"]/h1/text()').get()
		if not title:
			title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="p p-imagetext col-12"]//following-sibling::p//text()').getall()
		if not content:
			content = response.xpath('//div[@class="p mb-3 p-imagetext p-width-auto p-imagetext-tb"]/div[@class="row"]/div[@class="p-txt-container col-12"]//text()[not (ancestor::h1) and not (ancestor::h4)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NyhederItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
