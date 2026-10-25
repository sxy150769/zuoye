// =====================================================================
// 实训项目（版本2）· 图书情报检索与统计平台
// 任务二 · 数据建模：创建 library 数据库、四个普通集合与三种特殊集合
// 对应任务书 ST-2.1 / ST-2.2
// =====================================================================

// 0) 若 library 库已存在则先清空，保证可重复执行
use library;
db.dropDatabase();

// 1) ST-2.1 创建业务数据库与四个普通集合
db.createCollection("books");
db.createCollection("readers");
db.createCollection("borrow_logs");
db.createCollection("category_stats");
print("==> 四个普通集合创建完成：books / readers / borrow_logs / category_stats");

// 2) ST-2.2 创建固定集合 book_logs：容量 1MB（1048576 字节），最多 1000 条
db.createCollection("book_logs", { capped: true, size: 1048576, max: 1000 });
print("==> 固定集合 book_logs 创建完成（capped=true, size=1048576, max=1000）");

// 3) ST-2.2 创建时间序列集合 borrow_logs：时间字段 borrow_date，粒度 hours，过期 2 年
//    注意：先删除刚才创建的普通集合 borrow_logs，再以时间序列方式重建；
//    expireAfterSeconds 为 createCollection 顶层选项（MongoDB 7.0 语法）
db.borrow_logs.drop();
db.createCollection("borrow_logs", {
  timeseries: {
    timeField: "borrow_date",
    granularity: "hours"
  },
  expireAfterSeconds: 63072000
});
print("==> 时间序列集合 borrow_logs 创建完成（timeField=borrow_date, granularity=hours, expireAfterSeconds=63072000）");

// 4) ST-2.2 创建视图 book_in_stock：过滤 stock > 0 的图书
db.createView("book_in_stock", "books", [{ $match: { stock: { $gt: 0 } } }]);
print("==> 视图 book_in_stock 创建完成（基于 books，过滤 stock>0）");

// 5) 验证：集合列表（含类型标记）
print("\n===== 集合列表（含类型标记） =====");
db.getCollectionInfos().forEach(function (info) {
  var type = "普通集合";
  if (info.type === "view") type = "视图";
  if (info.options.capped) type = "固定集合";
  if (info.options.timeseries) type = "时间序列集合";
  print("  - " + info.name + " | 类型: " + type);
});

// 6) 验证：各集合选项配置
print("\n===== 集合选项配置查询 =====");
print("book_logs 选项: " + JSON.stringify(db.getCollectionInfos({ name: "book_logs" })[0].options));
print("borrow_logs 选项: " + JSON.stringify(db.getCollectionInfos({ name: "borrow_logs" })[0].options));
print("book_in_stock 选项: " + JSON.stringify(db.getCollectionInfos({ name: "book_in_stock" })[0].options));
print("\n任务二数据建模完成。");
