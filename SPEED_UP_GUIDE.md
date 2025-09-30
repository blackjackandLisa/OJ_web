# 🚀 加速部署指南

## 📊 **当前情况分析**

您正在下载：
```
postgres:15-alpine (106.4MB)
当前进度: 21MB/106.4MB
速度: 较慢
```

**正在下载的内容：**
- PostgreSQL 15 数据库镜像（Alpine精简版）
- 这是OJ系统的核心数据库

---

## ⚡ **3种加速方法**

### **方法一：使用加速部署脚本（推荐）⭐**

**先停止当前下载，然后使用国内镜像源：**

```bash
# 1. 停止当前部署（按Ctrl+C）
# 然后执行：

# 2. 清理并使用加速脚本
docker-compose down
chmod +x speed-up-deployment.sh
./speed-up-deployment.sh
```

**优势：**
- ✅ 使用阿里云镜像源
- ✅ 下载速度提升 **10-50倍**
- ✅ 自动化处理所有步骤

---

### **方法二：手动使用国内镜像**

```bash
# 1. 停止当前部署（Ctrl+C）
docker-compose down

# 2. 使用阿里云镜像拉取
docker pull registry.cn-hangzhou.aliyuncs.com/library/postgres:15-alpine

# 3. 重新标记
docker tag registry.cn-hangzhou.aliyuncs.com/library/postgres:15-alpine postgres:15-alpine

# 4. 继续部署
./deploy-simple.sh
```

---

### **方法三：等待当前下载完成（不推荐）**

如果您不想中断：
- ⏱️ 预计还需 **5-20分钟**（取决于网络）
- 📊 当前进度：21MB/106.4MB (约20%)
- 💡 下载完成后会自动继续

**监控进度：**
```bash
# 在另一个终端查看
watch docker images
```

---

## 🎯 **推荐操作流程**

### **立即加速（推荐）：**

```bash
# 步骤1: 停止当前下载
按 Ctrl+C

# 步骤2: 清理
docker-compose down

# 步骤3: 拉取最新加速脚本
git pull origin main

# 步骤4: 使用加速脚本
chmod +x speed-up-deployment.sh
./speed-up-deployment.sh
```

### **或者手动加速：**

```bash
# 停止
Ctrl+C
docker-compose down

# 使用阿里云镜像（速度快）
docker pull registry.cn-hangzhou.aliyuncs.com/library/postgres:15-alpine
docker tag registry.cn-hangzhou.aliyuncs.com/library/postgres:15-alpine postgres:15-alpine

# 继续部署
./deploy-simple.sh
```

---

## 📦 **镜像大小参考**

| 镜像 | 大小 | 用途 |
|------|------|------|
| postgres:15-alpine | ~106MB | 数据库 |
| python:3.11-slim | ~130MB | Django应用 |
| **总计** | **~240MB** | 完整系统 |

---

## 🌐 **国内镜像源对比**

| 来源 | 速度 | 可靠性 |
|------|------|--------|
| **阿里云** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **腾讯云** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **DaoCloud** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Docker Hub | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## ⏱️ **速度对比**

### **使用Docker Hub（官方）：**
```
postgres:15-alpine (106MB)
速度: 0.1-0.5 MB/s
时间: 5-20分钟 ⚠️
```

### **使用阿里云镜像：**
```
postgres:15-alpine (106MB)
速度: 5-20 MB/s
时间: 10-30秒 ✅
```

**提速：10-50倍！** 🚀

---

## 💡 **为什么速度慢？**

1. **Docker Hub在国外**
   - 服务器在美国
   - 国内访问受限

2. **网络带宽限制**
   - Docker Hub对免费用户有速率限制
   - 高峰期更慢

3. **防火墙/代理**
   - 某些地区网络限制

---

## 🔧 **如果使用加速脚本后仍然慢**

### **检查网络：**
```bash
# 测试网速
curl -o /dev/null http://speedtest.tele2.net/100MB.zip

# 测试阿里云镜像连通性
curl -I https://registry.cn-hangzhou.aliyuncs.com

# 测试DNS
ping registry.cn-hangzhou.aliyuncs.com
```

### **临时解决方案：**

**使用更小的镜像：**
```bash
# 修改docker-compose.yml
nano docker-compose.yml

# 将 postgres:15-alpine 改为 postgres:15-alpine
# （已经是最小版本）

# 或使用SQLite（开发测试）
# 在docker.env中注释掉DATABASE_URL
```

---

## 📊 **下载进度说明**

当前显示的下载进度：
```
15-alpine: Pulling from library/postgres
9824c27679d3: Pull complete     ✅ Layer 1
13f83b31e777: Pull complete     ✅ Layer 2
06cd8c6c6a3a: Pull complete     ✅ Layer 3
fc2b15c27045: Pull complete     ✅ Layer 4
08a69ddf91e5: Pull complete     ✅ Layer 5
240908555035: Downloading [==>  ] 21MB/106.4MB  ⏳ 正在下载
ebe21bfc7d0e: Download complete ⏸️ 等待中
ced3635131f: Download complete  ⏸️ 等待中
...
```

**说明：**
- Docker镜像是分层下载的
- 正在下载第6层（最大的一层）
- 这一层包含PostgreSQL的主要程序文件

---

## 🎯 **最终建议**

### **如果时间紧急：**
```bash
Ctrl+C                          # 停止
docker-compose down             # 清理
./speed-up-deployment.sh        # 使用加速脚本
```

### **如果不着急：**
```bash
# 让它继续下载，大约还需 5-15 分钟
# 下载完成后会自动继续部署
```

### **如果经常部署：**
```bash
# 一次性配置Docker镜像加速
./fix-docker-registry.sh
# 以后所有镜像下载都会更快
```

---

## ✅ **成功标志**

当看到这些时表示下载完成：

```
✅ All layers downloaded
✅ Container django-oj-db is healthy
✅ Container django-oj-web started
✅ Django OJ系统部署完成！
```

---

## 📞 **需要帮助？**

如果遇到问题：

1. **查看完整日志：**
   ```bash
   docker-compose logs -f
   ```

2. **检查服务状态：**
   ```bash
   docker-compose ps
   ```

3. **重新开始：**
   ```bash
   docker-compose down -v
   ./speed-up-deployment.sh
   ```
