# -*- coding: utf-8 -*-
# @AuThor  : frank_lee
import pymongo
from pymongo.collection import Collection


class SaveToMongodb(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host="localhost", port=27017)
        self.db_data = self.client['douguo']

    def insert_to_mongo(self, item):
        db_collection = Collection(self.db_data, "meishi")
        db_collection.insert(item)


save_to_mongo = SaveToMongodb()