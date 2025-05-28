"""
自定义异常类
定义项目中使用的各种异常类型，提供更精确的错误处理
"""
from typing import Any, Dict, Optional


class InterviewGPTException(Exception):
    """
    Interview-GPT基础异常类
    所有自定义异常的基类
    """
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(InterviewGPTException):
    """数据验证异常"""
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class DatabaseError(InterviewGPTException):
    """数据库操作异常"""
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation


class InterviewNotFoundError(InterviewGPTException):
    """面试会话未找到异常"""
    def __init__(self, interview_id: int):
        message = f"面试会话未找到: ID={interview_id}"
        super().__init__(message, "INTERVIEW_NOT_FOUND")
        self.interview_id = interview_id


class InterviewerError(InterviewGPTException):
    """面试官相关异常"""
    def __init__(self, message: str, interviewer_id: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "INTERVIEWER_ERROR", details)
        self.interviewer_id = interviewer_id


class AIServiceError(InterviewGPTException):
    """AI服务异常"""
    def __init__(self, message: str, service_name: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "AI_SERVICE_ERROR", details)
        self.service_name = service_name


class AssessmentError(InterviewGPTException):
    """评估相关异常"""
    def __init__(self, message: str, assessment_type: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "ASSESSMENT_ERROR", details)
        self.assessment_type = assessment_type


class FileUploadError(InterviewGPTException):
    """文件上传异常"""
    def __init__(self, message: str, filename: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "FILE_UPLOAD_ERROR", details)
        self.filename = filename


class FileProcessingError(InterviewGPTException):
    """文件处理异常"""
    def __init__(self, message: str, filename: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "FILE_PROCESSING_ERROR", details)
        self.filename = filename


class AuthenticationError(InterviewGPTException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(InterviewGPTException):
    """授权异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class RateLimitError(InterviewGPTException):
    """请求频率限制异常"""
    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(message, "RATE_LIMIT_ERROR")


class ConfigurationError(InterviewGPTException):
    """配置错误异常"""
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key 


class SpeechProcessingError(InterviewGPTException):
    """语音处理异常"""
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "SPEECH_PROCESSING_ERROR", details)
        self.operation = operation