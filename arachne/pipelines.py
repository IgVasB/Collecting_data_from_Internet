# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from hashlib import md5
from arachne.items import ArachneItem
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class ArachnePipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client['labirint_books']

    def process_item(self, item: ArachneItem, spider):
        if spider.name == 'labirint':
            insert_item = self.process_labirint(item)

        # Добавляем словарь в MongoDB
        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(insert_item)
        except DuplicateKeyError:
            print('Already exists!')

        return item

    def process_labirint(self, item: ArachneItem):
        # Меняем значиния на числовые
        if item['price']:
            item['price'] = float(item['price'])
        if item['discount_price']:
            item['discount_price'] = float(item['discount_price'])
        if item['rating']:
            item['rating'] = float(item['rating'])

        # Создаем словарь для генерации id через хэш функию
        item_dict = dict(item)
        # Генерируем id
        hash_id = md5(str(item_dict).encode('utf-8'))
        # Добавляем поле _id в словарь
        item['_id'] = hash_id.hexdigest()

        return item