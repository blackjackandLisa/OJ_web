# 📦 Django OJ - 依赖文件说明

## 📋 **依赖文件总览**

项目包含三个主要的依赖文件，针对不同的使用场景：

| 文件 | 用途 | 使用场景 |
|-----|------|---------|
| `requirements.txt` | 基础依赖 | 所有环境的核心依赖 |
| `requirements-linux.txt` | Linux生产环境 | Docker部署、Linux服务器 |
| `requirements-dev.txt` | 开发环境 | 本地开发、测试 |

---

## 📄 **requirements.txt - 基础依赖**

### **用途**
- 包含所有环境都需要的核心依赖
- 适用于基本的Django应用运行
- Windows/macOS/Linux通用

### **主要依赖**
```
Django==4.2.24              # Django框架
djangorestframework==3.16.0 # REST API
Pillow==10.2.0             # 图像处理
psutil==5.9.8              # 系统监控
markdown==3.5.2            # Markdown支持
```

### **安装方法**
```bash
pip install -r requirements.txt
```

---

## 🐧 **requirements-linux.txt - Linux生产环境**

### **用途**
- Linux服务器Docker部署
- 生产环境完整依赖
- 包含数据库、缓存、判题系统支持

### **主要依赖分类**

#### **1. 数据库支持**
```
psycopg2-binary==2.9.9     # PostgreSQL (推荐)
# mysqlclient==2.2.4       # MySQL (可选)
```

#### **2. 缓存和会话**
```
redis==5.0.1               # Redis客户端
django-redis==5.4.0        # Django Redis缓存
```

#### **3. 生产服务器**
```
gunicorn==21.2.0           # WSGI服务器
whitenoise==6.6.0          # 静态文件服务
```

#### **4. 判题系统**
```
docker==7.0.0              # Docker SDK (安全沙箱)
psutil==5.9.8              # 系统资源监控
```

#### **5. 工具库**
```
markdown==3.5.2            # Markdown解析
requests==2.31.0           # HTTP请求
```

### **安装方法**
```bash
# 在Docker中自动安装
docker-compose up -d

# 或手动安装
pip install -r requirements-linux.txt
```

---

## 💻 **requirements-dev.txt - 开发环境**

### **用途**
- 本地开发环境
- 代码质量检查
- 单元测试

### **主要依赖分类**

#### **1. 开发工具**
```
django-extensions==3.2.3   # Django扩展命令
django-debug-toolbar==4.4.0 # 调试工具栏
```

#### **2. 代码质量**
```
pylint==3.0.3              # 代码检查
flake8==7.0.0              # 风格检查
black==24.1.1              # 代码格式化
```

#### **3. 测试框架**
```
pytest==7.4.4              # 测试框架
pytest-django==4.7.0       # Django测试插件
pytest-cov==4.1.0          # 测试覆盖率
factory-boy==3.3.0         # 测试数据工厂
```

### **安装方法**
```bash
# 包含基础依赖 + 开发工具
pip install -r requirements-dev.txt
```

---

## 🚀 **不同场景的安装指南**

### **场景1: Windows本地开发**
```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装开发依赖
pip install -r requirements-dev.txt
```

### **场景2: Linux本地开发**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -r requirements-dev.txt
```

### **场景3: Docker生产部署**
```bash
# Dockerfile中自动安装
# COPY requirements-linux.txt .
# RUN pip install -r requirements-linux.txt

# 使用docker-compose部署
docker-compose up -d
```

### **场景4: Linux生产服务器（非Docker）**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装生产依赖
pip install -r requirements-linux.txt
```

---

## 📊 **核心依赖版本说明**

### **Django生态**
- **Django 4.2.24**: LTS版本，长期支持
- **DRF 3.16.0**: REST API框架最新稳定版
- **django-cors-headers 4.8.0**: CORS支持

