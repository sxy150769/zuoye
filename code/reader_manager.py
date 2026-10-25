# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
读者管理模块：读者信息管理、学院统计、等级分布
对应任务书 ST-5.3 reader_manager.py
"""
from datetime import datetime


def list_all(db):
    """返回全部读者（不展示注册时间细节）"""
    return list(db.readers.find({}, {"card_no": 1, "name": 1, "college": 1, "level": 1}))


def count_by_college(db):
    """按学院统计读者人数（aggregate）"""
    return list(
        db.readers.aggregate(
            [{"$group": {"_id": "$college", "人数": {"$sum": 1}}}, {"$sort": {"人数": -1}}]
        )
    )


def count_by_level(db):
    """按借阅等级统计读者人数"""
    return list(
        db.readers.aggregate(
            [{"$group": {"_id": "$level", "人数": {"$sum": 1}}}, {"$sort": {"_id": 1}}]
        )
    )


def distinct_colleges(db):
    """返回去重后的学院清单（distinct）"""
    return db.readers.distinct("college")


def add_reader(db, reader_doc):
    """新增读者"""
    if "register_date" not in reader_doc:
        reader_doc["register_date"] = datetime.utcnow()
    return db.readers.insert_one(reader_doc)


def find_by_card(db, card_no):
    """按借阅证号查询读者"""
    return db.readers.find_one({"card_no": card_no})
