#!/bin/bash

# Interview-GPT 项目启动脚本

echo "🚀 启动 Interview-GPT 项目..."

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  请先激活虚拟环境："
    echo "   source venv/bin/activate"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
cd backend
python -c "from src.main import app; print('✅ 后端依赖检查通过')" || {
    echo "❌ 后端依赖检查失败，请安装缺失的依赖"
    exit 1
}

cd ../frontend
npm list > /dev/null 2>&1 || {
    echo "📦 安装前端依赖..."
    npm install
}

echo "✅ 依赖检查完成"

# 清理现有进程
echo "🧹 清理现有进程..."
pkill -f "uvicorn\|next" 2>/dev/null || true
sleep 2

# 启动后端
echo "🔧 启动后端服务..."
cd ../backend
PYTHONPATH=. python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 10

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务启动成功 (http://localhost:8000)"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 启动前端
echo "🎨 启动前端服务..."
cd ../frontend
PORT=3000 npm run dev &
FRONTEND_PID=$!

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 15

# 检查前端是否启动成功
if curl -s http://localhost:3000 | grep -q "Interview-GPT"; then
    echo "✅ 前端服务启动成功 (http://localhost:3000)"
else
    echo "❌ 前端服务启动失败"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Interview-GPT 项目启动成功！"
echo ""
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ 服务已停止"; exit 0' INT

# 保持脚本运行
wait 