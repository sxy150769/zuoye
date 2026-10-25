// =====================================================================
// 实训项目（版本2）· 图书情报检索与统计平台
// 任务四 · 用户与权限管理 S1—S3（账号创建部分）
// 对应任务书 ST-4：只读账号 libReader（read）、读写账号 libWriter（readWrite + dbAdmin）
// 说明：任务书要求密码交互式输入；实训脚本以参数化方式等价提供密码
// =====================================================================
use library;

// 可重复执行：先清理可能已存在的同名账号
try { db.dropUser("libReader"); print("==> 已清理旧账号 libReader"); } catch (e) {}
try { db.dropUser("libWriter"); print("==> 已清理旧账号 libWriter"); } catch (e) {}

// S1 创建只读账号 libReader（read 角色）
print("S1 创建只读账号 libReader（角色 read）");
db.createUser({ user: "libReader", pwd: "LibReader@2026", roles: [{ role: "read", db: "library" }] });
print("  libReader 创建成功");

// S2 创建读写账号 libWriter（readWrite + dbAdmin 角色）
print("S2 创建读写账号 libWriter（角色 readWrite + dbAdmin）");
db.createUser({ user: "libWriter", pwd: "LibWriter@2026", roles: [{ role: "readWrite", db: "library" }, { role: "dbAdmin", db: "library" }] });
print("  libWriter 创建成功");

// 查看账号清单
print("\n===== library 库用户清单 =====");
db.getUsers().users.forEach(function (u) {
  print("  - " + u.user + " | 角色: " + u.roles.map(function (r) { return r.role + "@" + r.db; }).join(", "));
});

print("\n账号创建完成。下一步：重启服务启用 --auth 访问控制后进行 S3 权限验证。");
