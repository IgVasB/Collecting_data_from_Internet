import scrapy
from scrapy.http import HtmlResponse
from arachne.items import ArachneItem
from scrapy.loader import ItemLoader


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']

#  Обеспечиваем передачу данных в паук для поиска
    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f"https://www.castorama.ru/catalogsearch/result/?q={kwargs.get('query')}"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class='product-card__name ga-product-card-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=ArachneItem(), response=response)
        loader.add_xpath('name', "//h1[@class='product-essential__name hide-max-small']/text()")
        loader.add_xpath('price', "//span[@class='price']//text()")
        loader.add_xpath('photos', "//img[contains(@class,'top-slide__img')]/@data-src")
        loader.add_value('url', response.url)
        yield loader.load_item()