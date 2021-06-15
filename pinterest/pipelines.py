# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import time
from .items import *
from .database_tool import DBConnector
from scrapy.exceptions import DropItem
from pymongo.errors import DuplicateKeyError
import json


class PinterestPipeline(object):

    def __init__(self):
        # to check the __uid from TotalNumItem, means just need to save one item and drop others
        db_connector = DBConnector()
        self.__hash_uid_list = []
        # self.db, self.client = db_connector.create_mongo_connection()
        self.db = db_connector.create_mysql_connection()

    def get_crawled_time(self):
        return time.strftime("Crawled time: %Y-%m-%d %H:%M:%S")

    def close_spider(self, spider):
        # self.client.close()
        self.db.close()

    def process_item(self, item, spider):
        try:
            crawled_time = self.get_crawled_time()
            if isinstance(item, PinItem):
                images = item['pin']['images']
                orig = images.get('orig')
                x736 = images.get('736x')

                id = item['pin']['id']
                videos = item['pin']['videos']
                author_id = item['pin']['pinner']['id']
                verified = item['pin']['pinner']['verified_identity'].get('verified')
                content = item['pin']['grid_title']

                type = 2
                if videos is not None:
                    type = 3

                # logging.info('uid: ' + str(author_id) + ', id: ' + str(id) + ', type: ' + str(type))

                # 非图跳过
                if type != 2:
                    return item

                # 推广跳过
                if verified is not None and verified:
                    return item

                images = []
                if orig is None:
                    images.append(x736['url'])
                else:
                    images.append(orig['url'])

                with self.db.cursor() as cursor:
                    sql = "insert into crawl_post(source, origin_id, type, author_id, pub_time, origin, origin_images, origin_content, origin_video) " \
                          "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    try:
                        cursor.execute(sql, (2, id, type, author_id, '0000-00-00 00:00:00',
                                             json.dumps(item['pin']), json.dumps(images), content, ''))
                    except DuplicateKeyError:
                        logging.info('duplicate key')
                self.db.commit()

                return item

        except BaseException as e:
            logging.info(e)
            raise DropItem
