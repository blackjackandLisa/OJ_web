# 🔒 生产环境安全配置指南

## ⚠️ **部署前必须修改的安全配置**

### 1. **SECRET_KEY安全配置**

**当前配置（不安全）：**
```bash
SECRET_KEY=your-secret-key-here-change-in-production
```

**生产环境配置：**
```bash
# 生成新的SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 更新docker.env文件
SECRET_KEY=your-generated-secret-key-here
```

### 2. **数据库密码安全**

**当前配置（不安全）：**
```bash
POSTGRES_PASSWORD=oj_password
```

**生产环境配置：**
```bash
# 使用强密码
POSTGRES_PASSWORD=your-strong-database-password-here
```

### 3. **ALLOWED_HOSTS配置**

**当前配置：**
```bash
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

**生产环境配置：**
```bash
# 设置您的域名
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### 4. **SSL/HTTPS配置**

**当前配置（HTTP）：**
```nginx
listen 80;
```

**生产环境配置（HTTPS）：**
```nginx
# 需要SSL证书
listen 443 ssl;
ssl_certificate /path/to/certificate.crt;
ssl_certificate_key /path/to/private.key;
```

## 🛡️ **安全配置检查清单**

### ✅ **已配置的安全措施**

1. **安全头设置**
   - ✅ X-Frame-Options: SAMEORIGIN
   - ✅ X-Content-Type-Options: nosniff
   - ✅ X-XSS-Protection: 1; mode=block
   - ✅ Referrer-Policy: strict-origin-when-cross-origin
   - ✅ Content-Security-Policy

2. **Django安全设置**
   - ✅ SECURE_BROWSER_XSS_FILTER: True
   - ✅ SECURE_CONTENT_TYPE_NOSNIFF: True
   - ✅ X_FRAME_OPTIONS: DENY

3. **容器安全**
   - ✅ 健康检查配置
   - ✅ 服务依赖控制
   - ✅ 端口最小化暴露

### ❌ **需要手动配置的安全措施**

1. **SSL证书配置**
   ```bash
   # 使用Let's Encrypt获取免费SSL证书
   certbot --nginx -d your-domain.com
   ```

2. **防火墙配置**
   ```bash
   # 只开放必要端口
   ufw allow 80
   ufw allow 443
   ufw deny 5432  # 关闭数据库外部访问
   ufw deny 6379  # 关闭Redis外部访问
   ```

3. **数据库备份**
   ```bash
   # 设置定期备份
   crontab -e
   # 添加：0 2 * * * docker-compose exec db pg_dump -U oj_user django_oj > /backup/db_$(date +%Y%m%d).sql
   ```

## 🚀 **生产环境部署步骤**

### 1. **准备服务器**
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. **配置安全设置**
```bash
# 生成新的SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 更新docker.env文件
nano docker.env
```

### 3. **部署应用**
```bash
# 克隆项目
git clone <your-repo-url>
cd django_OJ_02

# 构建和启动服务
docker-compose up -d

# 检查服务状态
docker-compose ps
docker-compose logs -f
```

### 4. **配置域名和SSL**
```bash
# 安装Nginx（如果使用外部Nginx）
sudo apt install nginx

# 配置域名解析
# 设置DNS记录指向服务器IP

# 获取SSL证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 **监控和日志**

### 1. **日志监控**
```bash
# 查看应用日志
docker-compose logs -f web

# 查看数据库日志
docker-compose logs -f db

# 查看Nginx日志
docker-compose logs -f nginx
```

### 2. **性能监控**
```bash
# 查看容器资源使用
docker stats

# 查看服务健康状态
curl http://localhost/health/
```

## 🔧 **故障排除**

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查日志
   docker-compose logs web
   
   # 检查数据库连接
   docker-compose exec web python manage.py shell
   ```

2. **静态文件404**
   ```bash
   # 重新收集静态文件
   docker-compose exec web python manage.py collectstatic --noinput
   ```

3. **数据库连接失败**
   ```bash
   # 检查数据库服务
   docker-compose exec db pg_isready -U oj_user -d django_oj
   ```

## 📝 **部署后检查清单**

- [ ] 所有服务正常运行
- [ ] 数据库连接正常
- [ ] 静态文件加载正常
- [ ] SSL证书配置正确
- [ ] 防火墙配置完成
- [ ] 备份策略设置
- [ ] 监控系统配置
- [ ] 日志轮转配置

## 🆘 **紧急情况处理**

### 数据备份恢复
```bash
# 备份数据库
docker-compose exec db pg_dump -U oj_user django_oj > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U oj_user django_oj < backup.sql
```

### 服务重启
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart web
```
