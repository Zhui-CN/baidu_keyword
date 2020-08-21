# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
from BaiDu.utils import get_ip


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            print('Got exception: %s' % exception)
            # 随意封装一个response，返回给spider
            retry_numb = request.meta.get('retry_numb', 0)
            if retry_numb == 0 or retry_numb < 5:
                if request.meta.get('pro'):
                    ip_dict = spider.loop.run_until_complete(get_ip(request.meta['pro']))
                    request.meta['ip_dict'] = ip_dict
                    request.meta['proxy'] = f"https://{ip_dict.get('IP')}"
                request.meta['retry_numb'] = 1 if retry_numb is None else retry_numb + 1
                return request
            else:
                raise Exception('Got exception: %s' % exception)
        # 打印出未捕获到的异常
        print('not contained exception: %s' % exception)