### **数据库**
- **psycopg2-binary 2.9.9**: PostgreSQL适配器（生产推荐）
- **mysqlclient 2.2.4**: MySQL适配器（可选）

### **缓存**
- **redis 5.0.1**: Redis客户端
- **django-redis 5.4.0**: Django Redis缓存后端

### **判题系统**
- **docker 7.0.0**: Docker SDK，用于容器化代码执行
- **psutil 5.9.8**: 系统监控，资源限制

### **生产服务器**
- **gunicorn 21.2.0**: WSGI HTTP服务器
- **whitenoise 6.6.0**: 静态文件服务

---

## 🔄 **依赖更新策略**

### **检查过时的包**
```bash
pip list --outdated
```

### **更新所有包**
```bash
# 更新pip
pip install --upgrade pip

# 更新所有依赖
pip install --upgrade -r requirements-linux.txt
```

### **生成最新的依赖列表**
```bash
# 生成当前环境的依赖
pip freeze > requirements-current.txt

# 对比差异
diff requirements.txt requirements-current.txt
```

---

## ⚠️ **常见问题**

### **问题1: psycopg2安装失败**
```bash
# 解决方案：使用二进制版本
pip install psycopg2-binary
```

### **问题2: Pillow安装失败**
```bash
# Ubuntu/Debian
sudo apt-get install libjpeg-dev zlib1g-dev

# CentOS/RHEL
sudo yum install libjpeg-devel zlib-devel
```

### **问题3: mysqlclient安装失败**
```bash
# Ubuntu/Debian
sudo apt-get install default-libmysqlclient-dev

# CentOS/RHEL
sudo yum install mysql-devel
```

### **问题4: Docker SDK安装失败**
```bash
# 确保Docker已安装并运行
docker --version

# 重新安装Docker SDK
pip install docker --upgrade
```

### **问题5: externally-managed-environment错误**
```bash
# Ubuntu 23.04+系统
pip install --break-system-packages -r requirements.txt

# 或移除保护
sudo rm /usr/lib/python*/EXTERNALLY-MANAGED
```

---

## 🔒 **安全考虑**

### **固定版本**
- 所有依赖都固定版本，确保可重现性
- 避免自动升级导致的兼容性问题

### **定期更新**
- 每月检查安全更新
- 关注Django安全公告
- 及时修复已知漏洞

### **生产环境**
```bash
# 只安装必要的依赖
pip install -r requirements-linux.txt

# 不安装开发工具
# 避免安装 django-debug-toolbar 等调试工具
```

---

## 📝 **自定义依赖**

### **添加新依赖**
1. 安装并测试
   ```bash
   pip install package-name==version
   ```

2. 添加到相应文件
   ```bash
   # 基础依赖
   echo "package-name==version" >> requirements.txt
   
   # 或生产依赖
   echo "package-name==version" >> requirements-linux.txt
   ```

3. 更新文档
   - 在本文件中说明用途
   - 更新部署文档

### **移除依赖**
1. 从文件中删除
2. 卸载包
   ```bash
   pip uninstall package-name
   ```
3. 测试应用功能

---

## 🛠️ **开发工具说明**

### **代码质量工具**

#### **Pylint** - 代码检查
```bash
pylint --load-plugins pylint_django --django-settings-module=oj_system.settings **/*.py
```

#### **Flake8** - 风格检查
```bash
flake8 --max-line-length=120 .
```

#### **Black** - 代码格式化
```bash
black --line-length=120 .
```

### **测试工具**

#### **Pytest** - 运行测试
```bash
pytest
```

#### **Coverage** - 测试覆盖率
```bash
pytest --cov=. --cov-report=html
```

---

## 📚 **参考资源**

- [Django文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Gunicorn文档](https://docs.gunicorn.org/)
- [Docker SDK for Python](https://docker-py.readthedocs.io/)
- [PostgreSQL适配器](https://www.psycopg.org/)

---

## 📄 **许可证**

所有依赖包遵循各自的开源许可证。
