# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
任务二 · 数据填充：将 books.txt / readers.txt / borrow_logs.txt 导入 library 库
对应任务书 ST-2.3：insertOne 单独录入一条图书 + insertMany 批量录入其余数据
"""
import os

from bson import json_util
from pymongo import MongoClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["library"]


def read_records(filename):
    """读取 Extended JSON v2 数组文件"""
    path = os.path.join(DATA_FOLDER, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json_util.loads(f.read())


def fill_books():
    print("==> 图书数据开始录入")
    docs = read_records("books.txt")
    print("    数据文件共 %d 条" % len(docs))
    head, tail = docs[0], docs[1:]

    res1 = db.books.insert_one(head)
    print("    insert_one 录入第 1 条，返回 _id = %s" % res1.inserted_id)

    res2 = db.books.insert_many(tail)
    print("    insert_many 批量录入 %d 条" % len(res2.inserted_ids))
    print("    books 集合当前文档数 = %d" % db.books.count_documents({}))


def fill_readers():
    print("==> 读者数据开始录入")
    docs = read_records("readers.txt")
    res = db.readers.insert_many(docs)
    print("    insert_many 批量录入 %d 条" % len(res.inserted_ids))
    print("    readers 集合当前文档数 = %d" % db.readers.count_documents({}))


def fill_borrow_logs():
    print("==> 借阅流水开始录入（时间序列集合）")
    docs = read_records("borrow_logs.txt")
    res = db.borrow_logs.insert_many(docs)
    print("    insert_many 批量录入 %d 条" % len(res.inserted_ids))
    print("    borrow_logs 集合当前文档数 = %d" % db.borrow_logs.count_documents({}))


if __name__ == "__main__":
    fill_books()
    fill_readers()
    fill_borrow_logs()

    print("\n===== 各集合文档数量核对 =====")
    for name in ("books", "readers", "borrow_logs", "book_logs", "category_stats"):
        print("  %-16s -> %d 条" % (name, db[name].count_documents({})))
    print("  视图 book_in_stock    -> %d 条" % db["book_in_stock"].count_documents({}))
    client.close()
    print("\n数据填充完成，连接已关闭。")
