# -*- coding: utf-8 -*-

import json
import logging
import time

import requests

from ..items import *


class board(scrapy.Spider):
    # init parameters
    name = 'board'
    allowed_domains = ['pinterest.com']  # crawling sites
    handle_httpstatus_list = [418]  # http status code for not ignoring

    def __init__(self, source_url, page=3, *args, **kwargs):
        super(board, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.pinterest.com/resource/BoardFeedResource/get/']
        self.__board_url = 'https://www.pinterest.com/resource/BoardResource/get/'
        self.__source_url = source_url
        self.__board_id = 0
        self.__board_api = {'api_0': '?source_url=',
                            'api_1': '&data=',
                            'api_2': '&_='
                            }
        self.__weibo_page_range = int(page)

    def start_requests(self):
        split = self.__source_url.split('/')
        self.__board_id = self.get_board_id(split[1], split[2])

        board_url = self.gen_url(None)
        yield scrapy.Request(url=board_url, callback=self.parse_board, meta={'bookmark': ''})

    def get_board_id(self, username, slug):
        options = {
            'field_set_key': 'profile_grid_item',
            'is_mobile_fork': True,
            'username': username,
            'slug': slug,
            'no_fetch_context_on_resource': False
        }
        data = {'options': options, 'context': {}}

        url = self.__board_url + \
              self.__board_api['api_0'] + self.__source_url + \
              self.__board_api['api_1'] + json.dumps(data) + \
              self.__board_api['api_2'] + str(int(time.time()) * 1000)

        logging.info(url)

        response = requests.get(url)

        res_obj = json.loads(response.content)
        return res_obj['resource_response']['data']['id']

    def gen_url(self, bookmarks):
        options = {
            'add_vase': False,
            'board_id': self.__board_id,
            'field_set_key': 'react_grid_pin',
            'filter_section_pins': True,
            'is_react': True,
            'prepend': False,
            'no_fetch_context_on_resource': False
        }
        if bookmarks is not None and bookmarks != '':
            options['bookmarks'] = [bookmarks]

        data = {'options': options, 'context': {}}

        url = self.start_urls[0] + \
              self.__board_api['api_0'] + self.__source_url + \
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

        datas = resource_response.get('data')
        for data in datas:
            type = data['type']
            if type != 'pin':
                continue

            pin_item = PinItem()
            pin_item['pin'] = data
            yield pin_item
