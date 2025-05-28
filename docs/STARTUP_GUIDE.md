# Interview-GPT 项目启动指南

## 🚀 快速启动

### 前提条件
- Python 3.9+
- Node.js 18+
- 已激活虚拟环境：`source venv/bin/activate`

### 方法一：使用清理启动脚本（推荐）

```bash
# 在项目根目录下
./start_clean.sh
```

### 方法二：使用原始启动脚本

```bash
# 在项目根目录下
./start_project.sh
```

### 方法三：分别启动前后端

#### 启动后端
```bash
# 方式1：使用脚本
./start_backend.sh

# 方式2：手动启动
cd backend
export PYTHONPATH=.
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

#### 启动前端
```bash
# 方式1：使用脚本
./start_frontend.sh

# 方式2：手动启动
cd frontend
PORT=3011 npm run dev
```

### 方法四：使用终端分屏

1. **终端1 - 启动后端**：
   ```bash
   cd backend
   export PYTHONPATH=.
   python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **终端2 - 启动前端**：
   ```bash
   cd frontend
   PORT=3011 npm run dev
   ```

## 📱 访问地址

- **前端应用**: http://localhost:3011
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **测试评估页面**: http://localhost:3011/TestAssessment

## 🔧 故障排除

### 端口被占用
```bash
# 查看端口占用
lsof -i :3011
lsof -i :8000

# 杀死进程
pkill -f "uvicorn|next"
```

### 后端启动失败
1. 确保在backend目录下启动
2. 设置PYTHONPATH环境变量：`export PYTHONPATH=.`
3. 检查虚拟环境是否激活：`which python`
4. 检查依赖是否安装完整：`pip list`

### 前端启动失败
1. 确保在frontend目录下启动
2. 运行 `npm install` 安装依赖
3. 清理缓存：`rm -rf .next node_modules && npm install`
4. 使用不同端口：`PORT=3012 npm run dev`

### 页面显示问题
1. 检查浏览器控制台是否有JavaScript错误
2. 确保Tailwind CSS正确加载
3. 清理浏览器缓存
4. 检查网络请求是否正常

## 📦 依赖检查

### 后端依赖
```bash
cd backend
python -c "from src.main import app; print('✅ 后端依赖正常')"
```

### 前端依赖
```bash
cd frontend
npm list
```

## 🛑 停止服务

```bash
# 停止所有相关进程
pkill -f "uvicorn|next"

# 或者在启动的终端中按 Ctrl+C
```

## 📝 开发模式特性

- **热重载**: 代码修改后自动重启
- **实时日志**: 查看请求和错误日志
- **调试模式**: 详细的错误信息
- **API文档**: 自动生成的交互式API文档

## 🎯 测试功能

启动成功后，可以访问以下页面测试功能：

1. **主页**: http://localhost:3011
2. **面试创建**: http://localhost:3011/interview/new
3. **评估测试**: http://localhost:3011/TestAssessment
4. **API文档**: http://localhost:8000/docs

## 💡 提示

- 首次启动可能需要较长时间来安装依赖
- 确保8000和3011端口未被其他应用占用
- 如果遇到问题，请查看终端输出的错误信息
- 前端现在使用端口3011而不是3000，避免端口冲突
- 页面样式已优化，确保正确显示

## 🐛 常见问题

### Q: 前端页面显示不完整或样式错误
A: 这通常是因为Tailwind CSS没有正确加载或JavaScript执行错误。请检查浏览器控制台的错误信息。

### Q: 后端无法找到src模块
A: 确保在backend目录下启动，并设置`PYTHONPATH=.`环境变量。

### Q: 端口被占用
A: 使用`pkill -f "uvicorn|next"`清理进程，或使用不同端口启动。

### Q: 虚拟环境问题
A: 确保已激活虚拟环境：`source venv/bin/activate`，并检查Python路径：`which python`。 