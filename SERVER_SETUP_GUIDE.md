# 🖥️ Django OJ - 服务器配置和访问指南

## 📋 **目录**
- [数据库配置](#数据库配置)
- [部署步骤](#部署步骤)
- [访问方式](#访问方式)
- [管理员设置](#管理员设置)
- [常见问题](#常见问题)

---

## 🐘 **数据库配置**

### **好消息：数据库自动配置！**

在简化部署方案中，**PostgreSQL数据库会自动创建和配置**，您无需手动操作！

### **自动化流程：**

```
1. docker-compose启动PostgreSQL容器
   ↓
2. 自动创建数据库 "django_oj"
   ↓
3. 自动创建用户 "oj_user"
   ↓
4. Django自动连接数据库
   ↓
5. 自动运行数据库迁移
   ↓
6. 完成！
```

### **数据库信息：**

| 配置项 | 值 | 说明 |
|-------|-----|------|
| **数据库名** | `django_oj` | 自动创建 |
| **用户名** | `oj_user` | 自动创建 |
| **密码** | `oj_password` | 建议修改 |
| **主机** | `db` | Docker内部 |
| **端口** | `5432` | 容器内部 |

### **修改数据库密码（可选但推荐）：**

```bash
# 在部署前修改docker.env
nano docker.env

# 修改这一行：
POSTGRES_PASSWORD=your_strong_password_here
```

**生成强密码：**
```bash
openssl rand -base64 32
```

---

## 🚀 **部署步骤（完整版）**

### **步骤1：准备服务器**

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | sh

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

### **步骤2：获取项目**

```bash
# 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 或手动下载
wget https://github.com/blackjackandLisa/OJ_web/archive/refs/heads/main.zip
unzip main.zip
cd OJ_web-main
```

### **步骤3：配置环境变量**

```bash
# 编辑配置文件
nano docker.env
```

**必须修改的配置：**

```bash
# 1. 生成SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# 复制输出结果

# 2. 在docker.env中修改：
SECRET_KEY=<刚才生成的密钥>
POSTGRES_PASSWORD=<设置强密码>
ALLOWED_HOSTS=<服务器IP>,localhost,127.0.0.1

# 例如：
SECRET_KEY=5j=_+u7e7fstqt4h196p!n$3xt2fka2qdx_7%h9+$%nhad6o(
POSTGRES_PASSWORD=MyStr0ng_P@ssw0rd_2024
ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1
```

**保存并退出：** `Ctrl+X`, `Y`, `Enter`

### **步骤4：一键部署**

```bash
# 执行部署脚本
chmod +x deploy-simple.sh
./deploy-simple.sh
```

**部署过程：**
```
✓ 检查Docker环境
✓ 构建Docker镜像
✓ 启动PostgreSQL数据库
✓ 启动Django应用
✓ 自动运行数据库迁移
✓ 创建默认代码模板
✓ 收集静态文件
✓ 提示创建管理员账号
```

### **步骤5：创建管理员账号**

部署脚本会提示：
```
是否创建管理员账号？(y/n)
```

输入 `y`，然后按提示输入：
```
Username: admin
Email: admin@example.com
Password: ********
Password (again): ********
```

---

## 🌐 **访问方式**

### **方式1：本地访问（在服务器上）**

```bash
# 使用curl测试
curl http://localhost:8000

# 或使用浏览器（如果服务器有桌面）
firefox http://localhost:8000
```

### **方式2：局域网访问**

**在同一局域网的其他设备上：**

```
http://服务器IP:8000
```

**查找服务器IP：**
```bash
# 在服务器上执行
hostname -I
# 或
ip addr show | grep inet
```

**示例：**
```
服务器IP: 192.168.1.100
访问地址: http://192.168.1.100:8000
```

### **方式3：公网访问（如果有公网IP）**

```
http://公网IP:8000
```

**注意：** 需要在云服务器控制台开放8000端口

### **访问地址总结：**

| 访问类型 | 地址 | 示例 |
|---------|------|------|
| **Web界面** | `http://服务器IP:8000` | `http://192.168.1.100:8000` |
| **管理后台** | `http://服务器IP:8000/admin` | `http://192.168.1.100:8000/admin` |
| **API接口** | `http://服务器IP:8000/api` | `http://192.168.1.100:8000/api` |

---

## 👤 **管理员设置**

### **创建管理员（如果部署时跳过了）**

```bash
docker-compose exec web python manage.py createsuperuser
```

按提示输入：
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

### **登录管理后台**

1. 打开浏览器访问：`http://服务器IP:8000/admin`
2. 输入管理员用户名和密码
3. 点击"登录"

### **管理后台功能：**

- ✅ 用户管理
- ✅ 题目管理
- ✅ 提交记录查看
- ✅ 判题配置
- ✅ 代码模板管理

---

## 🔌 **端口配置**

### **当前配置：**

```yaml
# docker-compose.yml
ports:
  - "8000:8000"  # 主机端口:容器端口
```

### **修改端口（如果8000被占用）：**

```bash
# 编辑docker-compose.yml
nano docker-compose.yml

# 修改为其他端口，例如：
ports:
  - "8080:8000"  # 使用8080端口

# 保存后重新部署
docker-compose down
docker-compose up -d
```

### **防火墙配置：**

**Ubuntu/Debian:**
```bash
# 开放8000端口
sudo ufw allow 8000/tcp
sudo ufw enable
sudo ufw status
```

**CentOS/RHEL:**
```bash
# 开放8000端口
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**云服务器（阿里云/腾讯云/AWS）：**
- 在安全组规则中添加入站规则
- 协议：TCP
- 端口：8000
- 来源：0.0.0.0/0（所有IP）

---

## 📊 **数据库管理**

### **查看数据库状态：**

```bash
# 检查数据库容器
docker-compose ps db

# 查看数据库日志
docker-compose logs db
```

### **连接数据库（命令行）：**

```bash
# 进入数据库容器
docker-compose exec db psql -U oj_user -d django_oj

# 在psql中执行SQL
\dt              # 查看所有表
\d problems_problem  # 查看表结构
SELECT * FROM auth_user;  # 查询用户
\q               # 退出
```

### **使用数据库管理工具：**

**推荐工具：** DBeaver, pgAdmin, DataGrip

**连接信息：**
```
Host: 服务器IP
Port: 5432（需要在docker-compose.yml中暴露）
Database: django_oj
Username: oj_user
Password: oj_password（您设置的密码）
```

**如需外部访问数据库：**

```yaml
# 编辑docker-compose.yml
db:
  ports:
    - "5432:5432"  # 添加这一行
```

**注意：** 生产环境不建议暴露数据库端口！

---

## 🔒 **安全检查**

### **部署后必做的安全检查：**

- [ ] SECRET_KEY已修改为随机值
- [ ] POSTGRES_PASSWORD已设置强密码
- [ ] ALLOWED_HOSTS已配置为实际IP
- [ ] DEBUG=False（生产环境）
- [ ] 防火墙已配置
- [ ] 管理员密码强度足够

### **验证配置：**

```bash
# 检查环境变量
cat docker.env | grep SECRET_KEY
cat docker.env | grep POSTGRES_PASSWORD
cat docker.env | grep ALLOWED_HOSTS
cat docker.env | grep DEBUG
```

---

## ❓ **常见问题**

### **Q1: 无法访问8000端口**

**检查步骤：**
```bash
# 1. 检查服务是否运行
docker-compose ps

# 2. 检查端口是否监听
netstat -tuln | grep 8000

# 3. 检查防火墙
sudo ufw status

# 4. 查看日志
docker-compose logs web
```

### **Q2: 数据库连接失败**

**解决方案：**
```bash
# 1. 检查数据库容器
docker-compose ps db

# 2. 重启数据库
docker-compose restart db

# 3. 查看数据库日志
docker-compose logs db

# 4. 检查密码是否一致
cat docker.env | grep POSTGRES_PASSWORD
```

### **Q3: 忘记管理员密码**

**重置密码：**
```bash
# 进入Django shell
docker-compose exec web python manage.py shell

# 重置密码
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin = User.objects.get(username='admin')
>>> admin.set_password('new_password')
>>> admin.save()
>>> exit()
```

### **Q4: 如何查看服务器IP？**

```bash
# 内网IP
hostname -I

# 外网IP
curl ifconfig.me
curl ipinfo.io/ip
```

### **Q5: 如何停止服务？**

```bash
# 停止但保留数据
docker-compose down

# 停止并删除所有数据
docker-compose down -v
```

---

## 📝 **完整配置示例**

### **docker.env 配置示例：**

```bash
# Django配置
SECRET_KEY=5j=_+u7e7fstqt4h196p!n$3xt2fka2qdx_7%h9+$%nhad6o(
DEBUG=False
ALLOWED_HOSTS=192.168.1.100,123.45.67.89,localhost,127.0.0.1

# 数据库配置
DATABASE_URL=postgresql://oj_user:MyStr0ng_P@ssw0rd@db:5432/django_oj
POSTGRES_DB=django_oj
POSTGRES_USER=oj_user
POSTGRES_PASSWORD=MyStr0ng_P@ssw0rd
POSTGRES_HOST=db
POSTGRES_PORT=5432

# 安全配置
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# 判题系统配置
JUDGE_ENGINE=sandbox
SANDBOX_ENABLED=True
```

---

## 🎯 **快速参考**

### **部署命令：**
```bash
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web
nano docker.env  # 修改配置
chmod +x deploy-simple.sh
./deploy-simple.sh
```

### **访问地址：**
```
Web: http://服务器IP:8000
Admin: http://服务器IP:8000/admin
```

### **常用命令：**
```bash
# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f web

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

---

## 🎉 **完成！**

按照本指南配置后，您应该能够：

- ✅ 自动配置PostgreSQL数据库
- ✅ 通过IP地址访问OJ系统
- ✅ 登录管理后台
- ✅ 管理题目和用户
- ✅ 使用判题功能

**祝您使用愉快！** 🚀
