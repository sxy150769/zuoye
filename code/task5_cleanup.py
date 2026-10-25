# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
演示后清理恢复：将库恢复到「初始数据 + 完整索引」的干净交付状态
- books：重新导入 20 条，重建视图 book_in_stock，重建 5 个索引
- borrow_logs：按原配置重建时间序列集合并恢复 66 条
"""
import os

from bson import json_util

import mongodb_connect as conn

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

client = conn.build_client()
db = conn.get_database(client)


def load(filename):
    with open(os.path.join(DATA_DIR, filename), encoding="utf-8") as f:
        return json_util.loads(f.read())


# 1) books 恢复
db.books.drop()
books = load("books.txt")
db.books.insert_one(books[0])
db.books.insert_many(books[1:])
print("==> books 重新导入 %d 条" % db.books.count_documents({}))

# 2) 视图重建（PyMongo 4.x 通过 command 创建视图）
db.command({"drop": "book_in_stock"})
db.command({"create": "book_in_stock", "viewOn": "books", "pipeline": [{"$match": {"stock": {"$gt": 0}}}]})
print("==> 视图 book_in_stock 重建，当前 %d 条" % db.book_in_stock.count_documents({}))

# 3) 索引重建
db.books.create_index([("isbn", 1)], unique=True, name="idx_isbn_unique")
db.books.create_index([("title", 1)], name="idx_title")
db.books.create_index([("category", 1)], name="idx_category")
db.books.create_index([("tags", 1)], name="idx_tags_multikey")
db.books.create_index([("category", 1), ("price", 1)], name="idx_category_price")
print("==> books 索引重建完成：%d 个" % len(list(db.books.list_indexes())))

# 4) borrow_logs 恢复
db.borrow_logs.drop()
db.create_collection(
    "borrow_logs",
    timeseries={"timeField": "borrow_date", "granularity": "hours"},
    expireAfterSeconds=63072000,
)
logs = load("borrow_logs.txt")
db.borrow_logs.insert_many(logs)
print("==> borrow_logs 恢复 %d 条" % db.borrow_logs.count_documents({}))

# 5) 终态核对
print("\n===== 清理后终态核对 =====")
for name in ("books", "readers", "borrow_logs", "category_stats"):
    print("  %-16s -> %d 条" % (name, db[name].count_documents({})))
print("  视图 book_in_stock    -> %d 条" % db.book_in_stock.count_documents({}))
print("  books 索引            -> %s" % ", ".join(sorted(i["name"] for i in db.books.list_indexes())))

client.close()
print("\n清理恢复完成。")
