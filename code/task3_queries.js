// =====================================================================
// 实训项目（版本2）· 图书情报检索与统计平台
// 任务三 · 检索功能实现：基础检索 Q1—Q6、组合检索 Q7—Q12、结果处理 Q13—Q16、
//          更新 U1—U4、删除 D1—D3
// 对应任务书 ST-3，全部命令在 library 数据库实际执行并记录结果条数
// =====================================================================
use library;

function show(tag, cursor, fields) {
  var arr = cursor.toArray();
  print("----- " + tag + " 结果条数：" + arr.length + " -----");
  arr.forEach(function (doc) {
    if (!fields) fields = ["title", "author", "price", "stock", "rating", "category", "name", "college", "level", "email", "status"];
    var parts = [];
    fields.forEach(function (k) { if (doc[k] !== undefined) parts.push(doc[k] + (k === "price" ? "元" : "")); });
    print("  " + parts.join(" | "));
  });
}

// ============ 基础检索 Q1—Q6 ============
print("\n========== 基础检索 Q1—Q6 ==========");
print("Q1 定价在 80 元以上的图书（$gt）");
show("Q1", db.books.find({ price: { $gt: 80 } }), ["title", "price"]);

print("Q2 库存不足 10 本的图书（$lt）");
show("Q2", db.books.find({ stock: { $lt: 10 } }), ["title", "stock"]);

print("Q3 按 ISBN 精确查找指定图书（$eq）");
show("Q3", db.books.find({ isbn: { $eq: "9787115458932" } }), ["title", "author"]);

print("Q4 email 为空的读者（$eq: null）");
show("Q4", db.readers.find({ email: { $eq: null } }), ["name", "college"]);

print("Q5 排除“高等教育出版社”的图书（$nin）");
show("Q5", db.books.find({ publisher: { $nin: ["高等教育出版社"] } }), ["title", "publisher"]);

print("Q6 属于“计算机”或“经济管理”类别的图书（$in）");
show("Q6", db.books.find({ category: { $in: ["计算机", "经济管理"] } }), ["category", "title"]);

// ============ 组合与高级检索 Q7—Q12 ============
print("\n========== 组合与高级检索 Q7—Q12 ==========");
print("Q7 评分 4.0 以上且属于计算机类的图书（$and）");
show("Q7", db.books.find({ $and: [{ rating: { $gt: 4.0 } }, { category: "计算机" }] }), ["title", "rating", "category"]);

print("Q8 评分低于 3.5 或库存为 0 的图书（$or）");
show("Q8", db.books.find({ $or: [{ rating: { $lt: 3.5 } }, { stock: 0 }] }), ["title", "rating", "stock"]);

print("Q9 书名中包含“Python”的图书（$regex）");
show("Q9", db.books.find({ title: { $regex: "Python" } }), ["title"]);

print("Q10 同时带有“编程”和“入门”两个标签的图书（$all）");
show("Q10", db.books.find({ tags: { $all: ["编程", "入门"] } }), ["title", "tags"]);

print("Q11 恰好有 3 个标签的图书（$size）");
show("Q11", db.books.find({ tags: { $size: 3 } }), ["title", "tags"]);

print("Q12 已录入 tags 字段的图书（$exists）");
show("Q12", db.books.find({ tags: { $exists: true } }), ["title"]);

// ============ 结果处理 Q13—Q16 ============
print("\n========== 结果处理 Q13—Q16 ==========");
print("Q13 查找 _id 为字符串类型的文档（$type）");
show("Q13", db.books.find({ _id: { $type: "string" } }), ["title"]);

print("Q14 按评分降序排列，取前 5 条（sort + limit）");
show("Q14", db.books.find().sort({ rating: -1 }).limit(5), ["title", "rating"]);

print("Q15 只返回书名、价格、评分三个字段，不含 _id（投影）");
var arr15 = db.books.find({}, { title: 1, price: 1, rating: 1, _id: 0 }).toArray();
print("----- Q15 投影结果条数：" + arr15.length + " -----");
arr15.slice(0, 5).forEach(function (d) { print("  " + JSON.stringify(d)); });
print("  ...（共 " + arr15.length + " 条，投影字段：title/price/rating，无 _id）");

