# 📁 Django OJ - 项目结构说明

## 📋 **目录结构**

```
django_OJ_02/
├── 📂 judge/                      # 判题系统核心
│   ├── engine.py                  # 基础判题引擎
│   ├── docker_engine.py           # Docker容器判题引擎
│   ├── sandbox_engine.py          # 进程沙箱判题引擎
│   ├── engine_factory.py          # 判题引擎工厂
│   ├── models.py                  # 判题相关模型
│   ├── tasks.py                   # 异步判题任务
│   └── management/commands/       # 管理命令
│       ├── build_judger.py       # 构建Judger镜像
│       ├── init_judge_config.py  # 初始化判题配置
│       └── judge_worker.py       # 判题工作进程
│
├── 📂 problems/                   # 题目管理
│   ├── models.py                  # 题目、模板模型
│   ├── views.py                   # 题目视图
│   ├── serializers.py             # API序列化器
│   ├── admin.py                   # 管理后台配置
│   └── management/commands/       
│       └── create_default_templates.py  # 创建默认模板
│
├── 📂 submissions/                # 提交管理
│   ├── models.py                  # 提交模型
│   ├── views.py                   # 提交视图
│   └── admin.py                   # 管理后台配置
│
├── 📂 users/                      # 用户系统
│   ├── models.py                  # 用户模型
│   ├── views.py                   # 用户视图
│   ├── forms.py                   # 表单
│   └── admin.py                   # 管理后台配置
│
├── 📂 contests/                   # 竞赛系统
│   ├── models.py                  # 竞赛模型
│   ├── views.py                   # 竞赛视图
│   └── admin.py                   # 管理后台配置
│
├── 📂 templates/                  # 模板文件
│   ├── base.html                  # 基础模板
│   ├── 📂 problems/              # 题目相关模板
│   │   ├── list.html             # 题目列表
│   │   ├── detail.html           # 题目详情
│   │   └── submit.html           # 代码提交
│   ├── 📂 submissions/           # 提交相关模板
│   │   ├── list.html             # 提交列表
│   │   └── detail.html           # 提交详情
│   ├── 📂 users/                 # 用户相关模板
│   │   ├── login.html            # 登录
│   │   ├── register.html         # 注册
│   │   └── profile.html          # 个人中心
│   └── 📂 contests/              # 竞赛相关模板
│       ├── list.html             # 竞赛列表
│       └── detail.html           # 竞赛详情
│
├── 📂 static/                     # 静态文件
│   ├── 📂 css/                   # 样式文件
│   ├── 📂 js/                    # JavaScript文件
│   └── 📂 images/                # 图片资源
│
├── 📂 media/                      # 媒体文件
│   └── 📂 avatars/               # 用户头像
│
├── 📂 docker/                     # Docker配置
│   └── 📂 judger/                # 判题容器
│       ├── Dockerfile            # Judger镜像定义
│       ├── entrypoint.py         # 容器入口脚本
│       └── limits.conf           # 资源限制配置
│
├── 📂 scripts/                    # 部署和工具脚本
│   ├── build_judger.sh           # 构建Judger镜像
│   ├── init_database.sh          # 初始化数据库
│   ├── diagnose-network.sh       # 网络诊断工具
│   └── check-docker.sh           # Docker环境检查
│
├── 📂 oj_system/                  # Django项目配置
│   ├── settings.py               # 项目设置
│   ├── urls.py                   # URL路由
│   └── wsgi.py                   # WSGI入口
│
├── 📄 Dockerfile                  # 主应用Docker镜像
├── 📄 docker-compose.yml          # Docker Compose配置
├── 📄 docker.env                  # 环境变量配置
├── 📄 nginx.conf                  # Nginx配置
│
├── 📄 deploy.sh                   # 统一部署脚本
├── 📄 requirements.txt            # Python依赖（通用）
├── 📄 requirements-linux.txt      # Python依赖（Linux）
│
├── 📄 manage.py                   # Django管理脚本
│
└── 📚 文档/
    ├── README.md                  # 项目说明
    ├── DEPLOYMENT_GUIDE.md        # 部署指南
    ├── JUDGE_SYSTEM_GUIDE.md      # 判题系统指南
    ├── JUDGE_SECURITY_GUIDE.md    # 安全指南
    ├── DOCKER_DEPLOYMENT_CHECKLIST.md  # 部署检查清单
    ├── PRODUCTION_SECURITY.md     # 生产安全配置
    └── PROJECT_STRUCTURE.md       # 本文件
```

