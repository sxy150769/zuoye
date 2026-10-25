// =====================================================================
// 实训项目（版本2）· 图书情报检索与统计平台
// 任务四 · 索引建立 I1—I5 与 explain 对比
// 对应任务书 ST-4 索引部分
// =====================================================================
use library;

print("========== 索引建立 I1—I5 ==========");

// I1 books.isbn 唯一索引
print("I1 为 books.isbn 建立唯一索引");
db.books.createIndex({ isbn: 1 }, { unique: true, name: "idx_isbn_unique" });

// 验证重复 ISBN 无法插入
print("  验证重复 ISBN 插入被拒绝：");
try {
  db.books.insertOne({ isbn: "9787115458932", title: "重复测试书", author: "测试", category: "计算机", price: 1, stock: 1, rating: 1, tags: [], publish_date: new Date(), borrow_count: 0 });
  print("  [异常] 重复插入竟然成功");
} catch (e) {
  print("  重复插入失败（符合预期）：错误码 " + e.code + "，错误信息 " + e.errmsg.split("E11000")[1] || e.errmsg);
}

// I2 books.title 单键索引
print("I2 为 books.title 建立单键索引");
db.books.createIndex({ title: 1 }, { name: "idx_title" });

// I3 books.category 单键索引
print("I3 为 books.category 建立单键索引");
db.books.createIndex({ category: 1 }, { name: "idx_category" });

// I4 books.tags 多键索引
print("I4 为 books.tags 建立多键索引");
db.books.createIndex({ tags: 1 }, { name: "idx_tags_multikey" });

// I5 category 与 price 复合索引
print("I5 为 category 与 price 建立复合索引");
db.books.createIndex({ category: 1, price: 1 }, { name: "idx_category_price" });

// 查看索引清单
print("\n===== 索引清单（getIndexes） =====");
db.books.getIndexes().forEach(function (i) {
  print("  - " + i.name + " | " + JSON.stringify(i.key) + (i.unique ? " | unique" : ""));
});

// explain 对比：有索引 vs 无索引
print("\n===== explain 对比（isbn 精确查询） =====");
print("-- 有唯一索引时 --");
var withIdx = db.books.find({ isbn: "9787115458932" }).explain("executionStats");
print("  查询计划：" + withIdx.queryPlanner.winningPlan.inputStage.stage + " -> " + withIdx.queryPlanner.winningPlan.inputStage.inputStage.stage);
print("  扫描文档数：" + withIdx.executionStats.totalDocsExamined + "，返回：" + withIdx.executionStats.nReturned + " 条");

print("-- 删除索引后（全表扫描） --");
db.books.dropIndex("idx_isbn_unique");
var withoutIdx = db.books.find({ isbn: "9787115458932" }).explain("executionStats");
print("  查询计划：" + withoutIdx.queryPlanner.winningPlan.stage);
print("  扫描文档数：" + withoutIdx.executionStats.totalDocsExamined + "，返回：" + withoutIdx.executionStats.nReturned + " 条");

// 恢复唯一索引，保持最终状态完整
print("-- 恢复 isbn 唯一索引 --");
db.books.createIndex({ isbn: 1 }, { unique: true, name: "idx_isbn_unique" });
print("  已恢复。当前 books 索引数：" + db.books.getIndexes().length);

print("\n任务四索引部分执行完毕。");
