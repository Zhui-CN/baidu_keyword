# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from twisted.internet.threads import deferToThread


class MongoDBPipeline(object):
    def __init__(self, db):
        self.db = db

    @classmethod
    def from_settings(cls, settings):
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        db_name = settings["MONGODB_DBNAME"]
        db_table = settings["MONGODB_TABLE"]
        client = MongoClient(host=host, port=port)
        db = client[db_name][db_table]
        return cls(db)

    def _process_item(self, item, spider):
        data = dict(item)
        self.db.update_one({
            'keyword': data.get('keyword'),
            'domain': data.get('domain'),
            'ip': data.get('ip')}, {'$set': data}, True)

        return item

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)
