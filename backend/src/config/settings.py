"""
应用程序配置设置
从环境变量加载配置参数，为应用程序提供配置
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用程序设置类"""
    
    # 基础设置
    APP_NAME: str = "Interview-GPT"
    API_V1_STR: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 安全设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS设置 - 使用简单字符串类型避免解析问题
    CORS_ORIGINS_STR: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8000,https://interview-gpt.vercel.app")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.CORS_ORIGINS_STR.split(",")
    
    # 数据库设置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./interview_gpt.db")
    
    # AI服务设置
    # DEEPSEEK API配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # MiniMax API配置
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_GROUP_ID: str = os.getenv("MINIMAX_GROUP_ID", "")
    
    # OpenAI API配置（备用）
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Speech API配置
    GOOGLE_SPEECH_CREDENTIALS_PATH: str = os.getenv("GOOGLE_SPEECH_CREDENTIALS_PATH", "")
    GOOGLE_SPEECH_PROJECT_ID: str = os.getenv("GOOGLE_SPEECH_PROJECT_ID", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # 知识库设置
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "chroma")  # chroma 或 pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    
    # CrewAI设置
    CREWAI_VERBOSE: bool = os.getenv("CREWAI_VERBOSE", "true").lower() == "true"
    CREWAI_MAX_ITERATIONS: int = int(os.getenv("CREWAI_MAX_ITERATIONS", "15"))
    CREWAI_MAX_RPM: int = int(os.getenv("CREWAI_MAX_RPM", "60"))
    
    # 日志设置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/interview_gpt.log")
    
    # AI服务优先级配置
    @property
    def PRIMARY_AI_SERVICE(self) -> str:
        """获取主要AI服务"""
        if self.DEEPSEEK_API_KEY:
            return "deepseek"
        elif self.MINIMAX_API_KEY:
            return "minimax"
        elif self.OPENAI_API_KEY:
            return "openai"
        else:
            return "mock"  # 使用模拟服务
    
    @property
    def AVAILABLE_AI_SERVICES(self) -> List[str]:
        """获取可用的AI服务列表"""
        services = []
        if self.DEEPSEEK_API_KEY:
            services.append("deepseek")
        if self.MINIMAX_API_KEY:
            services.append("minimax")
        if self.OPENAI_API_KEY:
            services.append("openai")
        if not services:
            services.append("mock")
        return services
    
    class Config:
        case_sensitive = True


# 创建设置实例
settings = Settings()
