# -*- coding: utf-8 -*-
"""
实训项目（版本2）· 图书情报检索与统计平台
主程序：菜单式交互命令行应用，串联各功能模块
对应任务书 ST-5.5：启动打印连接状态与集合文档总数；≥8 项功能；变更打印受影响文档数；
查询无结果给出提示；退出前关闭连接
"""
import sys

import mongodb_connect as conn
import book_manager as book_mgr
import reader_manager as reader_mgr
import borrow_manager as borrow_mgr
import stat_manager as stat_mgr


def show_menu():
    print("\n" + "=" * 54)
    print("  图书情报检索与统计平台 · 主菜单（版本2）")
    print("=" * 54)
    items = [
        ("1", "录入图书（单本）"),
        ("2", "批量导入图书（演示数据）"),
        ("3", "按 ISBN 精确查询"),
        ("4", "按价格区间查询"),
        ("5", "评分排行榜 TOP5"),
        ("6", "按书名关键字检索"),
        ("7", "调整图书库存"),
        ("8", "删除图书"),
        ("9", "查看全部读者"),
        ("10", "学院读者统计"),
        ("11", "读者等级分布"),
        ("12", "借阅登记"),
        ("13", "图书归还"),
        ("14", "逾期记录查询"),
        ("15", "统计报表（分类/趋势/畅销榜）"),
        ("0", "退出程序"),
    ]
    for num, label in items:
        print("  [%s] %s" % (num, label))
    print("=" * 54)


def do_task(db, choice):
    """根据菜单选择执行对应功能"""
    if choice == "1":
        doc = {"isbn": input("ISBN：").strip(), "title": input("书名：").strip(),
               "author": input("作者：").strip(), "publisher": input("出版社：").strip(),
               "category": input("类别：").strip(), "price": float(input("价格：")),
               "stock": int(input("库存：")), "rating": float(input("评分：")),
               "tags": input("标签（逗号分隔）：").split(","), "borrow_count": 0}
        res = book_mgr.add_book(db, doc)
        print("已新增图书，_id = %s" % res.inserted_id)

    elif choice == "2":
        demo = [
            {"isbn": "9787121000011", "title": "示例图书甲", "author": "演示者", "publisher": "测试出版社",
             "category": "计算机", "price": 39.9, "stock": 10, "rating": 4.0, "tags": ["示例"], "borrow_count": 0},
            {"isbn": "9787121000028", "title": "示例图书乙", "author": "演示者", "publisher": "测试出版社",
             "category": "数学", "price": 29.9, "stock": 8, "rating": 3.9, "tags": ["示例"], "borrow_count": 0},
        ]
        res = book_mgr.add_books_batch(db, demo)
        print("批量导入 %d 本示例图书" % len(res.inserted_ids))

    elif choice == "3":
        doc = book_mgr.fetch_by_isbn(db, input("ISBN：").strip())
        if doc:
            print("查询结果：%s | %s | ¥%s | 库存 %s" % (doc["title"], doc["author"], doc["price"], doc["stock"]))
        else:
            print("（提示）未找到该 ISBN 对应的图书")

    elif choice == "4":
        low, high = float(input("最低价：")), float(input("最高价："))
        docs = book_mgr.fetch_by_price_range(db, low, high)
        print("价格区间 [%s, %s] 内图书 %d 本：" % (low, high, len(docs)))
        for d in docs:
            print("  - %s ¥%s" % (d["title"], d["price"]))

    elif choice == "5":
        docs = book_mgr.fetch_top_rated(db, 5)
        print("评分排行榜 TOP5：")
        for i, d in enumerate(docs, 1):
            print("  %d. %s（评分 %s）" % (i, d["title"], d["rating"]))

    elif choice == "6":
        docs = book_mgr.fetch_by_keyword(db, input("关键字：").strip())
        print("命中 %d 本：" % len(docs))
        for d in docs:
            print("  - %s" % d["title"])

    elif choice == "7":
        isbn, delta = input("ISBN：").strip(), int(input("库存变化量（负数为减少）："))
        res = book_mgr.adjust_stock(db, isbn, delta)
        print("匹配 %d 条，修改 %d 条（受影响文档数）" % (res.matched_count, res.modified_count))

    elif choice == "8":
        res = book_mgr.remove_book(db, input("ISBN：").strip())
        print("删除条数：%d" % res.deleted_count)

    elif choice == "9":
        for r in reader_mgr.list_all(db):
            print("  %s | %s | %s | %s" % (r["card_no"], r["name"], r["college"], r["level"]))

    elif choice == "10":
        for row in reader_mgr.count_by_college(db):
            print("  %s：%s 人" % (row["_id"], row["人数"]))

    elif choice == "11":
        for row in reader_mgr.count_by_level(db):
            print("  %s：%s 人" % (row["_id"], row["人数"]))

    elif choice == "12":
        card, isbn = input("借阅证号：").strip(), input("图书 ISBN：").strip()
        res = borrow_mgr.register_borrow(db, card, isbn)
        print("借阅登记成功，记录 _id = %s" % res.inserted_id)

    elif choice == "13":
        card, isbn = input("借阅证号：").strip(), input("图书 ISBN：").strip()
        res = borrow_mgr.handle_return(db, card, isbn)
        if res:
            print("归还成功：删除借出记录 %d 条，库存已回库 +1" % res.deleted_count)
        else:
            print("（提示）未找到该读者对应图书的借出记录")

    elif choice == "14":
        docs = borrow_mgr.show_overdue(db)
        print("逾期记录 %d 条：" % len(docs))
        for d in docs:
            print("  - %s 借阅 %s，日期 %s" % (d["reader_card"], d["book_isbn"], d["borrow_date"].strftime("%Y-%m-%d")))

    elif choice == "15":
        print("\n--- 分类统计（按库存总量降序） ---")
        for row in stat_mgr.category_summary(db):
            print("  %s：库存 %s，均价 ¥%s，数量 %s" % (row["_id"], row["库存总量"], row["平均价格"], row["图书数量"]))
        print("--- 借阅趋势（按年份） ---")
        for row in stat_mgr.yearly_trend(db):
            print("  %s：%s 次" % (row["_id"]["文本"], row["借阅量"]))
        print("--- 畅销榜（借阅次数最多） ---")
        for row in stat_mgr.bestseller(db):
            print("  %s：借阅 %s 次" % (row["title"], row["borrow_count"]))

    elif choice == "0":
        return False
    return True


def main():
    print("正在连接 MongoDB（%s:%s/%s）..." % (conn.HOST, conn.PORT, conn.DB_NAME))
    try:
        client = conn.build_client()
        db = conn.get_database(client)
    except Exception as exc:
        print("连接失败：%s" % exc)
        sys.exit(1)
    print("连接成功，当前时间 %s" % stat_mgr.current_ts())
    print("集合文档总数：books=%d, readers=%d, borrow_logs=%d, category_stats=%d"
          % (db.books.count_documents({}), db.readers.count_documents({}),
             db.borrow_logs.count_documents({}), db.category_stats.count_documents({})))

    running = True
    while running:
        show_menu()
        choice = input("请输入功能编号：").strip()
        if choice not in [str(i) for i in range(16)]:
            print("无效编号，请重新输入")
            continue
        try:
            running = do_task(db, choice)
        except Exception as exc:
            print("执行出错：%s" % exc)

    client.close()
    print("已退出程序，数据库连接已关闭。再见！")


if __name__ == "__main__":
    main()
