# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
图书管理模块：增删改查、条件检索、评分排行
对应任务书 ST-5.3 book_manager.py
"""
import re


def add_book(db, book_doc):
    """新增单本图书，返回插入结果"""
    return db.books.insert_one(book_doc)


def add_books_batch(db, book_docs):
    """批量新增图书（演示用）"""
    return db.books.insert_many(book_docs)


def fetch_by_isbn(db, isbn):
    """按 ISBN 精确查询"""
    return db.books.find_one({"isbn": isbn})


def fetch_by_price_range(db, min_price, max_price):
    """按价格区间查询（含边界）"""
    return list(db.books.find({"price": {"$gte": min_price, "$lte": max_price}}))


def fetch_top_rated(db, limit=5):
    """按评分降序返回前 N 本"""
    return list(db.books.find().sort("rating", -1).limit(limit))


def fetch_by_keyword(db, keyword):
    """按书名关键字模糊检索（$regex，不区分大小写）"""
    pattern = re.compile(keyword, re.IGNORECASE)
    return list(db.books.find({"title": pattern}))


def adjust_stock(db, isbn, delta):
    """调整某本书库存（$inc，delta 可为负）"""
    return db.books.update_one({"isbn": isbn}, {"$inc": {"stock": delta}})


def remove_book(db, isbn):
    """按 ISBN 删除图书"""
    return db.books.delete_one({"isbn": isbn})


def show_all(db):
    """列出全部图书（简略）"""
    return list(db.books.find({}, {"title": 1, "author": 1, "price": 1, "stock": 1}))
