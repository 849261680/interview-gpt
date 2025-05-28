"""
Interview-GPT 后端主入口文件
提供FastAPI应用程序实例和基本路由配置
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import uvicorn
import logging
from typing import Dict

# 导入配置
from src.config.settings import settings

# 导入错误处理
from src.middlewares.error_handler import (
    ErrorHandlerMiddleware,
    create_http_exception_handler,
    create_validation_exception_handler
)

# 创建应用实例
app = FastAPI(
    title="Interview-GPT API",
    description="多AI AGENT面试系统的后端API",
    version="0.1.0",
)

# 配置CORS - 强化对OPTIONS预检请求的支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境下允许所有源，生产环境应该改回 settings.CORS_ORIGINS
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=600,  # 预检请求结果缓存时间10分钟
)

# 添加全局错误处理中间件
app.add_middleware(ErrorHandlerMiddleware)

# 重新启用请求日志中间件，以便在控制台看到API请求
from src.middlewares.request_logger import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)

# 配置异常处理器
app.add_exception_handler(HTTPException, create_http_exception_handler())
app.add_exception_handler(ValidationError, create_validation_exception_handler())

# 配置日志
# 从环境变量或配置文件中获取日志级别
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
log_file_path = settings.LOG_FILE

# 确保日志目录存在
import os
log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

# 配置根日志器
root_logger = logging.getLogger()
root_logger.setLevel(log_level)

# 清除现有的处理器
if root_logger.handlers:
    root_logger.handlers.clear()

# 配置文件处理器
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(log_level)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

# 配置控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

# 获取应用主日志记录器
logger = logging.getLogger("interview-gpt")

# 记录启动日志
logger.info(f"启动 Interview-GPT API, 日志级别: {settings.LOG_LEVEL}, 日志文件: {log_file_path}")
logger.info(f"已配置根日志记录器，所有模块日志都将写入文件: {log_file_path}")

# 健康检查路由
@app.get("/")
async def root() -> Dict[str, str]:
    """
    提供API根路由，用于健康检查
    """
    return {"status": "online", "message": "Interview-GPT API 正常运行"}

# 健康检查路由
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    详细的健康检查路由
    """
    return {
        "status": "healthy",
        "service": "Interview-GPT API",
        "version": "0.1.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# 导入路由
from src.api.router import api_router
app.include_router(api_router, prefix="/api")

# 直接运行（开发环境）
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=9999, reload=True)
