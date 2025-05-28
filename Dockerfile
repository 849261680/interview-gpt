# Interview-GPT 生产环境 Dockerfile
# 多阶段构建：前端构建 -> 后端构建 -> 生产镜像

# ================================
# 阶段1: 前端构建
# ================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./
COPY package.json /app/

# 安装前端依赖
RUN npm ci --only=production

# 复制前端源码
COPY frontend/ ./
COPY shared/ /app/shared/

# 构建前端应用
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ================================
# 阶段2: 后端Python环境准备
# ================================
FROM python:3.11-slim AS backend-builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    git \
    # 图像处理依赖（用于OCR）
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    # 文件处理依赖
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt ./

# 创建虚拟环境并安装Python依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# 下载spaCy模型
RUN python -m spacy download en_core_web_sm

# ================================
# 阶段3: 生产环境镜像
# ================================
FROM python:3.11-slim AS production

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"
ENV NODE_ENV=production

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制Python虚拟环境
COPY --from=backend-builder /opt/venv /opt/venv

# 复制后端应用代码
COPY backend/ ./backend/
COPY shared/ ./shared/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json

# 创建必要的目录
RUN mkdir -p /app/logs /app/uploads /app/data
RUN chown -R appuser:appuser /app

# 切换到应用用户
USER appuser

# 暴露端口
EXPOSE 8000 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动脚本
COPY scripts/start-production.sh /app/
USER root
RUN chmod +x /app/start-production.sh
USER appuser

CMD ["/app/start-production.sh"] 