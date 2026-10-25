# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
数据恢复脚本：任务三的 D1/D2 删除了借阅记录，为保证任务四/五统计基于完整数据，
重建 borrow_logs 时间序列集合并从数据文件恢复全部 66 条记录
"""
import os

from bson import json_util
from pymongo import MongoClient

import mongodb_connect as conn

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

client = conn.build_client()
db = conn.get_database(client)

# 1) 删除现有 borrow_logs（含时间序列底层桶集合）
db.borrow_logs.drop()
print("==> 已删除现有 borrow_logs 集合")

# 2) 按任务书配置重建时间序列集合（expireAfterSeconds 为顶层选项）
db.create_collection(
    "borrow_logs",
    timeseries={"timeField": "borrow_date", "granularity": "hours"},
    expireAfterSeconds=63072000,
)
print("==> 已按原配置重建 borrow_logs（timeField=borrow_date, granularity=hours, expireAfterSeconds=63072000）")

# 3) 从数据文件重新导入全部记录
with open(os.path.join(PROJECT_ROOT, "data", "borrow_logs.txt"), encoding="utf-8") as f:
    docs = json_util.loads(f.read())
res = db.borrow_logs.insert_many(docs)
print("==> 已恢复 %d 条借阅记录" % len(res.inserted_ids))
print("==> borrow_logs 当前文档数：%d" % db.borrow_logs.count_documents({}))

client.close()
print("恢复完成。")
