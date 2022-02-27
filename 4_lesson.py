from pprint import pprint
import requests
from lxml import html
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)

db = client['news']
lenta_ru = db.lenta_ru

url = 'https://lenta.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)

news_blocks = dom.xpath("//a[contains(@class, '_topnews')]")

for news in news_blocks:
    doc = {}
    name_news = news.xpath(".//h3[contains(@class, 'card-big__title')]/text() | //span[contains(@class, 'card-mini__title')]/text()")[0]
    link_news = news.xpath(".//a[contains(@class, 'card-big _topnews')]/@href | //a[contains(@class, 'card-mini _topnews')]/@href")
    link_source = url + str(link_news[0])
    time = news.xpath(".//time[contains(@class, 'card-big__date')]/text() | //time[contains(@class, 'card-mini__date')]/text()")[0]

    doc['Name'] = name_news
    doc['Link'] = link_source
    doc['Time'] = time

lenta_ru.update_one(doc, {'$set': doc}, upsert=True)

for doc in lenta_ru.find({}):
    pprint(doc)