print("Q16 获取所有图书类别清单（distinct）");
var cats = db.books.distinct("category");
print("----- Q16 distinct 结果：" + cats.length + " 类 -----");
print("  " + cats.join(" / "));

// ============ 更新 U1—U4 ============
print("\n========== 更新操作 U1—U4 ==========");
print("U1 把《深度学习入门》库存减少 5（updateOne + $inc）");
var u1 = db.books.updateOne({ title: "深度学习入门：基于Python的理论与实现" }, { $inc: { stock: -5 } });
print("  匹配 " + u1.matchedCount + " 条，修改 " + u1.modifiedCount + " 条，库存 20 -> " + db.books.findOne({ title: "深度学习入门：基于Python的理论与实现" }).stock);

print("U2 将文学类所有图书价格打 9 折（updateMany + $mul）");
var u2 = db.books.updateMany({ category: "文学" }, { $mul: { price: 0.9 } });
print("  匹配 " + u2.matchedCount + " 条，修改 " + u2.modifiedCount + " 条（36→32.4、55→49.5、128→115.2、42→37.8、45→40.5）");

print("U3 为《算法（第4版）》新增 last_modified 字段并记录当前时间（$currentDate）");
var u3 = db.books.updateOne({ title: "算法（第4版）" }, { $currentDate: { last_modified: true } });
var algo = db.books.findOne({ title: "算法（第4版）" });
print("  匹配 " + u3.matchedCount + " 条，last_modified = " + JSON.stringify(algo.last_modified));

print("U4 删除《围城》的 tags 字段（$unset）");
var u4 = db.books.updateOne({ title: "围城" }, { $unset: { tags: "" } });
var wei = db.books.findOne({ title: "围城" });
print("  匹配 " + u4.matchedCount + " 条，删除后围城文档字段：" + Object.keys(wei).join(" / "));

// ============ 删除 D1—D3 ============
print("\n========== 删除操作 D1—D3 ==========");
print("D1 删除一条已归还的借阅记录（deleteOne + $eq）");
var target = db.borrow_logs.findOne({ status: "已归还" });
var d1 = db.borrow_logs.deleteOne({ _id: target._id });
print("  删除记录 reader_card=" + target.reader_card + "，book_isbn=" + target.book_isbn + "，删除条数：" + d1.deletedCount);

print("D2 清理逾期未还的借阅记录（deleteMany）——先预览再删除");
var preview = db.borrow_logs.find({ status: "逾期" }).toArray();
print("  【预览】逾期记录条数：" + preview.length);
preview.forEach(function (r) { print("    - " + r.reader_card + " 借阅 " + r.book_isbn + "，借阅日期 " + r.borrow_date.toISOString().slice(0, 10)); });
var d2 = db.borrow_logs.deleteMany({ status: "逾期" });
print("  deleteMany 实际删除条数：" + d2.deletedCount);
print("  删除后 borrow_logs 文档数：" + db.borrow_logs.countDocuments({}));

print("D3 整体替换读者《邓凯文》的信息，保留 _id（replaceOne）");
var d3target = db.readers.findOne({ name: "邓凯文" });
var d3 = db.readers.replaceOne(
  { _id: d3target._id },
  {
    card_no: "R20250016",
    name: "邓凯文",
    college: "经济管理学院",
    email: "dengkw@stu.edu.cn",
    phone: "188 2233 6655",
    level: "普通",
    register_date: d3target.register_date,
    fav_categories: ["经济管理", "外语", "数学"]
  }
);
print("  匹配 " + d3.matchedCount + " 条，替换 " + d3.modifiedCount + " 条，_id 未变化：" + (db.readers.findOne({ _id: d3target._id }).name === "邓凯文"));

print("\n任务三全部检索、更新与删除操作执行完毕。");
