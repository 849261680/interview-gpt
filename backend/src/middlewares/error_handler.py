"""
全局错误处理中间件
统一处理应用中的异常，返回标准化的错误响应
"""
import logging
import traceback
from datetime import datetime
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..utils.exceptions import (
    InterviewGPTException,
    ValidationError,
    DatabaseError,
    InterviewNotFoundError,
    InterviewerError,
    AIServiceError,
    FileUploadError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ConfigurationError
)

# 设置日志
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    全局错误处理中间件
    捕获并处理应用中的所有异常
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        处理请求并捕获异常
        
        Args:
            request: HTTP请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: HTTP响应对象
        """
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self._handle_exception(request, exc)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        处理异常并返回标准化响应
        
        Args:
            request: HTTP请求对象
            exc: 异常对象
            
        Returns:
            JSONResponse: 标准化的错误响应
        """
        # 记录异常信息
        logger.error(
            f"异常发生在 {request.method} {request.url}: {str(exc)}",
            exc_info=True
        )
        
        # 根据异常类型返回相应的错误响应
        if isinstance(exc, ValidationError):
            return self._create_error_response(
                status_code=400,
                error_code=exc.error_code,
                message=exc.message,
                details=exc.details
            )
        
        elif isinstance(exc, InterviewNotFoundError):
            return self._create_error_response(
                status_code=404,
                error_code=exc.error_code,
                message=exc.message,
                details={"interview_id": exc.interview_id}
            )
        
        elif isinstance(exc, AuthenticationError):
            return self._create_error_response(
                status_code=401,
                error_code=exc.error_code,
                message=exc.message
            )
        
        elif isinstance(exc, AuthorizationError):
            return self._create_error_response(
                status_code=403,
                error_code=exc.error_code,
                message=exc.message
            )
        
        elif isinstance(exc, RateLimitError):
            return self._create_error_response(
                status_code=429,
                error_code=exc.error_code,
                message=exc.message
            )
        
        elif isinstance(exc, (DatabaseError, InterviewerError, AIServiceError, FileUploadError)):
            return self._create_error_response(
                status_code=500,
                error_code=exc.error_code,
                message=exc.message,
                details=exc.details
            )
        
        elif isinstance(exc, ConfigurationError):
            return self._create_error_response(
                status_code=500,
                error_code=exc.error_code,
                message=exc.message,
                details={"config_key": exc.config_key}
            )
        
        elif isinstance(exc, HTTPException):
            return self._create_error_response(
                status_code=exc.status_code,
                error_code="HTTP_EXCEPTION",
                message=exc.detail
            )
        
        elif isinstance(exc, InterviewGPTException):
            return self._create_error_response(
                status_code=500,
                error_code=exc.error_code,
                message=exc.message,
                details=exc.details
            )
        
        else:
            # 未知异常
            return self._create_error_response(
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
                message="服务器内部错误，请稍后重试"
            )
    
    def _create_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Dict[str, Any] = None
    ) -> JSONResponse:
        """
        创建标准化的错误响应
        
        Args:
            status_code: HTTP状态码
            error_code: 错误代码
            message: 错误消息
            details: 错误详情
            
        Returns:
            JSONResponse: 标准化的错误响应
        """
        error_response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": self._get_current_timestamp()
            }
        }
        
        if details:
            error_response["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def create_http_exception_handler():
    """
    创建HTTP异常处理器
    用于处理FastAPI的HTTPException
    """
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理HTTP异常"""
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_EXCEPTION",
                    "message": exc.detail,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        )
    
    return http_exception_handler


def create_validation_exception_handler():
    """
    创建验证异常处理器
    用于处理Pydantic的ValidationError
    """
    from pydantic import ValidationError as PydanticValidationError
    
    async def validation_exception_handler(request: Request, exc: PydanticValidationError):
        """处理验证异常"""
        logger.warning(f"数据验证失败: {exc.errors()}")
        
        # 格式化验证错误信息
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "数据验证失败",
                    "details": {"errors": errors},
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        )
    
    return validation_exception_handler 