# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose

def price_processed(price_list):
    try:
        result = int(price_list[0].replace(' ',''))
        return result
    except:
        return price_list

def characteristics_processed(characteristics):
    char_dict = characteristics[0]
    for k, v in char_dict.items():
        result = v.replace('\n', '')
        res = result.replace('\n', '')
        try:
            char_dict[k] = float(res)
        except:
            char_dict[k] = res
    return char_dict

class LeruamerlenparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(price_processed))
    currency = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    characteristics = scrapy.Field(input_processor=Compose(characteristics_processed))
    _id = scrapy.Field()
