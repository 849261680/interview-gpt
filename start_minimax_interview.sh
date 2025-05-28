#!/bin/bash

# MiniMax MCP 实时AI语音面试启动脚本
# 快速启动Interview-GPT的MiniMax MCP功能

echo "🚀 启动 MiniMax MCP 实时AI语音面试系统"
echo "================================================"

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 检查npm环境
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到npm，请先安装npm"
    exit 1
fi

# 进入前端目录
cd frontend

# 检查环境变量配置
if [ ! -f ".env.local" ]; then
    echo "⚠️  警告: 未找到.env.local文件"
    echo "📝 请创建.env.local文件并配置MiniMax API密钥："
    echo ""
    echo "NEXT_PUBLIC_MINIMAX_API_KEY=your_minimax_api_key_here"
    echo "NEXT_PUBLIC_MINIMAX_GROUP_ID=your_minimax_group_id_here"
    echo "NEXT_PUBLIC_MINIMAX_BASE_URL=https://api.minimax.chat"
    echo ""
    echo "💡 提示: 可以复制.env.example文件并重命名为.env.local"
    echo "🌐 获取API密钥: https://api.minimax.chat"
    echo ""
    read -p "是否继续启动（将使用模拟模式）？[y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖包..."
    npm install
fi

# 启动开发服务器
echo "🎤 启动MiniMax MCP语音面试服务..."
echo "📍 前端地址: http://localhost:3011"
echo "🎯 面试页面: http://localhost:3011/interview/3274"
echo ""
echo "✨ 功能特性:"
echo "   🤖 MiniMax智能对话"
echo "   🎤 语音识别(ASR)"
echo "   🔊 语音合成(TTS)"
echo "   ⚡ 实时流式响应"
echo "   🎭 多角色面试官"
echo ""
echo "🔧 使用说明:"
echo "   1. 访问面试页面"
echo "   2. 检查MCP连接状态"
echo "   3. 点击'开始AI面试'"
echo "   4. 授权麦克风权限"
echo "   5. 使用🎤按钮语音回答"
echo ""
echo "⏹️  按 Ctrl+C 停止服务"
echo "================================================"

# 启动服务
npm run dev 