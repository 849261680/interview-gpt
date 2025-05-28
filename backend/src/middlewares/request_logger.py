import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("interview-gpt.request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    中间件：记录所有API请求的信息，包括路径、方法、状态码和处理时间
    """
    async def dispatch(self, request: Request, call_next):
        # 开始时间
        start_time = time.time()
        
        # 记录请求开始
        logger.debug(
            f"开始处理请求: {request.method} {request.url.path} | "
            f"客户端: {request.client.host if request.client else 'unknown'}"
        )
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录请求结果
            logger.info(
                f"请求完成: {request.method} {request.url.path} | "
                f"状态码: {response.status_code} | "
                f"处理时间: {process_time:.4f}秒"
            )
            
            return response
        except Exception as e:
            # 记录异常
            logger.error(
                f"请求异常: {request.method} {request.url.path} | "
                f"异常: {str(e)}",
                exc_info=True
            )
            raise
