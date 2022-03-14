import scrapy
from scrapy.http import HtmlResponse
from leruamerlenparser.items import LeruamerlenparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f"https://leroymerlin.ru/search/?q={kwargs.get('search')}/"]


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@data-qa-pagination-item, 'right')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[contains(@data-qa, 'product-name')]")
        for link in links:
            yield response.follow(link, callback=self.parse_ler)

    def parse_ler(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruamerlenparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('currency', "//span[@slot='currency']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('photos', "//picture[@slot='pictures']/source[contains(@media, '1024px')]/@srcset")

        characteristics_key = response.xpath('//dt/text()').getall()
        characteristics_value = response.xpath('//dd/text()').getall()
        characteristics = dict(zip(characteristics_key, characteristics_value))
        loader.add_value('characteristics', characteristics)

        yield loader.load_item()

        # name = response.xpath("//h1/text()").get()
        # price = response.xpath("//span[@slot='price']/text()").get()
        # currency = response.xpath("//span[@slot='currency']/text()").get()
        # url = response.url
        # photos = response.xpath("//picture[@slot='pictures']/source[contains(@media, '1024px')]/@srcset").getall()
        # yield LeruamerlenparserItem(name=name, price=price, currency=currency, url=url)

