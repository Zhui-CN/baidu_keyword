# -*- coding: utf-8 -*-

import scrapy
import re
import time
from copy import deepcopy
from BaiDu.utils import get_ip
import asyncio


class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['baidu.com']

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Host": "www.baidu.com",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Referer": "https://www.baidu.com",
        "Sec-Fetch-Dest": "document",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
        # "Cookie": "BIDUPSID=D30CAE60380E271AF108C24D7ADAC643; PSTM=1595388493; BAIDUID=D30CAE60380E271AD9B008260FA6A4D7:FG=1; BD_UPN=12314753; sug=3; sugstore=0; ORIGIN=0; bdime=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; PSINO=6; shifen[6905455_91638]=1597975617; BCLID=11892191315056380902; BDSFRCVID=CdkOJexroG3oaIRrhgobhbA5neKK0gOTDYLEOwXPsp3LGJLVN6Y7EG0PtfOStp0-oxSmogKK0gOTH6KF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoCK5tCvHjtjY-P7Hq4D_MfOtetJyaR3japjvWJ5TMCoLhMoNXPCXMMJGQPva0RTXLP3I2bF5ShPC-tnABPCZbUrabJ3zfIopopbN3l02VMO9e-t2yUoD0N530tRMW20e0h7mWIbUsxA45J7cM4IseboJLfT-0bc4KKJxbnLWeIJIjjCajTcQjGKDq-jeHDrKBRbaHJOoDDvk5Iccy4LbKxnxJ-RKWGrHBn37QRnDED5kbfRvD--g3-OkWUQ9babTQ-tbBp3k8MQ8jlubQfbQ0hOhWhJJ-n4LW-nRaR7JOpkxbUnxy5KUQRPH-Rv92DQMVU52QqcqEIQHQT3m5-5bbN3ut6IDJbKj_D_hfbo5KRopMtOhq4tehHRU-fc9WDTOQJ7Ttb7HOfo4M-JrX4kVLHoXKxnitIv9-pbwBp5cfUnMKn05XM-pXbjwtqFf3mkjbPbDBMOMqKtzhn76ht4syP4jKMRnWnciKfA-b4ncjRcTehoM3xI8LNj405OTbIFO0KJzJCFaMIIxj6KaePDyqx5Ka43tHD7yWCvMapjcOR59K4nnDP4_yJ5HaPbd2Kba5C585lvvhb3O3MOZXMLg5n7Tbb8eBgvZ2UQkJfIbsq0x0bOtXpt3Ka0L2bvgaCOMahkM5h7xOKQoQlPK5JkgMx6MqpQJQeQ-5KQN3KJmfbL9bT3YjjTLjNujtjDDfKresJoq2RbhKROvhjRTb-PgyxoObtRxtKOKaxo-2n3oHRnPLjo_bfPUDMJ9LU3kBgT9LMnx--t58h3_XhjFjlcWQttjQn3hBa7JQItEa-n6DJ7TyU42bU47yaji0q4Hb6b9BJcjfU5MSlcNLTjpQT8r5MDOK5OuJRQ2QJ8BtK02MI3P; BD_HOME=1; H_PS_PSSID=1466_32572_32327_31660_32352_32045_32500_32482; H_PS_645EC=177ca3U6mKPQWlTGCwxzf1g4fVWd9ead7pBIQtHDCTlcNqGwXijhKdIQ6I0; BDSVRTM=0; COOKIE_SESSION=527_2_9_7_46_56_0_4_8_8_143_8_1234_0_525_0_1597976121_1597975026_1597975596%7C9%23315734_27_1597975013%7C5"
    }

    keyword_url = "https://www.baidu.com/s?wd={}&si={}&ct=2190592"
    search_url = "https://www.baidu.com/s?wd={}&ie=utf-8&rn={}&pn={}"

    re_page = re.compile(r'pn=(\d+)')

    def __init__(self, keyword_list, job_id, check_row, pros, *args, **kwargs):
        super(BaiduSpider, self).__init__()
        self.keyword_list = eval(keyword_list) if isinstance(keyword_list, str) else keyword_list
        self.job_id = job_id
        self.check_row = check_row
        self.pros = eval(pros) if isinstance(pros, str) else pros
        self.loop = asyncio.get_event_loop()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        keyword_list = crawler.settings.get("KEYWORD_LIST", [])
        job_id = crawler.settings.get("JOB_ID")
        check_row = int(crawler.settings.get("CHECK_ROW")) if crawler.settings.get("CHECK_ROW") else 10
        pros = crawler.settings.get("PROS", [])
        spider = cls(keyword_list, job_id, check_row, pros, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def start_requests(self):
        if self.pros:
            for pro in self.pros:
                ip_dict = self.loop.run_until_complete(get_ip(pro))
                for keyword_item in self.keyword_list:
                    keywords = keyword_item['keywords']
                    domain = keyword_item['domain']

                    yield scrapy.Request(url=self.keyword_url.format(domain, domain), meta={
                        "keywords": deepcopy(keywords),
                        "domain": deepcopy(domain),
                        "ip_dict": deepcopy(ip_dict),
                        "pro": deepcopy(pro),
                    }, headers=self.headers, dont_filter=True, callback=self.parse)
        else:
            for keyword_item in self.keyword_list:
                keywords = keyword_item['keywords']
                domain = keyword_item['domain']

                yield scrapy.Request(url=self.keyword_url.format(domain, domain), meta={
                    "keywords": deepcopy(keywords),
                    "domain": deepcopy(domain),
                    "ip_dict": deepcopy(None),
                    "pro": deepcopy(None),
                }, headers=self.headers, dont_filter=True, callback=self.parse)

    def parse(self, response, **kwargs):
        item = deepcopy(response.meta)
        if item['ip_dict']:
            item['proxy'] = f"https://{item['ip_dict'].get('IP')}"

        lis = response.xpath('//div[contains(@class, "f13")]')
        item['xzh'] = None
        for li in lis:
            name = li.xpath('./a/span/text()').extract_first()
            if name:
                item['xzh'] = name.strip()
                break

        for keyword in item['keywords']:
            item['keyword'] = keyword
            yield scrapy.Request(url=self.search_url.format(keyword, self.check_row, 0), meta=deepcopy(item),
                                 callback=self.parse_item,
                                 headers=self.headers, dont_filter=True)

    def parse_item(self, response):
        pn_num = int(self.re_page.search(response.url).group(1))
        page = pn_num // self.check_row + 1
        item = deepcopy(response.meta)
        xzh = item['xzh']
        domain = item['domain']
        keyword = item['keyword']
        ip_dict = item['ip_dict']

        domain_min = domain.split(".")[1]
        lis = response.xpath('//div[@tpl="se_com_default"]')
        for rank, li in enumerate(lis):
            name = li.xpath('.//div[contains(@class, "f13")]/a/span/text()').extract_first()
            if name:
                if name.strip() == xzh:
                    web_id = li.xpath('./@id').extract_first()
                    title = ''.join(li.xpath('./h3/a//text()').extract()).strip()
                    yield self.get_items(keyword, domain, self.check_row, page, rank + 1, xzh, response.url, title,
                                         ip_dict, web_id)
                    return
            else:
                url = li.xpath('.//div[contains(@class, "f13")]/a[contains(@class, "c-showurl")]//text()').extract()
                if url:
                    if domain_min in "".join(url).strip():
                        web_id = li.xpath('./@id').extract_first()
                        title = ''.join(li.xpath('./h3/a//text()').extract()).strip()
                        yield self.get_items(keyword, domain, self.check_row, page, rank + 1, xzh, response.url, title,
                                             ip_dict, web_id)
                        return

        next_page = None
        if self.check_row == 10:
            if page < 10:
                next_page = self.search_url.format(keyword, self.check_row, pn_num + 10)
            else:
                item, next_page = self.is_retry(item)
                if not next_page:
                    yield self.get_items(keyword, domain, self.check_row, page, None, xzh, response.url, None, ip_dict,
                                         None)
                    return

        elif self.check_row == 50:
            if page < 2:
                next_page = self.search_url.format(keyword, self.check_row, pn_num + 50)
            else:
                item, next_page = self.is_retry(item)
                if not next_page:
                    yield self.get_items(keyword, domain, self.check_row, page, None, xzh, response.url, None, ip_dict,
                                         None)
                    return

        yield scrapy.Request(url=response.urljoin(next_page),
                             meta=deepcopy(item), callback=self.parse_item,
                             dont_filter=True, headers=self.headers)

    def is_retry(self, item):
        # TODO 暂时无可用ip, 不使用重试
        if self.pros:
            retry_http = item.get('retry_http', 0)
            if retry_http == 0 or retry_http < 5:
                ip_dict = self.loop.run_until_complete(get_ip(item['pro']))
                item['ip_dict'] = ip_dict
                item['retry_http'] = 1 if retry_http is None else retry_http + 1
                item['proxy'] = f"https://{item['ip_dict'].get('IP')}"
                next_page = self.search_url.format(item['keyword'], self.check_row, 0)
                return item, next_page
        return item, False

    def get_items(self, *args):
        items = {}
        items['keyword'] = args[0]
        items['domain'] = args[1]
        items['check_row'] = args[2]
        items['page_numb'] = args[3]
        items['rank'] = args[4]
        items['xzh'] = args[5]
        items['response_url'] = args[6]
        items['title'] = args[7]
        items['ip'] = args[8].get("IP") if args[8] else None
        items['address'] = args[8].get("IpAddress") if args[8] else None
        items['web_id'] = args[9]
        items['job_id'] = self.job_id
        items['query_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return items


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute("scrapy crawl baidu".split())
