# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os
import re
import time
import json
import random
import logging

import requests as requests
from fake_useragent import UserAgent
from scrapy import signals
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


# to add random user-agent for every request
# to add random proxy IP address for every request
from scrapy.http import HtmlResponse
from scrapy.xlib.tx import ResponseFailed
from twisted.internet import defer
from twisted.internet.error import TCPTimedOutError, ConnectionDone, ConnectError, DNSLookupError, ConnectionLost


class RandomUaAndProxyIpMiddleware(UserAgentMiddleware):
    def __init__(self, ua, ip_num, api):
        super(UserAgentMiddleware, self).__init__()
        self.ua = ua
        self.api = api
        self.ip_num = ip_num

    @classmethod
    def from_crawler(cls, crawler):
        api = crawler.settings.get('PROXY_API')  # api to get proxy ip address, usually an url
        ip_num = int(re.findall(r'count=\d+', api)[0][6:])  # number of the proxy ip getting from url
        s = cls(ua=UserAgent(), ip_num=ip_num, api=api)
        return s

    @staticmethod
    def get_proxy_ip(ip_num):
        # rewrite your own method for getting proxy ip address

        # rad_index = random.randint(1, ip_num)
        # file_path_dir = os.path.join(os.path.dirname(os.getcwd() + os.path.sep + '..'), 'proxy_utils\\proxy\\')
        # file_path = os.path.join(file_path_dir, f"{str(rad_index)}.temp")
        # with open(file_path, 'r') as file:
        #     for line in file:
        #         proxy_ip = line.split(':')
        # proxy = f'https://{proxy_ip[0]}:{proxy_ip[1]}'
        # return proxy
        # return None

        proxy = requests.get("http://127.0.0.1:5010/get/").json().get('proxy')
        print('proxy: ' + proxy)
        return proxy

    def process_request(self, request, spider):
        # proxy = RandomUaAndProxyIpMiddleware.get_proxy_ip(self.ip_num)
        # request.meta['proxy'] = proxy
        request.headers['User-agent'] = self.ua.random


# to solve crawling failed
class RetryMiddleware(object):

    def __init__(self, ip_num, retry_time=3):
        self.retry_time = retry_time
        self.ua = UserAgent()
        self.__err_count = {}  # request error times
        self.ip_num = ip_num

    @classmethod
    def from_crawler(cls, crawler):
        api = crawler.settings.get('PROXY_API')
        ip_num = int(re.findall(r'count=\d+', api)[0][6:])
        s = cls(ip_num=ip_num)
        return s

    def process_response(self, request, response, spider):
        # 捕获状态码为40x/50x的response
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            # 随意封装，直接返回response，spider代码中根据url==''来处理response
            response = HtmlResponse(url='')
            return response
        # 其他状态码不处理
        return response

        # if response.status == 418:
        #     # receive http status code 418, resend this request
        #     url_hash = hash(request.url)
        #     # to count the recrawling times for each request
        #     if url_hash not in self.__err_count.keys():
        #         self.__err_count[url_hash] = 0
        #     else:
        #         self.__err_count[url_hash] += 1
        #     # to resend this request and change the ua and proxy ip
        #     if self.__err_count[url_hash] < self.retry_time:
        #         request.headers['User-agent'] = self.ua.random
        #         # add proxy for the new request
        #         # proxy = RandomUaAndProxyIpMiddleware.get_proxy_ip(self.ip_num)
        #         # request.meta['proxy'] = proxy
        #         logging.log(msg=time.strftime("%Y-%m-%d %H:%M:%S [RetryMiddleware] ")
        #                     + spider.name + ": restart crawl url:" + response.url, level=logging.INFO)
        #         return request
        #     else:
        #         # raise error IgnoreRequest to drop this request
        #         logging.log(msg=time.strftime("%Y-%m-%d %H:%M:%S [RetryMiddleware] ")
        #                     + spider.name + ": drop request by maximum retry, url:" + response.url, level=logging.INFO)
        #         raise IgnoreRequest
        # else:
        #     try:
        #         parse_json = json.loads(response.text)
        #         if parse_json['ok'] == 0:
        #             # crawl empty json string
        #             # drop this request
        #             logging.log(msg=time.strftime("%Y-%m-%d %H:%M:%S [RetryMiddleware] ")
        #                         + spider.name + ": drop request by empty json, url:" + response.url, level=logging.INFO)
        #             raise IgnoreRequest
        #         else:
        #             # request.meta['parse_json'] = parse_json
        #             return response
        #     except json.JSONDecodeError:
        #         # error when json string decoding, drop this request
        #         if "<!DOCTYPE html>" in response.text:
        #             # crawled string is a html file
        #             return response
        #         else:
        #             logging.log(msg=time.strftime("%Y-%m-%d %H:%M:%S [RetryMiddleware] ")
        #                         + spider.name + ": drop request by json decoding error, url:"
        #                         + response.url, level=logging.INFO)
        #             raise IgnoreRequest

    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            logging.info('Got exception: %s' % (exception))
            # 随意封装一个response，返回给spider
            response = HtmlResponse(url='exception')
            return response
        # 打印出未捕获到的异常
        logging.info('not contained exception: %s' % exception)
