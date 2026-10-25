# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
借阅管理模块：借阅登记、归还处理、逾期查询
对应任务书 ST-5.3 borrow_manager.py

重要说明：borrow_logs 为时间序列集合且未定义 metaField，MongoDB 不允许对其执行
update 操作（错误码 72）。因此归还处理采用「删除借出记录 + 插入已归还记录」的
等价实现，同时用 update_many 更新 books 库存（回库 +1）。
"""
from datetime import datetime, timedelta


def register_borrow(db, card_no, isbn):
    """借阅登记：向 borrow_logs 插入一条借出记录"""
    doc = {
        "borrow_date": datetime.now(),
        "reader_card": card_no,
        "book_isbn": isbn,
        "status": "借出",
    }
    return db.borrow_logs.insert_one(doc)


def handle_return(db, card_no, isbn):
    """归还处理：删除对应借出记录并插入已归还记录，同时 books 库存 +1"""
    deleted = db.borrow_logs.delete_many(
        {"reader_card": card_no, "book_isbn": isbn, "status": "借出"}
    )
    if deleted.deleted_count == 0:
        return None  # 没有找到可归还的借出记录

    db.borrow_logs.insert_one(
        {
            "borrow_date": datetime.now() - timedelta(days=14),
            "return_date": datetime.now(),
            "reader_card": card_no,
            "book_isbn": isbn,
            "status": "已归还",
        }
    )
    # 图书回库：库存 +1（update_many 的常规用法）
    db.books.update_many({"isbn": isbn}, {"$inc": {"stock": 1}})
    return deleted


def show_overdue(db):
    """逾期查询：状态为逾期的借阅记录"""
    return list(db.borrow_logs.find({"status": "逾期"}))
