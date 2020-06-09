import pymongo
from pymongo.collection import Collection


class Cnonnect_mongo(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.client.admin.authenticate('admin', "abc123456")

        self.dbdata = self.client['douguomeishi']

    def insert_item(self, item):
        db_collection = Collection(self.dbdata, 'douguo_item')
        db_collection.insert_many(item)


mongo_info = Cnonnect_mongo()
