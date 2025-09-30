# 🔧 快速修复：镜像拉取被拒

## ❌ 问题

```
Error response from daemon: pull access denied for registry.cn-hangzhou.aliyuncs.com/library/postgres, 
repository does not exist or may require 'docker login': denied: requested access to the resource is denied
```

**原因：** 阿里云镜像源需要登录，但我们不需要这么麻烦！

---

## ✅ 立即解决方案

### **方案一：使用更新的脚本（推荐）⭐**

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 使用更新后的加速脚本（已修复，无需登录）
chmod +x speed-up-deployment.sh
./speed-up-deployment.sh
```

**新脚本会自动尝试多个公开镜像源：**
- 1Panel (docker.1panel.live)
- DaoCloud (docker.m.daocloud.io)
- 腾讯云 (mirror.ccs.tencentyun.com)
- Docker Hub (官方)

---

### **方案二：使用镜像拉取脚本**

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 先拉取镜像
chmod +x simple-pull-images.sh
./simple-pull-images.sh

# 3. 然后部署
./deploy-simple.sh
```

---

### **方案三：手动拉取（无需登录）**

```bash
# 停止当前操作
docker-compose down

# 尝试公开镜像源（按顺序尝试）
# 1. 尝试1Panel
docker pull docker.1panel.live/library/postgres:15-alpine && \
docker tag docker.1panel.live/library/postgres:15-alpine postgres:15-alpine

# 如果上面失败，尝试DaoCloud
# docker pull docker.m.daocloud.io/library/postgres:15-alpine && \
# docker tag docker.m.daocloud.io/library/postgres:15-alpine postgres:15-alpine

# 如果还失败，尝试腾讯云
# docker pull mirror.ccs.tencentyun.com/library/postgres:15-alpine && \
# docker tag mirror.ccs.tencentyun.com/library/postgres:15-alpine postgres:15-alpine

# 然后继续部署
./deploy-simple.sh
```

---

### **方案四：让原来的下载继续**

如果上述方案都不行，可以回到原来的方式：

```bash
# 使用已配置的Docker镜像加速继续下载
./deploy-simple.sh

# 虽然慢，但是稳定
# 预计还需要 5-15 分钟
```

---

## 🌐 **可用的公开镜像源**

| 镜像源 | 地址 | 需要登录 | 速度 |
|--------|------|---------|------|
| **1Panel** | docker.1panel.live | ❌ 否 | ⭐⭐⭐⭐⭐ |
| **DaoCloud** | docker.m.daocloud.io | ❌ 否 | ⭐⭐⭐⭐ |
| **腾讯云** | mirror.ccs.tencentyun.com | ❌ 否 | ⭐⭐⭐⭐ |
| 阿里云 | registry.cn-hangzhou.aliyuncs.com | ✅ 是 | ⭐⭐⭐⭐⭐ |
| Docker Hub | registry-1.docker.io | ❌ 否 | ⭐⭐ |

---

## 🎯 **推荐操作（最简单）**

```bash
# 在Linux服务器上执行：

# 步骤1: 拉取最新代码
git pull origin main

# 步骤2: 执行更新后的脚本（已修复）
chmod +x speed-up-deployment.sh
./speed-up-deployment.sh

# 完成！
```

---

## 📋 **详细步骤**

### **完整流程：**

```bash
# 1. 进入项目目录
cd OJ_web

# 2. 停止旧容器
docker-compose down

# 3. 拉取最新代码（包含修复）
git pull origin main

# 4. 使用更新后的脚本
chmod +x speed-up-deployment.sh
./speed-up-deployment.sh

# 5. 等待部署完成（1-5分钟）
```

---

## 🔍 **验证镜像**

部署完成后，检查镜像：

```bash
# 查看已下载的镜像
docker images | grep postgres

# 应该看到：
# postgres   15-alpine   xxxxx   xxxx ago   xxx MB
```

---

## ❓ **常见问题**

### **Q: 为什么阿里云镜像需要登录？**

A: 阿里云最近改变了策略，某些镜像仓库需要登录才能访问。我们改用其他公开镜像源。

### **Q: 如果所有镜像源都失败怎么办？**

A: 检查：
1. 网络连接：`ping 8.8.8.8`
2. 防火墙设置
3. 等待几分钟后重试
4. 使用原始部署脚本（虽然慢）

### **Q: 可以登录阿里云再使用吗？**

A: 可以，但不推荐（太麻烦）：
```bash
docker login --username=你的用户名 registry.cn-hangzhou.aliyuncs.com
# 然后再执行原脚本
```

---

## 📊 **性能对比**

| 方案 | 速度 | 需要登录 | 推荐度 |
|------|------|---------|--------|
| **1Panel镜像** | 5-15 MB/s | ❌ | ⭐⭐⭐⭐⭐ |
| **DaoCloud镜像** | 3-10 MB/s | ❌ | ⭐⭐⭐⭐ |
| 阿里云镜像 | 10-20 MB/s | ✅ | ⭐⭐⭐ |
| Docker Hub | 0.1-0.5 MB/s | ❌ | ⭐⭐ |

---

## ✅ **成功标志**

当看到以下输出时表示成功：

```bash
✅ PostgreSQL镜像准备完成！
✅ 所有镜像准备完成！
✅ 服务启动中...
🎉 部署完成！
```

---

## 🚀 **立即执行**

```bash
# 复制粘贴，一键执行
cd OJ_web && \
git pull origin main && \
chmod +x speed-up-deployment.sh && \
./speed-up-deployment.sh
```

**就这么简单！** 🎉
