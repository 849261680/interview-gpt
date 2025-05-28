#!/bin/bash

# Interview-GPT 后端服务启动脚本
# 功能：环境检查、依赖安装、配置验证、服务启动

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 脚本配置
BACKEND_DIR="backend"
VENV_DIR="venv"
VENV_CREWAI_DIR="venv-crewai"
BACKEND_PORT=8000
BACKEND_HOST="127.0.0.1"

echo -e "${CYAN}🚀 启动 Interview-GPT 后端服务${NC}"
echo "================================================"

# 检查是否在项目根目录
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录运行此脚本${NC}"
    echo -e "${YELLOW}   当前目录: $(pwd)${NC}"
    echo -e "${YELLOW}   期望目录: Interview-GPT 项目根目录${NC}"
    exit 1
fi

# 进入后端目录
cd "$BACKEND_DIR"

echo -e "${BLUE}📁 当前工作目录: $(pwd)${NC}"

# 检查Python环境
echo -e "${BLUE}🐍 检查Python环境...${NC}"

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  未检测到激活的虚拟环境${NC}"
    
    # 尝试激活venv-crewai虚拟环境
    if [ -d "../$VENV_CREWAI_DIR" ]; then
        echo -e "${BLUE}🔄 尝试激活 $VENV_CREWAI_DIR 虚拟环境...${NC}"
        source "../$VENV_CREWAI_DIR/bin/activate"
        if [[ "$VIRTUAL_ENV" != "" ]]; then
            echo -e "${GREEN}✅ 成功激活虚拟环境: $VIRTUAL_ENV${NC}"
        fi
    # 尝试激活venv虚拟环境
    elif [ -d "../$VENV_DIR" ]; then
        echo -e "${BLUE}🔄 尝试激活 $VENV_DIR 虚拟环境...${NC}"
        source "../$VENV_DIR/bin/activate"
        if [[ "$VIRTUAL_ENV" != "" ]]; then
            echo -e "${GREEN}✅ 成功激活虚拟环境: $VIRTUAL_ENV${NC}"
        fi
    else
        echo -e "${RED}❌ 未找到虚拟环境目录${NC}"
        echo -e "${YELLOW}   请先创建并激活虚拟环境：${NC}"
        echo -e "${YELLOW}   python -m venv venv${NC}"
        echo -e "${YELLOW}   source venv/bin/activate${NC}"
        exit 1
    fi
    
    # 如果仍然没有激活虚拟环境
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${RED}❌ 无法激活虚拟环境${NC}"
        echo -e "${YELLOW}   请手动激活虚拟环境后重试：${NC}"
        echo -e "${YELLOW}   source venv/bin/activate${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"
fi

# 检查Python版本
PYTHON_VERSION=$(python --version 2>&1)
echo -e "${BLUE}🐍 Python版本: $PYTHON_VERSION${NC}"

# 检查环境配置文件
echo -e "${BLUE}⚙️  检查环境配置...${NC}"

if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo -e "${YELLOW}⚠️  .env 文件不存在，从 env.example 创建...${NC}"
        cp env.example .env
        echo -e "${GREEN}✅ 已创建 .env 文件${NC}"
        echo -e "${YELLOW}⚠️  请编辑 .env 文件配置必要的环境变量${NC}"
    else
        echo -e "${RED}❌ 错误: env.example 文件不存在${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env 文件存在${NC}"
fi

# 检查依赖
echo -e "${BLUE}📦 检查Python依赖...${NC}"

# 检查requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 错误: requirements.txt 文件不存在${NC}"
    exit 1
fi

# 尝试导入主模块来检查依赖
echo -e "${BLUE}🔍 验证依赖完整性...${NC}"
python -c "
import sys
sys.path.insert(0, '.')
try:
    from src.main import app
    print('✅ 核心依赖检查通过')
