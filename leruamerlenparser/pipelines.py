# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import hashlib
from scrapy.utils.python import to_bytes

class LeruamerlenparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.leroymerlin_14_03

    def process_item(self, item, spider):
        collections = self.mongobase[spider.name]
        collections.insert_one(item)
        return item

class LeroyMerlinPhotosPipeline(ImagesPipeline):
        def get_media_requests(self, item, info):
            if item['photos']:
                for photo in item['photos']:
                    try:
                        yield scrapy.Request(photo)
                    except Exception as e:
                        print(e)

        def item_completed(self, results, item, info):
            item['photos'] = [itm[1] for itm in results if itm[0]]
            return item

        def file_path(self, request, response=None, info=None, *, item=None):
            photos_dir = item['name'].replace('/', '_')
            image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
            return f'full/{photos_dir}/{image_guid}.jpeg'