# 🔧 Docker网络问题修复指南

## ❌ 问题描述

部署时出现错误：
```
ERROR: Get "https://registry-1.docker.io/v2/": net/http: request canceled while waiting for connection
```

**原因：** Docker官方镜像源在国内访问速度慢或超时。

---

## ✅ 解决方案

### **方案一：使用修复脚本（推荐）⭐**

```bash
# 1. 添加执行权限
chmod +x fix-docker-registry.sh

# 2. 运行修复脚本
./fix-docker-registry.sh

# 3. 重新部署
./deploy-simple.sh
```

---

### **方案二：手动配置镜像加速**

#### **步骤1：创建Docker配置**

```bash
# 创建配置目录
sudo mkdir -p /etc/docker

# 编辑配置文件
sudo nano /etc/docker/daemon.json
```

#### **步骤2：添加镜像源配置**

复制以下内容到 `daemon.json`：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://docker.nastool.de",
    "https://docker.chenby.cn"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "max-concurrent-downloads": 10
}
```

**保存并退出：** `Ctrl+X`, `Y`, `Enter`

#### **步骤3：重启Docker**

```bash
# 重新加载配置
sudo systemctl daemon-reload

# 重启Docker服务
sudo systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

#### **步骤4：重新部署**

```bash
./deploy-simple.sh
```

---

### **方案三：预先拉取镜像**

如果镜像加速仍然失败，可以手动拉取镜像：

```bash
# 拉取PostgreSQL镜像
docker pull postgres:15-alpine

# 拉取Python镜像
docker pull python:3.11-slim

# 验证镜像
docker images
```

然后重新运行部署脚本。

---

### **方案四：修改docker-compose.yml使用国内镜像**

如果以上方案都不行，可以修改镜像源：

```bash
# 编辑docker-compose.yml
nano docker-compose.yml
```

**修改PostgreSQL镜像：**
```yaml
# 从这个：
image: postgres:15-alpine

# 改为（使用阿里云镜像）：
image: registry.cn-hangzhou.aliyuncs.com/library/postgres:15-alpine
```

---

## 🔍 验证Docker配置

### **检查镜像源配置：**

```bash
# 查看Docker信息
docker info

# 查看镜像源（应该看到配置的镜像列表）
docker info | grep -i mirror

# 测试拉取镜像
docker pull hello-world
```

### **检查网络连接：**

```bash
# 测试DNS
ping -c 4 8.8.8.8

# 测试Docker Hub连接
curl -I https://registry-1.docker.io/v2/

# 测试国内镜像源
curl -I https://docker.m.daocloud.io
```

---

## 📋 常见问题

### **Q1: 镜像源配置后仍然超时**

**解决方案：**
1. 检查服务器网络连接
2. 尝试使用代理
3. 使用离线镜像部署

### **Q2: Docker重启失败**

```bash
# 查看Docker状态
sudo systemctl status docker

# 查看错误日志
sudo journalctl -u docker -n 50

# 检查配置文件语法
cat /etc/docker/daemon.json | python3 -m json.tool
```

### **Q3: 如何使用代理？**

如果有代理服务器，配置Docker代理：

```bash
# 创建代理配置目录
sudo mkdir -p /etc/systemd/system/docker.service.d

# 创建代理配置
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf
```

添加内容：
```
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=http://proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1"
```

重启Docker：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

---

## 🌐 可用的国内Docker镜像源

| 镜像源 | 地址 | 速度 |
|--------|------|------|
| DaoCloud | https://docker.m.daocloud.io | ⭐⭐⭐⭐⭐ |
| 1Panel | https://docker.1panel.live | ⭐⭐⭐⭐⭐ |
| Rat.dev | https://hub.rat.dev | ⭐⭐⭐⭐ |
| NAS Tool | https://docker.nastool.de | ⭐⭐⭐⭐ |
| Chenby | https://docker.chenby.cn | ⭐⭐⭐⭐ |

---

## 🚀 快速修复命令（一键复制）

```bash
# 完整修复流程
sudo mkdir -p /etc/docker && \
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl daemon-reload && \
sudo systemctl restart docker && \
echo "✅ Docker镜像加速配置完成！"
```

---

## 📝 检查清单

修复后请确认：

- [ ] Docker服务正常运行 (`sudo systemctl status docker`)
- [ ] 镜像源配置生效 (`docker info | grep -i mirror`)
- [ ] 能够拉取镜像 (`docker pull hello-world`)
- [ ] 网络连接正常 (`ping 8.8.8.8`)

---

## 💡 后续步骤

配置完成后：

1. **重新部署：**
   ```bash
   ./deploy-simple.sh
   ```

2. **如果还有问题，查看详细日志：**
   ```bash
   docker-compose logs -f
   ```

3. **如果仍然失败，考虑：**
   - 使用离线部署
   - 在网络环境好的地方预先下载镜像
   - 咨询网络管理员

---

## 🎉 成功标志

当看到以下输出时表示成功：

```
✅ Django OJ系统超级简化部署完成！
请等待几秒钟，然后访问 http://您的服务器IP:8000
```
