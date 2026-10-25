# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
数据导出：任务六 ST-6.3
- 导出 category_stats 集合数据文件
- 导出全部 books 集合数据（含全部字段）
- 附：导出集合清单信息
"""
import json
import os

from bson import json_util

import mongodb_connect as conn

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_ROOT, "导出数据")
os.makedirs(OUT_DIR, exist_ok=True)

client = conn.build_client()
db = conn.get_database(client)


def dump_json(name, docs):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json_util.dumps(docs, ensure_ascii=False, indent=2))
    print("已导出 %s：%d 条 -> %s" % (name, len(docs), path))


if __name__ == "__main__":
    dump_json("category_stats.json", list(db.category_stats.find().sort("_id", 1)))
    dump_json("books.json", list(db.books.find()))

    info = {
        "导出时间": "2026-10-25",
        "数据库": "library",
        "集合清单": [
            {"name": n, "count": db[n].count_documents({}), "type": "业务集合"}
            for n in db.list_collection_names()
            if not n.startswith("system.")
        ],
    }
    with open(os.path.join(OUT_DIR, "collections_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print("已导出 collections_info.json")

    client.close()
    print("数据导出完成。")
