# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
数据库连接模块：统一封装 MongoClient 连接逻辑，供其他模块调用
对应任务书 ST-5.2
"""
from urllib.parse import quote_plus

from pymongo import MongoClient

# 连接参数统一定义在本模块内
HOST = "127.0.0.1"
PORT = 27017
DB_NAME = "library"

# 读写账号（连接时以 URI 方式认证；密码中的特殊字符需 URL 编码）
USERNAME = "libWriter"
PASSWORD = "LibWriter@2026"


def build_client():
    """构造并返回 MongoClient（默认使用读写账号认证，认证库为 library）"""
    safe_pwd = quote_plus(PASSWORD)
    uri = "mongodb://%s:%s@%s:%d/?authSource=%s" % (USERNAME, safe_pwd, HOST, PORT, DB_NAME)
    return MongoClient(uri)


def get_database(client):
    """从 client 取出业务数据库"""
    return client[DB_NAME]
