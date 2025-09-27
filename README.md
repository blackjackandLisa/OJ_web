# Django Online Judge System

一个基于Django开发的在线评测系统(OJ)，支持多种编程语言的代码提交和评测。

## ✨ 主要特性

### 🎯 核心功能
- **题目管理**: 支持题目的增删改查，Markdown格式题目导入
- **代码评测**: 支持Python、C++、C、Java、JavaScript等多种语言
- **提交记录**: 完整的提交历史和评测结果展示
- **用户系统**: 用户注册、登录、个人信息管理
- **排行榜**: 用户积分和排名统计

### 🚀 高级功能
- **智能代码模板**: 全局模板和题目专用模板系统
- **实时搜索**: 题目列表实时搜索功能
- **代码编辑器**: 集成CodeMirror，支持语法高亮和多主题
- **竞赛系统**: 支持创建和管理编程竞赛
- **系统监控**: 实时系统状态监控
- **安全沙箱**: 跨平台代码执行沙箱环境

### 🎨 用户体验
- **响应式设计**: 适配各种屏幕尺寸
- **现代化UI**: Bootstrap + Font Awesome图标
- **新手引导**: 交互式用户指南
- **快捷键支持**: 提升编码效率
- **用户偏好**: 自动保存个人设置

## 🛠️ 技术栈

### 后端
- **Django 4.2**: Web框架
- **Django REST Framework**: API开发
- **SQLite**: 数据库
- **Celery**: 异步任务队列

### 前端
- **Bootstrap 5**: UI框架
- **jQuery**: JavaScript库
- **CodeMirror**: 代码编辑器
- **Font Awesome**: 图标库

### 评测系统
- **多语言支持**: Python, C++, C, Java, JavaScript
- **Docker容器**: 安全隔离的代码执行环境
- **进程沙箱**: Windows/Linux跨平台支持
- **资源限制**: 时间、内存、文件大小限制

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Django 4.2+
- Docker (可选，用于容器化评测)

### 安装步骤

#### 方法1：使用虚拟环境（推荐）

**Windows开发环境：**
```bash
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web
setup-dev.bat  # 自动设置开发环境
```

**Linux服务器部署：**
```bash
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web
chmod +x deploy-linux.sh
./deploy-linux.sh  # 自动部署到生产环境
```

**手动安装：**
```bash
# 1. 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt  # 基础依赖
# 或
pip install -r requirements-linux.txt  # 生产环境依赖

# 5. 数据库迁移
python manage.py migrate

# 6. 创建超级用户
python manage.py createsuperuser

# 7. 创建默认模板
python manage.py create_default_templates

# 8. 启动服务
python manage.py runserver
```

#### 方法2：使用Docker（一键部署）

```bash
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web
docker-compose up -d
```

访问 `http://localhost:8000` 即可使用系统。

### Docker部署（可选）

1. **构建评测镜像**
```bash
python manage.py build_judger
```

2. **配置Docker**
在 `settings.py` 中设置：
```python
JUDGE_ENGINE = 'docker'
JUDGE_DOCKER_IMAGE = 'oj-judger:latest'
```

## 📚 使用指南

### 管理员操作

1. **题目管理**
   - 进入Django管理后台 `/admin/`
   - 在"题目"部分添加新题目
   - 支持Markdown格式导入

2. **模板管理**
   - 创建全局代码模板
   - 为特定题目配置专用模板
   - 批量导入/导出模板

3. **用户管理**
   - 查看用户列表和统计信息
   - 管理用户权限

### 普通用户操作

1. **做题流程**
   - 浏览题目列表
   - 查看题目详情
   - 选择代码模板
   - 编写代码并提交
   - 查看评测结果

2. **个人中心**
   - 查看个人信息
   - 修改密码
   - 查看提交历史
   - 查看排名

## 🏗️ 项目结构

```
django-oj-system/
├── accounts/           # 用户系统
├── problems/           # 题目管理
├── submissions/        # 提交记录
├── judge/             # 评测系统
├── contests/          # 竞赛系统
├── monitor/           # 系统监控
├── templates/         # 模板文件
├── static/           # 静态文件
├── media/            # 媒体文件
├── docker/           # Docker配置
└── scripts/          # 辅助脚本
```

## 🔧 配置说明

### 评测系统配置

在 `settings.py` 中可以配置：

```python
# 评测引擎类型: 'process' 或 'docker'
JUDGE_ENGINE = 'process'

# Docker配置（如果使用Docker）
JUDGE_DOCKER_IMAGE = 'oj-judger:latest'
JUDGE_CONTAINER_TIMEOUT = 30

# 沙箱配置
JUDGE_SANDBOX_DIR = 'sandbox_tmp'
JUDGE_DEFAULT_TIME_LIMIT = 1000  # ms
JUDGE_DEFAULT_MEMORY_LIMIT = 256  # MB
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 开发计划

- [ ] WebSocket实时评测结果推送
- [ ] 多语言界面支持
- [ ] 题目难度智能评估
- [ ] 代码相似度检测
- [ ] 移动端适配优化
- [ ] 分布式评测集群

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Django](https://www.djangoproject.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - UI框架
- [CodeMirror](https://codemirror.net/) - 代码编辑器
- [Font Awesome](https://fontawesome.com/) - 图标库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件到: your-email@example.com

---

⭐ 如果这个项目对您有帮助，请给它一个星标！