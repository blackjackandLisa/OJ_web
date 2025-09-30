# 🛡️ Django OJ - 判题系统安全指南

## 📋 **目录**

- [系统架构](#系统架构)
- [安全沙箱](#安全沙箱)
- [判题引擎](#判题引擎)
- [配置指南](#配置指南)
- [安全特性](#安全特性)

---

## 系统架构

### **判题流程**

```
用户提交代码
    ↓
提交队列 (JudgeQueue)
    ↓
引擎工厂 (JudgeEngineFactory)
    ↓
    ├─→ Docker引擎 (DockerJudgeEngine)
    │   ├─→ Docker容器隔离
    │   ├─→ 资源限制
    │   └─→ 安全执行
    │
    ├─→ 沙箱引擎 (SandboxEngine)
    │   ├─→ 进程隔离
    │   ├─→ 资源限制
    │   └─→ 系统调用限制
    │
    └─→ 基础引擎 (JudgeEngine)
        └─→ 简单执行（仅开发）
    ↓
判题结果 (JudgeResult)
    ↓
返回用户
```

### **核心组件**

#### **1. 判题引擎工厂 (engine_factory.py)**
- 自动选择最佳判题引擎
- 支持多种引擎类型
- 环境检测和回退机制

#### **2. Docker判题引擎 (docker_engine.py)**
- 容器级别的完全隔离
- 最高级别的安全性
- 支持所有编程语言

#### **3. 沙箱判题引擎 (sandbox_engine.py)**
- 进程级别的隔离
- 资源限制和监控
- Linux系统支持

#### **4. 基础判题引擎 (engine.py)**
- 简单的进程管理
- 跨平台支持
- 仅供开发测试

---

## 安全沙箱

### **Docker安全沙箱 (推荐生产环境)**

#### **安全特性**

1. **容器隔离**
   - 完全独立的执行环境
   - 与主机系统完全隔离
   - 防止恶意代码影响宿主机

2. **非特权用户执行**
   ```dockerfile
   # 创建非特权用户
   RUN useradd -m judger
   USER judger
   ```

3. **网络隔离**
   ```python
   'network_mode': 'none',  # 完全禁用网络
   ```

4. **只读文件系统**
   ```python
   'read_only': True,  # 根文件系统只读
   'tmpfs': {
       '/tmp': 'size=100m,noexec,nosuid,nodev'
   }
   ```

5. **资源限制**
   ```python
   container_config = {
       'mem_limit': f'{memory_limit}m',      # 内存限制
       'memswap_limit': f'{memory_limit}m',  # 交换分区限制
       'cpu_quota': 50000,                   # CPU限制
       'cpu_period': 100000,
   }
   ```

6. **安全选项**
   ```python
   'security_opt': [
       'no-new-privileges:true',  # 禁止提权
       'seccomp:unconfined'       # 系统调用限制
   ]
   ```

#### **Dockerfile配置**

```dockerfile
# docker/judger/Dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc g++ default-jdk nodejs npm time \
    && rm -rf /var/lib/apt/lists/*

# 创建非特权用户
RUN useradd -m judger && \
    mkdir -p /sandbox && \
    chown judger:judger /sandbox

# 设置工作目录
WORKDIR /app

# 复制判题脚本
COPY entrypoint.py /app/
COPY limits.conf /etc/security/limits.d/judger.conf

# 切换到非特权用户
USER judger

# 设置入口点
ENTRYPOINT ["python", "/app/entrypoint.py"]
```

#### **资源限制配置**

```conf
# docker/judger/limits.conf
judger soft cpu 5
judger hard cpu 10
judger soft as 256000
judger hard as 512000
judger soft nproc 100
judger hard nproc 200
```

### **进程沙箱 (Linux开发环境)**

#### **安全特性**

1. **资源限制**
   ```python
   def set_resource_limits(time_limit: int, memory_limit: int):
       # CPU时间限制
       resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit + 1))
       
       # 内存限制
       memory_bytes = memory_limit * 1024 * 1024
       resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
       
       # 文件描述符限制
       resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))
   ```

2. **进程隔离**
   ```python
   process = subprocess.Popen(
       cmd,
       stdin=subprocess.PIPE,
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE,
       preexec_fn=os.setsid  # 创建新的进程组
   )
   ```

3. **超时控制**
   ```python
   try:
       stdout, stderr = process.communicate(
           input=input_data,
           timeout=time_limit
       )
   except subprocess.TimeoutExpired:
       os.killpg(os.getpgid(process.pid), signal.SIGKILL)
   ```

4. **内存监控**
   ```python
   ps_process = psutil.Process(process.pid)
   memory_info = ps_process.memory_info()
   max_memory = max(max_memory, memory_info.rss / 1024 / 1024)  # MB
   ```

---

## 判题引擎

### **引擎选择策略**

```python
# judge/engine_factory.py
class JudgeEngineFactory:
    @staticmethod
    def create_engine():
        engine_type = settings.JUDGE_ENGINE
        
        if engine_type == 'auto':
            if platform.system() == 'Windows':
                return JudgeEngine()
            else:
                try:
                    docker_engine = DockerJudgeEngine()
                    if docker_engine.test_connection():
                        return docker_engine
                    else:
                        return SandboxEngine()
                except:
                    return SandboxEngine()
        
        elif engine_type == 'docker':
            return DockerJudgeEngine()
        elif engine_type == 'sandbox':
            return SandboxEngine()
        else:
            return JudgeEngine()
```

### **引擎对比**

| 特性 | Docker引擎 | 沙箱引擎 | 基础引擎 |
|-----|----------|---------|---------|
| **安全性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **隔离级别** | 容器隔离 | 进程隔离 | 进程管理 |
| **资源限制** | 完善 | 良好 | 基础 |
| **网络隔离** | ✅ | ❌ | ❌ |
| **文件系统保护** | ✅ | ⚠️ | ❌ |
| **跨平台** | Linux | Linux | 全平台 |
| **性能开销** | 中等 | 低 | 最低 |
| **推荐环境** | 生产 | 开发 | 测试 |

---

## 配置指南

### **Docker引擎配置**

#### **1. 构建Judger镜像**

```bash
# 方法1: 使用管理命令
python manage.py build_judger

# 方法2: 手动构建
cd docker/judger
docker build -t django-oj-judger:latest .
```

#### **2. 配置环境变量**

```bash
# docker.env
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True
```

#### **3. 测试Docker引擎**

```bash
# 进入Django shell
python manage.py shell

# 测试引擎
>>> from judge.engine_factory import JudgeEngineFactory
>>> engine = JudgeEngineFactory.create_engine()
>>> print(type(engine).__name__)
DockerJudgeEngine
```

### **沙箱引擎配置**

#### **1. 配置环境变量**

```bash
# docker.env
JUDGE_ENGINE=sandbox
SANDBOX_ENABLED=True
```

#### **2. 确保系统支持**

```bash
# 检查资源限制支持
ulimit -a

# 检查进程隔离支持
ps aux | grep python
```

### **基础引擎配置**

```bash
# docker.env
JUDGE_ENGINE=basic
SANDBOX_ENABLED=False
```

---

## 安全特性

### **1. 代码执行安全**

#### **禁止的操作**
- ❌ 文件系统写入（只读模式）
- ❌ 网络访问（网络隔离）
- ❌ 系统调用（seccomp限制）
- ❌ 进程创建（资源限制）
- ❌ 特权提升（非特权用户）

#### **允许的操作**
- ✅ 标准输入输出
- ✅ 有限的内存使用
- ✅ 有限的CPU时间
- ✅ 临时文件读写（tmpfs）

### **2. 恶意代码防护**

#### **防护措施**

1. **无限循环防护**
   ```python
   # CPU时间限制
   resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
   ```

2. **内存炸弹防护**
   ```python
   # 内存限制
   'mem_limit': '128m'
   ```

3. **Fork炸弹防护**
   ```python
   # 进程数量限制
   resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
   ```

4. **文件操作防护**
   ```python
   # 只读文件系统
   'read_only': True
   ```

5. **网络攻击防护**
   ```python
   # 禁用网络
   'network_mode': 'none'
   ```

### **3. 测试安全性**

#### **测试恶意代码**

```python
# scripts/test_judge_security.py
def test_infinite_loop():
    """测试无限循环"""
    code = "while True: pass"
    result = judge_engine.execute(code, 'python')
    assert result['status'] == 'TIME_LIMIT_EXCEEDED'

def test_memory_bomb():
    """测试内存炸弹"""
    code = "a = [0] * (10 ** 9)"
    result = judge_engine.execute(code, 'python')
    assert result['status'] == 'MEMORY_LIMIT_EXCEEDED'

def test_fork_bomb():
    """测试Fork炸弹"""
    code = "import os; os.fork()"
    result = judge_engine.execute(code, 'python')
    assert result['status'] == 'RUNTIME_ERROR'

def test_file_write():
    """测试文件写入"""
    code = "open('/tmp/test.txt', 'w').write('data')"
    result = judge_engine.execute(code, 'python')
    assert result['status'] == 'RUNTIME_ERROR'

def test_network_access():
    """测试网络访问"""
    code = "import requests; requests.get('http://google.com')"
    result = judge_engine.execute(code, 'python')
    assert result['status'] == 'RUNTIME_ERROR'
```

#### **运行安全测试**

```bash
# 执行安全测试
python scripts/test_judge_security.py

# 或使用pytest
pytest scripts/test_judge_security.py -v
```

---

## 支持的编程语言

### **Python**

```python
# 配置
{
    'language': 'python',
    'compile_command': '',
    'run_command': 'python3 {file_path}',
    'file_extension': '.py',
    'time_limit': 5,
    'memory_limit': 128
}
```

### **C++**

```python
# 配置
{
    'language': 'cpp',
    'compile_command': 'g++ {file_path} -o {executable}',
    'run_command': '{executable}',
    'file_extension': '.cpp',
    'time_limit': 3,
    'memory_limit': 128
}
```

### **Java**

```python
# 配置
{
    'language': 'java',
    'compile_command': 'javac {file_path}',
    'run_command': 'java -cp {file_dir} {class_name}',
    'file_extension': '.java',
    'time_limit': 10,
    'memory_limit': 256
}
```

### **JavaScript**

```python
# 配置
{
    'language': 'javascript',
    'compile_command': '',
    'run_command': 'node {file_path}',
    'file_extension': '.js',
    'time_limit': 5,
    'memory_limit': 128
}
```

---

## 最佳实践

### **生产环境**

1. ✅ **使用Docker引擎**
2. ✅ **启用沙箱模式**
3. ✅ **配置合理的资源限制**
4. ✅ **定期更新安全策略**
5. ✅ **监控判题系统日志**

### **开发环境**

1. ✅ **使用沙箱引擎或基础引擎**
2. ✅ **使用SQLite数据库**
3. ✅ **启用Debug模式**
4. ✅ **测试各种边界情况**

### **安全检查清单**

- [ ] Docker Judger镜像已构建
- [ ] 环境变量已正确配置
- [ ] 资源限制已设置
- [ ] 网络隔离已启用
- [ ] 文件系统保护已启用
- [ ] 非特权用户执行
- [ ] 安全测试已通过
- [ ] 日志监控已配置

---

## 故障排除

### **问题1：Judger镜像构建失败**

```bash
# 检查Dockerfile
cat docker/judger/Dockerfile

# 检查网络连接
./scripts/diagnose-network.sh

# 手动构建
cd docker/judger
docker build -t django-oj-judger:latest .
```

### **问题2：判题任务超时**

```bash
# 增加超时时间
# 在JudgeConfig中设置
time_limit = 10  # 秒
```

### **问题3：内存限制不生效**

```bash
# 检查Docker配置
docker info | grep Memory

# 检查容器限制
docker inspect <container_id> | grep Memory
```

---

## 参考资源

- [Docker安全最佳实践](https://docs.docker.com/engine/security/)
- [Linux资源限制](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [Python安全编程](https://docs.python.org/3/library/security_warnings.html)

---

## 更新日志

- **v1.0** - 初始版本，支持Docker和沙箱引擎
- **v1.1** - 优化安全配置，增加恶意代码防护
- **v1.2** - 支持更多编程语言，完善资源限制

---

## 许可证

MIT License
