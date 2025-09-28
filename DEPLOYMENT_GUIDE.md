# 🚀 Django OJ系统部署指南

## 📋 概述

本指南将帮助您将Django OJ系统从SQLite迁移到PostgreSQL，并配置Docker容器化部署。

## 🔧 数据库迁移完成情况

### ✅ 已完成的配置

1. **PostgreSQL依赖启用**
   - `requirements-linux.txt` 中启用了 `psycopg2-binary`
   - 启用了Redis支持 (`redis`, `django-redis`)

2. **Django设置更新**
   - 支持环境变量配置
   - 根据 `DATABASE_URL` 自动选择数据库
   - 配置了Redis缓存和会话存储

3. **Docker配置优化**
   - 更新了 `docker-compose.yml` 使用环境变量
   - 创建了 `docker.env` 环境变量文件

4. **迁移脚本**
   - `scripts/migrate_to_postgresql.py` - 数据库迁移脚本
   - `scripts/init_database.sh` - 数据库初始化脚本
   - `scripts/test_postgresql.py` - 连接测试脚本

## 🐳 Docker部署步骤

### 1. 准备环境

```bash
# 克隆项目（如果还没有）
git clone <your-repo-url>
cd django_OJ_02

# 确保Docker和Docker Compose已安装
docker --version
docker-compose --version
```

### 2. 配置环境变量

编辑 `docker.env` 文件，设置生产环境的安全配置：

```bash
# 生成安全的SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 更新docker.env中的SECRET_KEY
SECRET_KEY=your-generated-secret-key-here
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f web
```

### 4. 初始化数据库

```bash
# 进入web容器
docker-compose exec web bash

# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput
```

### 5. 验证部署

访问以下URL验证部署：
- 主应用: http://localhost:8000
- 管理界面: http://localhost:8000/admin
- API文档: http://localhost:8000/api/

## 🔧 开发环境配置

### 使用SQLite（开发）

```bash
# 不设置DATABASE_URL，系统将使用SQLite
python manage.py runserver
```

### 使用PostgreSQL（开发）

```bash
# 设置环境变量
export DATABASE_URL=postgresql://oj_user:oj_password@localhost:5432/django_oj
export POSTGRES_HOST=localhost

# 运行服务器
python manage.py runserver
```

## 📊 数据库配置说明

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | 无 | 设置后启用PostgreSQL |
| `POSTGRES_DB` | django_oj | 数据库名称 |
| `POSTGRES_USER` | oj_user | 数据库用户 |
| `POSTGRES_PASSWORD` | oj_password | 数据库密码 |
| `POSTGRES_HOST` | db | 数据库主机 |
| `POSTGRES_PORT` | 5432 | 数据库端口 |
| `REDIS_URL` | redis://redis:6379/1 | Redis连接URL |

### 数据库选择逻辑

```python
if os.environ.get('DATABASE_URL'):
    # 使用PostgreSQL
else:
    # 使用SQLite
```

## 🧪 测试脚本

### 测试PostgreSQL连接

```bash
# 设置环境变量
export DATABASE_URL=postgresql://oj_user:oj_password@localhost:5432/django_oj

# 运行测试
python scripts/test_postgresql.py
```

### 测试Docker部署

```bash
# 启动Docker服务
docker-compose up -d

# 测试连接
docker-compose exec web python scripts/test_postgresql.py
```

## 🔒 安全配置

### 生产环境安全设置

1. **更改默认密码**
   ```bash
   # 在docker.env中设置强密码
   POSTGRES_PASSWORD=your-strong-password
   ```

2. **设置安全的SECRET_KEY**
   ```bash
   # 生成新的SECRET_KEY
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **配置ALLOWED_HOSTS**
   ```bash
   # 在docker.env中设置允许的主机
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

## 📝 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查PostgreSQL是否运行
   docker-compose ps db
   
   # 查看数据库日志
   docker-compose logs db
   ```

2. **迁移失败**
   ```bash
   # 重置数据库
   docker-compose down -v
   docker-compose up -d
   ```

3. **静态文件问题**
   ```bash
   # 重新收集静态文件
   docker-compose exec web python manage.py collectstatic --noinput
   ```

## 🎯 下一步

数据库迁移已完成！接下来可以：

1. **测试Docker部署** - 在Linux服务器上部署
2. **配置生产环境** - 设置域名、SSL证书等
3. **监控和日志** - 配置日志收集和监控
4. **备份策略** - 设置数据库备份

## 📞 支持

如果遇到问题，请检查：
1. Docker和Docker Compose版本
2. 环境变量配置
3. 网络连接
4. 日志输出
