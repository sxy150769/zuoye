// =====================================================================
// 实训项目（版本2）· 图书情报检索与统计平台
// 任务六 · 独立验证：用独立查询核对任务三、任务四的关键结果
// 对应任务书 ST-6.2（等价于 Compass 图形化逐项核对）
// =====================================================================
use library;

print("========== 任务六 独立验证（命令行核对） ==========");

// Q1 定价 80 元以上
var q1 = db.books.countDocuments({ price: { $gt: 80 } });
print("Q1 定价 80 元以上图书条数：" + q1 + "（预期 9）" + (q1 === 9 ? " ✔" : " ✘"));

// Q2 库存不足 10 本
var q2 = db.books.countDocuments({ stock: { $lt: 10 } });
print("Q2 库存不足 10 本图书条数：" + q2 + "（预期 9）" + (q2 === 9 ? " ✔" : " ✘"));

// Q7 评分 4.0 以上且计算机类
var q7 = db.books.countDocuments({ $and: [{ rating: { $gt: 4.0 } }, { category: "计算机" }] });
print("Q7 评分 4.0 以上且计算机类条数：" + q7 + "（预期 6）" + (q7 === 6 ? " ✔" : " ✘"));

// Q14 评分排行前 5
var q14 = db.books.find().sort({ rating: -1 }).limit(5).toArray();
print("Q14 评分排行前 5 条数：" + q14.length + "（预期 5）" + (q14.length === 5 ? " ✔" : " ✘"));

// A1 分类统计分组数
var a1 = db.books.aggregate([{ $group: { _id: "$category", n: { $sum: 1 } } }]).toArray();
print("A1 分类统计分组数：" + a1.length + "（预期 5）" + (a1.length === 5 ? " ✔" : " ✘"));

// 视图 book_in_stock 数据量（stock>0）
var view_count = db.book_in_stock.countDocuments({});
var stock_pos = db.books.countDocuments({ stock: { $gt: 0 } });
print("视图 book_in_stock 数据量：" + view_count + "，与直接过滤 stock>0 一致：" + (view_count === stock_pos ? "是 ✔" : "否 ✘"));

print("\n===== 验证结论 =====");
var all_ok = q1 === 9 && q2 === 9 && q7 === 6 && q14.length === 5 && a1.length === 5 && view_count === stock_pos;
print(all_ok ? "全部 6 项核对一致，独立验证通过。" : "存在不一致项，请排查。");