---

## 🔍 **核心模块说明**

### **1. 判题系统 (judge/)**

#### **引擎架构**

```python
# 引擎工厂模式
JudgeEngineFactory
    ├── DockerJudgeEngine      # Docker容器判题（生产推荐）
    ├── SandboxEngine          # 进程沙箱判题（开发推荐）
    └── JudgeEngine            # 基础判题（测试用）
```

#### **核心文件**

- **`engine_factory.py`**: 判题引擎工厂，自动选择最佳引擎
- **`docker_engine.py`**: Docker容器判题引擎，最高安全性
- **`sandbox_engine.py`**: 进程级沙箱引擎，良好安全性
- **`engine.py`**: 基础判题引擎，跨平台支持
- **`models.py`**: 判题相关数据模型
  - `JudgeConfig`: 编程语言配置
  - `JudgeQueue`: 判题队列
  - `JudgeResult`: 判题结果
- **`tasks.py`**: 异步判题任务处理

#### **管理命令**

- **`build_judger.py`**: 构建Docker Judger镜像
- **`init_judge_config.py`**: 初始化判题配置
- **`judge_worker.py`**: 启动判题工作进程

### **2. 题目管理 (problems/)**

#### **核心文件**

- **`models.py`**: 题目相关模型
  - `Problem`: 题目信息
  - `GlobalTemplate`: 全局代码模板
  - `ProblemTemplate`: 题目专用模板
- **`views.py`**: 题目视图和API
  - 题目列表、详情、提交
  - 模板管理API
- **`admin.py`**: 管理后台配置

#### **功能特性**

- ✅ 题目增删改查
- ✅ Markdown格式支持
- ✅ 全局和题目专用模板
- ✅ 模板预览和应用
- ✅ 用户偏好保存

### **3. 提交管理 (submissions/)**

#### **核心文件**

- **`models.py`**: 提交模型
  - `Submission`: 代码提交记录
  - 关联题目、用户、判题结果
- **`views.py`**: 提交视图
  - 提交列表、详情
  - 重新提交
- **`admin.py`**: 管理后台配置

#### **功能特性**

- ✅ 完整的提交历史
- ✅ 评测结果展示
- ✅ 代码查看
- ✅ 运行时间和内存统计

### **4. 用户系统 (users/)**

#### **核心文件**

- **`models.py`**: 用户模型扩展
  - `UserProfile`: 用户资料
  - 头像、积分、排名
- **`views.py`**: 用户视图
  - 登录、注册、个人中心
- **`forms.py`**: 表单定义

#### **功能特性**

- ✅ 用户注册登录
- ✅ 个人信息管理
- ✅ 头像上传
- ✅ 积分和排名

### **5. 竞赛系统 (contests/)**

#### **核心文件**

- **`models.py`**: 竞赛模型
  - `Contest`: 竞赛信息
  - `ContestProblem`: 竞赛题目
  - `ContestSubmission`: 竞赛提交
- **`views.py`**: 竞赛视图

#### **功能特性**

- ✅ 竞赛创建和管理
- ✅ 竞赛题目
- ✅ 排行榜
- ✅ 时间限制

---

## 🐳 **Docker配置**

### **docker/judger/ - 安全判题容器**

```
docker/judger/
├── Dockerfile          # 判题容器镜像定义
├── entrypoint.py       # 容器入口脚本
└── limits.conf         # 资源限制配置
```

#### **安全特性**

- 🔒 非特权用户执行
- 🌐 网络隔离
- 📁 只读文件系统
- ⚡ CPU和内存限制
- 🛡️ 系统调用限制

### **主应用容器**

```
Dockerfile              # 主应用镜像
docker-compose.yml      # 服务编排
docker.env              # 环境变量
nginx.conf              # Nginx配置
```

#### **服务架构**

```yaml
services:
  web:      # Django应用
  db:       # PostgreSQL数据库
  redis:    # Redis缓存
  nginx:    # 反向代理
```

---

## 🛠️ **部署脚本**

### **scripts/ - 部署和工具脚本**

```
scripts/
├── build_judger.sh         # 构建Judger镜像
├── init_database.sh        # 初始化数据库
├── diagnose-network.sh     # 网络诊断和修复
└── check-docker.sh         # Docker环境检查
```

### **根目录脚本**

- **`deploy.sh`**: 统一部署脚本（推荐使用）
  - 自动检测环境
  - 选择最佳部署方案
  - 安装依赖
  - 启动服务

---

