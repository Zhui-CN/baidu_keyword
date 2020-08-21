import time
from BaiDuSearchFlask.utils.client import scrapyd_client
from BaiDuSearchFlask.utils.settings import SPIDER_SCRAPYD_NAME

egg_path = 'BaiDuSearchSpider-1.0-py3.7.egg'
egg_file = open(egg_path, 'rb')
scrapyd = scrapyd_client.get_scrapyd()
scrapyd.add_version(SPIDER_SCRAPYD_NAME, int(time.time()), egg_file.read())
