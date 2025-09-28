# 🛡️ 判题系统安全沙箱指南

## 📊 **当前安全状况**

### ✅ **已实现的安全沙箱**

1. **Docker容器隔离**
   - ✅ 完整的Docker judger镜像
   - ✅ 非特权用户执行
   - ✅ 网络隔离（network_mode: none）
   - ✅ 只读文件系统
   - ✅ 资源限制（CPU、内存、文件大小）

2. **进程级沙箱**
   - ✅ 资源限制（CPU时间、内存、文件描述符）
   - ✅ 进程隔离
   - ✅ 安全进程组管理

3. **引擎工厂模式**
   - ✅ 自动选择最佳引擎
   - ✅ 支持多种判题引擎
   - ✅ 环境检测和回退机制

## 🔧 **安全配置说明**

### **1. Docker安全沙箱**

**特点：**
- 🛡️ **容器隔离** - 完全隔离的执行环境
- 🔒 **非特权用户** - 使用nobody用户执行
- 🌐 **网络隔离** - 禁用网络访问
- 📁 **文件系统保护** - 只读根文件系统
- ⚡ **资源限制** - CPU、内存、文件大小限制

**配置：**
```python
# 在docker.env中设置
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True
```

### **2. 进程级沙箱**

**特点：**
- 🔒 **资源限制** - 使用resource模块限制资源
- 🚫 **系统调用限制** - 限制危险系统调用
- ⏱️ **超时控制** - 严格的执行时间限制
- 💾 **内存控制** - 内存使用量监控

**配置：**
```python
# 在docker.env中设置
JUDGE_ENGINE=sandbox
SANDBOX_ENABLED=True
```

### **3. 基础引擎（开发环境）**

**特点：**
- ⚠️ **仅限开发** - 不推荐生产环境使用
- 🔧 **简单实现** - 基本的进程管理
- 🚨 **安全风险** - 缺乏完整隔离

## 🚀 **部署配置**

### **生产环境（推荐Docker）**

```bash
# 1. 构建Docker judger镜像
python manage.py build_judger

# 2. 配置环境变量
echo "JUDGE_ENGINE=docker" >> docker.env
echo "SANDBOX_ENABLED=True" >> docker.env

# 3. 重启服务
docker-compose restart web
```

### **开发环境（进程沙箱）**

```bash
# 配置环境变量
echo "JUDGE_ENGINE=sandbox" >> docker.env
echo "SANDBOX_ENABLED=True" >> docker.env
```

## 🧪 **安全测试**

### **运行安全测试**

```bash
# 测试所有判题引擎
python scripts/test_judge_security.py

# 测试Docker连接
python manage.py shell -c "from judge.docker_engine import DockerJudgeEngine; print(DockerJudgeEngine().test_connection())"
```

### **测试项目**

1. **恶意代码防护**
   - 文件系统访问测试
   - 网络访问测试
   - 系统命令执行测试
   - 无限循环测试

2. **资源限制测试**
   - 内存消耗测试
   - CPU消耗测试
   - 文件大小限制测试

3. **隔离性测试**
   - 进程隔离验证
   - 文件系统隔离验证
   - 网络隔离验证

## 📊 **安全级别对比**

| 引擎类型 | 隔离级别 | 安全等级 | 性能 | 适用场景 |
|----------|----------|----------|------|----------|
| **Docker** | 容器级 | ⭐⭐⭐⭐⭐ | 中等 | 生产环境 |
| **Sandbox** | 进程级 | ⭐⭐⭐⭐ | 高 | 开发环境 |
| **Basic** | 无隔离 | ⭐⭐ | 最高 | 仅开发测试 |

## 🔒 **安全特性详解**

### **Docker安全特性**

1. **容器隔离**
   ```dockerfile
   # 非特权用户
   USER judger
   
   # 网络隔离
   network_mode: none
   
   # 只读文件系统
   read_only: true
   
   # 资源限制
   mem_limit: 128m
   cpu_quota: 50000
   ```

2. **安全配置**
   ```dockerfile
   # 安全选项
   security_opt:
     - no-new-privileges:true
     - seccomp:unconfined
   
   # 临时文件系统
   tmpfs:
     /tmp: size=100m,noexec,nosuid,nodev
   ```

### **进程沙箱特性**

1. **资源限制**
   ```python
   # CPU时间限制
   resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit))
   
   # 内存限制
   resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
   
   # 文件大小限制
   resource.setrlimit(resource.RLIMIT_FSIZE, (100*1024*1024, 100*1024*1024))
   ```

2. **进程管理**
   ```python
   # 进程组隔离
   preexec_fn=os.setsid
   
   # 超时控制
   process.communicate(timeout=time_limit)
   
   # 强制终止
   os.killpg(os.getpgid(process.pid), signal.SIGTERM)
   ```

## 🚨 **安全风险与防护**

### **已防护的风险**

1. **代码注入** ✅
   - 容器隔离防止系统访问
   - 进程沙箱限制系统调用

2. **文件系统攻击** ✅
   - 只读文件系统保护
   - 临时目录隔离

3. **网络攻击** ✅
   - 网络完全隔离
   - 禁用网络访问

4. **资源滥用** ✅
   - 严格的资源限制
   - 实时监控和终止

5. **进程逃逸** ✅
   - 容器级隔离
   - 进程组管理

### **持续监控建议**

1. **日志监控**
   ```bash
   # 查看判题日志
   docker-compose logs -f web | grep "judge"
   ```

2. **资源监控**
   ```bash
   # 监控容器资源使用
   docker stats django-oj-web
   ```

3. **安全审计**
   ```bash
   # 定期运行安全测试
   python scripts/test_judge_security.py
   ```

## 📝 **最佳实践**

### **生产环境配置**

1. **使用Docker引擎**
   ```bash
   JUDGE_ENGINE=docker
   SANDBOX_ENABLED=True
   ```

2. **定期更新镜像**
   ```bash
   docker build -t django-oj-judger:latest ./docker/judger/
   ```

3. **监控和日志**
   - 启用详细日志记录
   - 监控资源使用情况
   - 定期安全审计

### **开发环境配置**

1. **使用沙箱引擎**
   ```bash
   JUDGE_ENGINE=sandbox
   SANDBOX_ENABLED=True
   ```

2. **安全测试**
   - 定期运行安全测试
   - 验证隔离效果
   - 检查资源限制

## 🎯 **总结**

✅ **判题系统已实现完整的安全沙箱**
✅ **支持Docker容器隔离和进程级沙箱**
✅ **提供多种安全级别选择**
✅ **包含完整的安全测试套件**

**推荐配置：**
- **生产环境**：Docker引擎 + 容器隔离
- **开发环境**：Sandbox引擎 + 进程沙箱
- **测试环境**：Basic引擎（仅限安全测试）

您的判题系统现在已经具备了企业级的安全防护能力！🛡️
