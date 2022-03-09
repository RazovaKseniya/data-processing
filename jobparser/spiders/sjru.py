import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@class, 'icMQ_ bs_sM _3ze9n l9LnJ f-test-button-dalshe f-test-link-Dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//span[contains(@class, '_3a-0Y _3DjcL _3sM6i')]//a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("//span[contains(@class, '_2Wp8I _3a-0Y _3DjcL _3fXVo')]/text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)