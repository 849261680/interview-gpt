#!/bin/bash

# Interview-GPT 生产环境启动脚本
# 负责启动前端和后端服务

set -e

echo "🚀 启动 Interview-GPT 生产环境..."

# 设置环境变量
export NODE_ENV=production
export PYTHONUNBUFFERED=1

# 创建必要的目录
mkdir -p /app/logs /app/uploads /app/data

# 等待数据库就绪
echo "⏳ 等待数据库连接..."
python -c "
import time
import sqlite3
import os

db_path = '/app/data/interview_gpt.db'
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 尝试连接数据库
        conn = sqlite3.connect(db_path)
        conn.close()
        print('✅ 数据库连接成功')
        break
    except Exception as e:
        retry_count += 1
        print(f'⏳ 数据库连接失败 ({retry_count}/{max_retries}): {e}')
        time.sleep(2)

if retry_count >= max_retries:
    print('❌ 数据库连接超时')
    exit(1)
"

# 运行数据库迁移
echo "📊 运行数据库迁移..."
cd /app/backend
python -c "
from src.db.database import engine, Base
from src.models import schemas

try:
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print('✅ 数据库表创建成功')
except Exception as e:
    print(f'❌ 数据库迁移失败: {e}')
    exit(1)
"

# 启动后端服务（后台运行）
echo "🔧 启动后端服务..."
cd /app/backend
python -m uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --access-log \
    --log-level info &

BACKEND_PID=$!

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 后端服务启动超时"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 2
done

# 启动前端服务（如果存在构建产物）
if [ -d "/app/frontend/.next" ]; then
    echo "🎨 启动前端服务..."
    cd /app/frontend
    
    # 安装生产依赖
    npm ci --only=production
    
    # 启动Next.js生产服务器
    npm start &
    FRONTEND_PID=$!
    
    # 等待前端服务启动
    echo "⏳ 等待前端服务启动..."
    for i in {1..30}; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            echo "✅ 前端服务启动成功"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ 前端服务启动超时"
            kill $FRONTEND_PID 2>/dev/null || true
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 2
    done
else
    echo "⚠️  前端构建产物不存在，仅启动后端服务"
    FRONTEND_PID=""
fi

echo "🎉 Interview-GPT 启动完成！"
echo "📍 后端服务: http://localhost:8000"
if [ -n "$FRONTEND_PID" ]; then
    echo "📍 前端服务: http://localhost:3000"
fi
echo "📍 API文档: http://localhost:8000/docs"
echo "📍 健康检查: http://localhost:8000/health"

# 优雅关闭处理
cleanup() {
    echo "🛑 正在关闭服务..."
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✅ 前端服务已关闭"
    fi
    kill $BACKEND_PID 2>/dev/null || true
    echo "✅ 后端服务已关闭"
    exit 0
}

trap cleanup SIGTERM SIGINT

# 保持脚本运行
if [ -n "$FRONTEND_PID" ]; then
    wait $FRONTEND_PID $BACKEND_PID
else
    wait $BACKEND_PID
fi 