## 📝 **配置文件**

### **环境变量 (docker.env)**

```bash
# Django配置
SECRET_KEY=xxx
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com

# 数据库配置
DATABASE_URL=postgresql://user:pass@db:5432/django_oj
POSTGRES_DB=django_oj
POSTGRES_USER=oj_user
POSTGRES_PASSWORD=xxx

# Redis配置
REDIS_URL=redis://redis:6379/1

# 判题引擎配置
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True

# 安全配置
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

### **Nginx配置 (nginx.conf)**

```nginx
server {
    listen 80;
    
    # 静态文件
    location /static/ {
        alias /app/staticfiles/;
    }
    
    # 媒体文件
    location /media/ {
        alias /app/media/;
    }
    
    # Django应用
    location / {
        proxy_pass http://web:8000;
    }
}
```

---

## 📚 **文档结构**

### **用户文档**

- **`README.md`**: 项目总览和快速开始
- **`DEPLOYMENT_GUIDE.md`**: 详细的部署指南
- **`JUDGE_SYSTEM_GUIDE.md`**: 判题系统架构和配置

### **技术文档**

- **`JUDGE_SECURITY_GUIDE.md`**: 安全沙箱配置
- **`DOCKER_DEPLOYMENT_CHECKLIST.md`**: Docker部署检查清单
- **`PRODUCTION_SECURITY.md`**: 生产环境安全配置
- **`PROJECT_STRUCTURE.md`**: 项目结构说明（本文件）

---

## 🔄 **数据流程**

### **判题流程**

```
用户提交代码
    ↓
保存到Submission表
    ↓
添加到JudgeQueue队列
    ↓
JudgeEngineFactory选择引擎
    ↓
    ├─→ DockerJudgeEngine（容器执行）
    ├─→ SandboxEngine（进程执行）
    └─→ JudgeEngine（简单执行）
    ↓
执行代码并测试
    ↓
保存到JudgeResult表
    ↓
更新Submission状态
    ↓
返回结果给用户
```

### **模板流程**

```
用户打开提交页面
    ↓
加载题目专用模板
    ↓
如果没有，加载全局模板
    ↓
用户选择模板
    ↓
预览模板（CodeMirror）
    ↓
应用到编辑器
    ↓
保存用户偏好（localStorage）
```

---

## 🗄️ **数据库模型关系**

```
User (Django内置)
    ↓ 1:1
UserProfile
    ↓ 1:N
Submission ←─── Problem
    ↓ 1:1           ↓ 1:N
JudgeResult     ProblemTemplate
    
GlobalTemplate (独立)

Contest
    ↓ 1:N
ContestProblem ←─── Problem
    ↓ 1:N
ContestSubmission ←─── Submission

JudgeConfig (配置表)
JudgeQueue (队列表)
```

---

## 🚀 **扩展指南**

### **添加新的编程语言**

1. 在`JudgeConfig`中添加语言配置
2. 更新`docker/judger/Dockerfile`安装编译器
3. 在`docker/judger/entrypoint.py`中添加编译和运行逻辑
4. 创建默认模板

### **添加新的判题引擎**

1. 在`judge/`下创建新引擎文件
2. 继承基类并实现接口
3. 在`engine_factory.py`中注册
4. 更新配置文档

### **自定义题目类型**

1. 扩展`Problem`模型
2. 更新题目表单和序列化器
3. 修改题目模板
4. 实现特殊判题逻辑

---

## 📊 **性能优化**

### **数据库优化**

- 使用`select_related`和`prefetch_related`减少查询
- 添加数据库索引
- 使用Redis缓存热点数据

### **判题优化**

- 使用异步任务队列
- 并行执行测试用例
- 预编译常用语言环境

### **前端优化**

- 静态文件CDN加速
- 代码压缩和合并
- 懒加载和分页

---

## 🔒 **安全注意事项**

### **代码执行安全**

- ✅ 使用Docker容器隔离
- ✅ 限制资源使用
- ✅ 禁用网络访问
- ✅ 只读文件系统
- ✅ 非特权用户执行

### **Web应用安全**

- ✅ CSRF保护
- ✅ XSS过滤
- ✅ SQL注入防护
- ✅ 密码哈希存储
- ✅ HTTPS加密传输

---

## 📞 **支持与贡献**

- **Issue**: 提交问题和建议
- **PR**: 欢迎贡献代码
- **文档**: 帮助完善文档
- **测试**: 提交测试用例

---

## 📄 **许可证**

MIT License