except ImportError as e:
    print(f'❌ 依赖检查失败: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  依赖检查失败，正在安装依赖...${NC}"
    
    # 升级pip
    echo -e "${BLUE}📦 升级pip...${NC}"
    python -m pip install --upgrade pip
    
    # 安装依赖 (跳过有问题的textract依赖)
    echo -e "${BLUE}📦 安装Python依赖...${NC}"
    pip install --no-deps -r requirements.txt 2>/dev/null || echo -e "${YELLOW}⚠️ 部分依赖安装可能被跳过${NC}"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 依赖安装失败${NC}"
        exit 1
    fi
    
    # 再次检查依赖
    python -c "
import sys
sys.path.insert(0, '.')
try:
    from src.main import app
    print('✅ 依赖安装成功')
except ImportError as e:
    print(f'❌ 依赖仍然缺失: {e}')
    sys.exit(1)
"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 依赖安装后仍然存在问题${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 所有依赖已满足${NC}"
fi

# 检查端口占用
echo -e "${BLUE}🔍 检查端口占用...${NC}"
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  端口 $BACKEND_PORT 已被占用${NC}"
    echo -e "${BLUE}🔄 尝试停止占用端口的进程...${NC}"
    
    # 获取占用端口的进程
    PID=$(lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t)
    if [ ! -z "$PID" ]; then
        echo -e "${YELLOW}   正在停止进程 PID: $PID${NC}"
        kill -TERM $PID 2>/dev/null
        sleep 2
        
        # 如果进程仍然存在，强制杀死
        if kill -0 $PID 2>/dev/null; then
            echo -e "${YELLOW}   强制停止进程...${NC}"
            kill -KILL $PID 2>/dev/null
        fi
    fi
    
    # 再次检查端口
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}❌ 无法释放端口 $BACKEND_PORT${NC}"
        echo -e "${YELLOW}   请手动停止占用端口的进程后重试${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ 端口 $BACKEND_PORT 已释放${NC}"
    fi
else
    echo -e "${GREEN}✅ 端口 $BACKEND_PORT 可用${NC}"
fi

# 创建日志目录
echo -e "${BLUE}📁 创建日志目录...${NC}"
mkdir -p logs
echo -e "${GREEN}✅ 日志目录已创建${NC}"

# 启动后端服务
echo -e "${BLUE}🚀 启动后端服务...${NC}"
echo -e "${CYAN}   主机: $BACKEND_HOST${NC}"
echo -e "${CYAN}   端口: $BACKEND_PORT${NC}"
echo -e "${CYAN}   模式: 开发模式 (热重载)${NC}"

# 设置环境变量
export PYTHONPATH=.

# 启动服务
echo -e "${BLUE}⏳ 正在启动服务...${NC}"

# 从.env文件读取日志级别（如果存在）
if [ -f ".env" ]; then
    LOG_LEVEL=$(grep LOG_LEVEL .env | cut -d= -f2 | tr -d "\r" | tr "[:upper:]" "[:lower:]" || echo "info")
    echo -e "${BLUE}📊 使用日志级别: $LOG_LEVEL${NC}"
else
    LOG_LEVEL="info"
fi

# 使用uvicorn启动服务
uvicorn src.main:app \
    --host $BACKEND_HOST \
    --port $BACKEND_PORT \
    --reload \
    --reload-dir src \
    --log-level $LOG_LEVEL \
    --access-log \
    --use-colors &

BACKEND_PID=$!

# 等待服务启动
echo -e "${BLUE}⏳ 等待服务启动...${NC}"
sleep 5

# 检查服务是否启动成功
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://$BACKEND_HOST:$BACKEND_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务启动成功！${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -e "${YELLOW}⏳ 等待服务启动... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
        sleep 2
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo -e "${YELLOW}   正在停止服务...${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 显示服务信息
echo ""
echo -e "${GREEN}🎉 Interview-GPT 后端服务启动成功！${NC}"
echo "================================================"
echo -e "${CYAN}🔧 服务地址:${NC}"
echo -e "${BLUE}   • API根路径: http://$BACKEND_HOST:$BACKEND_PORT${NC}"
echo -e "${BLUE}   • 健康检查: http://$BACKEND_HOST:$BACKEND_PORT/health${NC}"
echo -e "${BLUE}   • API文档:   http://$BACKEND_HOST:$BACKEND_PORT/docs${NC}"
echo -e "${BLUE}   • 交互文档: http://$BACKEND_HOST:$BACKEND_PORT/redoc${NC}"
echo ""
echo -e "${CYAN}📊 服务状态:${NC}"
echo -e "${BLUE}   • 进程ID: $BACKEND_PID${NC}"
echo -e "${BLUE}   • 运行模式: 开发模式 (热重载)${NC}"
echo -e "${BLUE}   • 日志级别: ${LOG_LEVEL}${NC}"
echo ""
echo -e "${YELLOW}💡 使用提示:${NC}"
echo -e "${BLUE}   • 按 Ctrl+C 停止服务${NC}"
echo -e "${BLUE}   • 修改代码会自动重载${NC}"
echo -e "${BLUE}   • 运行中的日志将显示在下方${NC}"
echo ""
echo -e "${GREEN}⏹️  按 Ctrl+C 停止服务${NC}"
echo "================================================"

# 显示日志
echo ""
echo -e "${CYAN}📄 正在显示实时后端日志...${NC}"
echo "------------------------------------------------"

# 设置信号处理
trap 'echo ""; echo -e "${YELLOW}🔴 正在停止后端服务...${NC}"; kill $BACKEND_PID 2>/dev/null; echo -e "${GREEN}✅ 后端服务已停止${NC}"; exit 0' INT

# 显示日志
tail -f logs/interview_gpt.log