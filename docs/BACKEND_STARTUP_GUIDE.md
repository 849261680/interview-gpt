# Interview-GPT 后端启动指南

## 📋 概述

本指南介绍如何启动 Interview-GPT 项目的后端服务，包括环境配置、依赖安装和服务启动。

## 🚀 快速启动

### 方式1：使用完整启动脚本（推荐）

```bash
# 在项目根目录运行
./start_backend.sh
```

**功能特性：**
- ✅ 自动检查和激活虚拟环境
- ✅ 自动创建 .env 配置文件
- ✅ 自动安装缺失的依赖
- ✅ 自动检查端口占用并清理
- ✅ 详细的启动日志和状态检查
- ✅ 优雅的错误处理和提示

### 方式2：使用简化启动脚本

```bash
# 在项目根目录运行
./start_backend_simple.sh
```

**适用场景：**
- 环境已配置完成
- 依赖已安装
- 需要快速启动

### 方式3：手动启动

```bash
# 1. 激活虚拟环境
source venv/bin/activate
# 或者
source venv-crewai/bin/activate

# 2. 进入后端目录
cd backend

# 3. 创建环境配置（首次运行）
cp env.example .env

# 4. 安装依赖（首次运行）
pip install -r requirements.txt

# 5. 启动服务
export PYTHONPATH=.
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

## ⚙️ 环境配置

### 必需的环境变量

编辑 `backend/.env` 文件：

```bash
# 基础设置
DEBUG=true
SECRET_KEY=your_secret_key_here_change_this_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS设置
CORS_ORIGINS=http://localhost:3011,http://localhost:8000

# 数据库设置
DATABASE_URL=sqlite:///./interview_gpt.db

# AI服务设置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# MiniMax API配置（可选）
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_GROUP_ID=your_minimax_group_id_here

# CrewAI设置
CREWAI_VERBOSE=true
CREWAI_MAX_ITERATIONS=15
CREWAI_MAX_RPM=60

# 日志设置
LOG_LEVEL=INFO
LOG_FILE=logs/interview_gpt.log
```

### API密钥获取

1. **DeepSeek API**：
   - 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
   - 注册账号并获取 API Key

2. **MiniMax API**（可选）：
   - 访问 [MiniMax 开放平台](https://api.minimax.chat/)
   - 注册账号并获取 API Key 和 Group ID

## 📦 依赖管理

### Python 依赖

主要依赖包括：
- **FastAPI**: Web框架
- **uvicorn**: ASGI服务器
- **SQLAlchemy**: ORM数据库操作
- **CrewAI**: 多智能体框架
- **LangChain**: AI应用开发框架
- **ChromaDB**: 向量数据库

### 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# 最小依赖（快速测试）
pip install -r requirements-minimal.txt
```

## 🔍 服务验证

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "service": "Interview-GPT API",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### API 文档

启动后可访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看占用端口的进程
   lsof -i :8000
   
   # 停止进程
   kill -9 <PID>
   ```

2. **虚拟环境问题**
   ```bash
   # 创建新的虚拟环境
   python -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

3. **依赖冲突**
   ```bash
   # 清理并重新安装
   pip freeze > installed_packages.txt
   pip uninstall -r installed_packages.txt -y
   pip install -r backend/requirements.txt
   ```

4. **数据库问题**
   ```bash
   # 删除数据库文件重新创建
   rm backend/interview_gpt.db
   # 重启服务会自动创建新数据库
   ```

### 日志查看

```bash
# 查看实时日志
tail -f backend/logs/interview_gpt.log

# 查看uvicorn日志
# 启动时会在终端显示
```

## 🔧 开发模式

### 热重载

启动脚本默认启用热重载模式：
- 修改 `src/` 目录下的代码会自动重启服务
- 无需手动重启服务

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG

# 启用CrewAI详细输出
export CREWAI_VERBOSE=true
```

## 📊 性能监控

### 服务状态

```bash
# 检查进程状态
ps aux | grep uvicorn

# 检查端口监听
netstat -tlnp | grep :8000

# 检查内存使用
top -p $(pgrep -f uvicorn)
```

### API 性能

```bash
# 简单性能测试
time curl http://localhost:8000/health

# 并发测试（需要安装ab）
ab -n 100 -c 10 http://localhost:8000/health
```

## 🔒 安全配置

### 生产环境

1. **更改默认密钥**：
   ```bash
   # 生成安全的SECRET_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **配置CORS**：
   ```bash
   # 限制允许的源
   CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
   ```

3. **HTTPS配置**：
   - 使用反向代理（Nginx）
   - 配置SSL证书

## 📝 脚本说明

### start_backend.sh

**完整功能脚本**，包含：
- 环境检查和自动配置
- 依赖安装和验证
- 端口冲突检测和处理
- 服务启动和健康检查
- 详细的状态显示和错误处理

### start_backend_simple.sh

**简化快速脚本**，适用于：
- 环境已配置的情况
- 快速重启服务
- 开发过程中的频繁启动

## 🎯 下一步

1. **启动前端服务**：
   ```bash
   ./start_frontend.sh
   ```

2. **启动完整项目**：
   ```bash
   ./start_project.sh
   ```

3. **配置MiniMax语音功能**：
   ```bash
   ./start_minimax_interview.sh
   ```

---

## 📞 技术支持

如果遇到问题，请检查：
1. Python版本（推荐3.9+）
2. 虚拟环境是否正确激活
3. 依赖是否完整安装
4. 环境变量是否正确配置
5. 端口是否被其他服务占用

**祝你使用愉快！** 🎉 