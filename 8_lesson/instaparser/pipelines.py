from itemadapter import ItemAdapter
from pymongo import MongoClient


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient("127.0.0.1", 27017)
        self.mongobase = client.instagram_30_03

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item
