# -*- coding: utf-8 -*-

import pymongo
import pymysql


class DBConnector:
    def __init__(self):
        # 重写该类或者填充本地数据库配置信息
        self.mongo_uri = ""
        self.mongo_database = ""
        self.mongo_user_name = ''
        self.mongo_pass_wd = ""

        self.mysql_uri = ""
        self.mysql_database = ""
        self.mysql_username = ""
        self.mysql_password = ""

    def create_mongo_connection(self):
        client = pymongo.MongoClient(self.mongo_uri)
        database = client[self.mongo_database]
        database.authenticate(self.mongo_user_name, self.mongo_pass_wd)
        return database, client

    def create_mysql_connection(self):
        db = pymysql.connect(host=self.mysql_uri,
                             user=self.mysql_username,
                             password=self.mysql_password,
                             database=self.mysql_database,
                             charset='utf8mb4')
        return db
