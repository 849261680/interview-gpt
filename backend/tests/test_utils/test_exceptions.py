"""
异常类测试用例
测试自定义异常的功能和行为
"""
import pytest

from src.utils.exceptions import (
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


class TestInterviewGPTException:
    """基础异常类测试"""
    
    def test_basic_exception(self):
        """测试基础异常创建"""
        exc = InterviewGPTException("测试错误")
        
        assert str(exc) == "测试错误"
        assert exc.message == "测试错误"
        assert exc.error_code == "UNKNOWN_ERROR"
        assert exc.details == {}
    
    def test_exception_with_code(self):
        """测试带错误代码的异常"""
        exc = InterviewGPTException("测试错误", "TEST_ERROR")
        
        assert exc.error_code == "TEST_ERROR"
        assert exc.message == "测试错误"
    
    def test_exception_with_details(self):
        """测试带详情的异常"""
        details = {"field": "value", "count": 42}
        exc = InterviewGPTException("测试错误", "TEST_ERROR", details)
        
        assert exc.details == details
        assert exc.details["field"] == "value"
        assert exc.details["count"] == 42


class TestValidationError:
    """验证错误测试"""
    
    def test_validation_error(self):
        """测试验证错误"""
        exc = ValidationError("字段验证失败", "email")
        
        assert exc.message == "字段验证失败"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field == "email"
    
    def test_validation_error_with_details(self):
        """测试带详情的验证错误"""
        details = {"expected": "email", "actual": "invalid"}
        exc = ValidationError("邮箱格式错误", "email", details)
        
        assert exc.field == "email"
        assert exc.details == details


class TestDatabaseError:
    """数据库错误测试"""
    
    def test_database_error(self):
        """测试数据库错误"""
        exc = DatabaseError("连接失败", "connect")
        
        assert exc.message == "连接失败"
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.operation == "connect"
    
    def test_database_error_without_operation(self):
        """测试不带操作的数据库错误"""
        exc = DatabaseError("未知数据库错误")
        
        assert exc.operation is None


class TestInterviewNotFoundError:
    """面试未找到错误测试"""
    
    def test_interview_not_found_error(self):
        """测试面试未找到错误"""
        exc = InterviewNotFoundError(123)
        
        assert "面试会话未找到: ID=123" in exc.message
        assert exc.error_code == "INTERVIEW_NOT_FOUND"
        assert exc.interview_id == 123


class TestInterviewerError:
    """面试官错误测试"""
    
    def test_interviewer_error(self):
        """测试面试官错误"""
        exc = InterviewerError("面试官初始化失败", "technical")
        
        assert exc.message == "面试官初始化失败"
        assert exc.error_code == "INTERVIEWER_ERROR"
        assert exc.interviewer_id == "technical"


class TestAIServiceError:
    """AI服务错误测试"""
    
    def test_ai_service_error(self):
        """测试AI服务错误"""
        exc = AIServiceError("API调用失败", "deepseek")
        
        assert exc.message == "API调用失败"
        assert exc.error_code == "AI_SERVICE_ERROR"
        assert exc.service_name == "deepseek"


class TestFileUploadError:
    """文件上传错误测试"""
    
    def test_file_upload_error(self):
        """测试文件上传错误"""
        exc = FileUploadError("文件太大", "resume.pdf")
        
        assert exc.message == "文件太大"
        assert exc.error_code == "FILE_UPLOAD_ERROR"
        assert exc.filename == "resume.pdf"


class TestAuthenticationError:
    """认证错误测试"""
    
    def test_authentication_error_default(self):
        """测试默认认证错误"""
        exc = AuthenticationError()
        
        assert exc.message == "认证失败"
        assert exc.error_code == "AUTHENTICATION_ERROR"
    
    def test_authentication_error_custom(self):
        """测试自定义认证错误"""
        exc = AuthenticationError("令牌已过期")
        
        assert exc.message == "令牌已过期"


class TestAuthorizationError:
    """授权错误测试"""
    
    def test_authorization_error_default(self):
        """测试默认授权错误"""
        exc = AuthorizationError()
        
        assert exc.message == "权限不足"
        assert exc.error_code == "AUTHORIZATION_ERROR"
    
    def test_authorization_error_custom(self):
        """测试自定义授权错误"""
        exc = AuthorizationError("需要管理员权限")
        
        assert exc.message == "需要管理员权限"


class TestRateLimitError:
    """频率限制错误测试"""
    
    def test_rate_limit_error_default(self):
        """测试默认频率限制错误"""
        exc = RateLimitError()
        
        assert exc.message == "请求过于频繁，请稍后再试"
        assert exc.error_code == "RATE_LIMIT_ERROR"
    
    def test_rate_limit_error_custom(self):
        """测试自定义频率限制错误"""
        exc = RateLimitError("每分钟最多10次请求")
        
        assert exc.message == "每分钟最多10次请求"


class TestConfigurationError:
    """配置错误测试"""
    
    def test_configuration_error(self):
        """测试配置错误"""
        exc = ConfigurationError("缺少API密钥", "DEEPSEEK_API_KEY")
        
        assert exc.message == "缺少API密钥"
        assert exc.error_code == "CONFIGURATION_ERROR"
        assert exc.config_key == "DEEPSEEK_API_KEY"
    
    def test_configuration_error_without_key(self):
        """测试不带配置键的配置错误"""
        exc = ConfigurationError("配置文件格式错误")
        
        assert exc.config_key is None


class TestExceptionInheritance:
    """异常继承测试"""
    
    def test_all_exceptions_inherit_from_base(self):
        """测试所有异常都继承自基础异常"""
        exception_classes = [
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
        ]
        
        for exc_class in exception_classes:
            assert issubclass(exc_class, InterviewGPTException)
            assert issubclass(exc_class, Exception)
    
    def test_exception_can_be_caught_as_base(self):
        """测试异常可以作为基础异常捕获"""
        with pytest.raises(InterviewGPTException):
            raise ValidationError("测试错误")
        
        with pytest.raises(InterviewGPTException):
            raise DatabaseError("测试错误")
        
        with pytest.raises(InterviewGPTException):
            raise InterviewNotFoundError(123) 