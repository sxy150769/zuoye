// =====================================================================
// 实训项目（版本2）· 图书情报检索与统计平台
// 任务四 · 聚合管道统计 A1—A9
// 对应任务书 ST-4，在 library 数据库实际执行
// =====================================================================
use library;

print("========== 聚合管道统计 A1—A9 ==========");

// A1 按类别统计图书数量与平均评分（$group + $sum、$avg）
print("A1 按类别统计图书数量与平均评分");
var a1 = db.books.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 }, avg_rating: { $avg: "$rating" } } },
  { $sort: { count: -1 } }
]).toArray();
print("  分组数：" + a1.length);
a1.forEach(function (g) { print("    " + g._id + "：数量 " + g.count + "，平均评分 " + g.avg_rating.toFixed(2)); });

// A2 统计各出版社图书数量，取最多的 5 家（$group + $topN）
print("A2 出版社图书数量 TOP5（$topN）");
var a2 = db.books.aggregate([
  { $group: { _id: "$publisher", book_count: { $sum: 1 } } },
  { $group: { _id: null, top: { $topN: { n: 5, sortBy: { book_count: -1 }, output: { publisher: "$_id", count: "$book_count" } } } } },
  { $unwind: "$top" },
  { $project: { _id: 0, publisher: "$top.publisher", count: "$top.count" } }
]).toArray();
print("  返回 " + a2.length + " 家");
a2.forEach(function (g) { print("    " + g.publisher + "：" + g.count + " 本"); });

// A3 找出文档数最多的图书类别（$sortByCount）
print("A3 文档数最多的图书类别（$sortByCount）");
var a3 = db.books.aggregate([{ $sortByCount: "$category" }]).toArray();
print("  结果 " + a3.length + " 组，最多的是：" + a3[0]._id + "（" + a3[0].count + " 本）");

// A4 评分最高的 3 本图书，显示书名与借阅次数（$sort + $limit + $project）
print("A4 评分最高的 3 本图书（书名 + 借阅次数）");
var a4 = db.books.aggregate([
  { $sort: { rating: -1 } },
  { $limit: 3 },
  { $project: { _id: 0, title: 1, rating: 1, borrow_count: 1 } }
]).toArray();
a4.forEach(function (g) { print("    " + g.title + " | 评分 " + g.rating + " | 借阅次数 " + g.borrow_count); });

// A5 每本书销售额 = 单价 × 借阅次数，四舍五入保留两位小数（$multiply + $round）
print("A5 每本书销售额（单价 × 借阅次数，保留两位小数）");
var a5 = db.books.aggregate([
  { $project: { _id: 0, title: 1, price: 1, borrow_count: 1, sales: { $round: [{ $multiply: ["$price", "$borrow_count"] }, 2] } } },
  { $sort: { sales: -1 } },
  { $limit: 5 }
]).toArray();
a5.forEach(function (g) { print("    " + g.title + "：¥" + g.sales + "（" + g.price + " × " + g.borrow_count + "）"); });
print("    ...共 20 本，以上为销售额前 5 名");

// A6 按借阅年份分组统计借阅量，格式化为“2026年”（$year + $dateToString）
print("A6 按年份统计借阅量（$year + $dateToString）");
var a6 = db.borrow_logs.aggregate([
  { $group: { _id: { $dateToString: { format: "%Y年", date: "$borrow_date" } }, total: { $sum: 1 } } },
  { $sort: { _id: 1 } }
]).toArray();
a6.forEach(function (g) { print("    " + g._id + "：借阅 " + g.total + " 次"); });

// A7 每位读者借阅次数，取前 5 名（$group + $sort + $limit）
print("A7 读者借阅次数 TOP5");
var a7 = db.borrow_logs.aggregate([
  { $group: { _id: "$reader_card", cnt: { $sum: 1 } } },
  { $sort: { cnt: -1 } },
  { $limit: 5 }
]).toArray();
a7.forEach(function (g) { print("    " + g._id + "：借阅 " + g.cnt + " 次"); });

// A8 关联读者与借阅流水，产出学院借阅量排行榜（$lookup）
print("A8 学院借阅量排行榜（$lookup）");
var a8 = db.borrow_logs.aggregate([
  { $lookup: { from: "readers", localField: "reader_card", foreignField: "card_no", as: "rd" } },
  { $unwind: "$rd" },
  { $group: { _id: "$rd.college", total: { $sum: 1 } } },
  { $sort: { total: -1 } }
]).toArray();
a8.forEach(function (g) { print("    " + g._id + "：" + g.total + " 次"); });

// A9 把 A1 的分类统计结果写入 category_stats（$merge）
print("A9 将 A1 分类统计结果写入 category_stats（$merge）");
db.books.aggregate([
  { $group: { _id: "$category", book_count: { $sum: 1 }, avg_rating: { $avg: "$rating" } } },
  { $merge: { into: "category_stats", on: "_id", whenMatched: "replace", whenNotMatched: "insert" } }
]);
print("  category_stats 集合当前文档数：" + db.category_stats.countDocuments({}));
db.category_stats.find().sort({ _id: 1 }).forEach(function (d) {
  print("    " + JSON.stringify(d));
});

print("\n任务四聚合统计执行完毕。");
