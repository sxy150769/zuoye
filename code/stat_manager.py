# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
统计模块：分类统计、借阅趋势、畅销榜（全部使用聚合管道）
对应任务书 ST-5.4
"""
from datetime import datetime


def category_summary(db):
    """分类统计：按类别分组统计库存总量、平均价格、图书数量，按库存总量降序"""
    return list(
        db.books.aggregate(
            [
                {
                    "$group": {
                        "_id": "$category",
                        "库存总量": {"$sum": "$stock"},
                        "平均价格": {"$avg": "$price"},
                        "图书数量": {"$sum": 1},
                    }
                },
                {"$sort": {"库存总量": -1}},
                {"$project": {"_id": 1, "库存总量": 1, "平均价格": {"$round": ["$平均价格", 2]}, "图书数量": 1}},
            ]
        )
    )


def yearly_trend(db):
    """借阅趋势：按年份分组统计借阅量，格式化为「2026年」"""
    return list(
        db.borrow_logs.aggregate(
            [
                {
                    "$group": {
                        "_id": {
                            "年": {"$year": "$borrow_date"},
                            "文本": {"$dateToString": {"format": "%Y年", "date": "$borrow_date"}},
                        },
                        "借阅量": {"$sum": 1},
                    }
                },
                {"$sort": {"_id.年": 1}},
            ]
        )
    )


def bestseller(db):
    """畅销榜：借阅次数最多的图书"""
    return list(
        db.books.aggregate(
            [
                {"$sort": {"borrow_count": -1}},
                {"$limit": 3},
                {"$project": {"_id": 0, "title": 1, "borrow_count": 1, "price": 1}},
            ]
        )
    )


def current_ts():
    """当前时间（用于日志展示）"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
