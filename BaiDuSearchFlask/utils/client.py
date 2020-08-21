from utils.settings import *
from pymongo import MongoClient
from scrapyd_api import ScrapydAPI


class ScrapydClient(object):
    def __init__(self):
        self.auth = CLIENT_AUTH
        self.ip = CLIENT_IP
        self.port = CLIENT_PORT
        self.username = CLIENT_USERNAME
        self.password = CLIENT_PWD

    def get_scrapyd(self):
        return ScrapydAPI(f"http://{self.ip}:{self.port}",
                          auth=(self.username, self.password) if self.auth else None)


class MongoDBClient(object):
    def __init__(self):
        client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
        self.db = client[MONGODB_COLLECTION][MONGODB_NAMESPACE]

    def find_all(self, job_id):
        result_list = []
        result_obj = self.db.find({'job_id': job_id})
        for data in result_obj:
            del data['_id']
            result_list.append(data)
        return result_list


scrapyd_client = ScrapydClient()
mongodb_client = MongoDBClient()
