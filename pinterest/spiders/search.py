# -*- coding: utf-8 -*-

import json
import logging
import time

import requests

from ..items import *


class board(scrapy.Spider):
    # init parameters
    name = 'search'
    allowed_domains = ['pinterest.com']  # crawling sites
    handle_httpstatus_list = [418]  # http status code for not ignoring

    def __init__(self, query, page=3, *args, **kwargs):
        super(board, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.pinterest.com/resource/BaseSearchResource/get/']
        self.__query = query
        self.__board_api = {'api_0': '?source_url=/search/pins/?rs=typed&q=',
                            'api_1': '&data=',
                            'api_2': '&_='
                            }
        self.__weibo_page_range = int(page)

    def start_requests(self):
        board_url = self.gen_url(None)
        yield scrapy.Request(url=board_url, callback=self.parse_board, meta={'bookmark': ''})

    def gen_url(self, bookmarks):
        options = {
            'article': '',
            'appliedProductFilters': '---',
            'query': self.__query,
            'scope': 'pins',
            'top_pin_id': '',
            'filters': '',
            'no_fetch_context_on_resource': False
        }
        if bookmarks is not None and bookmarks != '':
            options['bookmarks'] = [bookmarks]

        data = {'options': options, 'context': {}}

        url = self.start_urls[0] + \
              self.__board_api['api_0'] + self.__query.replace(' ', '+') + \
              self.__board_api['api_1'] + json.dumps(data) + \
              self.__board_api['api_2'] + str(int(time.time()) * 1000)

        logging.info(url)

        return url

    def parse_board(self, response):
        resource_info = json.loads(response.text)
        resource_response = resource_info['resource_response']

        bookmark = resource_response.get('bookmark')

        logging.info(bookmark)

        if bookmark is not None and bookmark != '':
            yield scrapy.Request(url=self.gen_url(bookmark), callback=self.parse_board, meta={'bookmark': bookmark})

        datas = resource_response['data']['results']
        for data in datas:
            type = data['type']
            if type != 'pin':
                continue

            pin_item = PinItem()
            pin_item['pin'] = data
            yield pin_item
