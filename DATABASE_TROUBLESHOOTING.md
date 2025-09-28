# 🔧 数据库配置问题解决指南

## 🚨 **当前问题**

您遇到了PostgreSQL连接错误，这是因为：

1. **本地没有PostgreSQL服务器**：Windows开发环境默认没有PostgreSQL
2. **环境变量设置错误**：URL中有拼写错误
3. **开发环境配置**：开发时使用SQLite更简单

## ✅ **解决方案**

### 方案1：使用SQLite（推荐开发环境）

```bash
# 清除PostgreSQL环境变量
Remove-Item Env:DATABASE_URL

# 启动Django服务器（自动使用SQLite）
python manage.py runserver
```

**优点：**
- ✅ 无需安装额外软件
- ✅ 开发环境简单
- ✅ 数据文件本地存储
- ✅ 快速启动

### 方案2：使用Docker PostgreSQL（测试生产环境）

```bash
# 1. 启动PostgreSQL和Redis服务
docker-compose -f docker-compose.dev.yml up -d

# 2. 设置环境变量
$env:DATABASE_URL="postgresql://oj_user:oj_password@localhost:5432/django_oj"
$env:REDIS_URL="redis://localhost:6379/1"

# 3. 执行数据库迁移
python manage.py migrate

# 4. 启动Django服务器
python manage.py runserver
```

**优点：**
- ✅ 模拟生产环境
- ✅ 测试PostgreSQL功能
- ✅ 验证Docker配置

## 🛠️ **快速修复脚本**

### 开发环境（SQLite）
```bash
# 使用SQLite开发
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
python manage.py runserver
```

### 测试PostgreSQL
```bash
# 启动PostgreSQL服务
scripts/start_dev_services.bat

# 设置环境变量
$env:DATABASE_URL="postgresql://oj_user:oj_password@localhost:5432/django_oj"

# 测试连接
python scripts/test_postgresql.py
```

## 📊 **数据库选择建议**

### 开发环境
- **推荐：SQLite**
  - 无需安装数据库服务器
  - 文件存储在本地
  - 开发速度快

### 生产环境
- **推荐：PostgreSQL**
  - 性能更好
  - 支持并发
  - 数据安全

## 🔍 **环境变量说明**

| 变量 | 设置 | 数据库引擎 |
|------|------|------------|
| 无 `DATABASE_URL` | - | SQLite |
| `DATABASE_URL=postgresql://...` | 设置 | PostgreSQL |

## 🚀 **当前状态**

✅ **Django服务器已启动** - 使用SQLite数据库
✅ **项目配置完成** - 支持PostgreSQL和SQLite
✅ **Docker配置就绪** - 生产环境部署准备完毕

## 📝 **下一步**

1. **继续开发** - 使用SQLite进行功能开发
2. **测试PostgreSQL** - 使用Docker测试PostgreSQL功能
3. **部署到Linux** - 使用Docker Compose部署到生产环境

## 🆘 **常见问题**

### Q: 为什么选择SQLite开发？
A: SQLite无需安装，开发简单，适合本地开发。

### Q: 什么时候使用PostgreSQL？
A: 生产环境部署时，或者需要测试PostgreSQL特定功能时。

### Q: 如何切换数据库？
A: 设置或清除 `DATABASE_URL` 环境变量即可。

### Q: Docker部署需要PostgreSQL吗？
A: 是的，生产环境使用PostgreSQL，Docker会自动处理。
