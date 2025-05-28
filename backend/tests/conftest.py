"""
pytest配置文件
定义测试环境和共享的fixtures
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.models.schemas import Base
from src.db.database import get_db


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 清理表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_interview_data():
    """示例面试数据"""
    return {
        "position": "AI应用工程师",
        "difficulty": "medium"
    }


@pytest.fixture
def sample_message_data():
    """示例消息数据"""
    return {
        "content": "我有3年的Python开发经验，熟悉机器学习和深度学习框架。",
        "sender_type": "user"
    }


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }


# AI集成测试相关的fixtures
@pytest.fixture
async def ai_service_manager():
    """AI服务管理器fixture"""
    from src.services.ai.ai_service_manager import ai_service_manager
    yield ai_service_manager
    # 清理资源
    try:
        await ai_service_manager.cleanup()
    except:
        pass  # 忽略清理错误


@pytest.fixture
def crewai_integration():
    """CrewAI集成fixture"""
    from src.services.ai.crewai_integration import crewai_integration
    return crewai_integration


@pytest.fixture
def interviewer_factory():
    """面试官工厂fixture"""
    from src.agents.interviewer_factory import InterviewerFactory
    return InterviewerFactory


@pytest.fixture
def mock_deepseek_response():
    """模拟DEEPSEEK API响应"""
    return {
        "choices": [
            {
                "message": {
                    "content": "这是一个模拟的AI回复，用于测试目的。Python是一种高级编程语言，广泛应用于Web开发、数据科学和人工智能领域。"
                }
            }
        ]
    }


@pytest.fixture
def sample_interview_messages():
    """示例面试消息"""
    return [
        {"sender_type": "system", "content": "面试开始"},
        {"sender_type": "interviewer", "content": "请介绍一下您的技术背景", "interviewer_id": "technical"},
        {"sender_type": "user", "content": "我有3年Python开发经验，熟悉Django和FastAPI框架"},
        {"sender_type": "interviewer", "content": "能否详细说明一下您在项目中的角色？", "interviewer_id": "technical"},
        {"sender_type": "user", "content": "我主要负责后端API开发和数据库设计，参与了多个Web应用项目"}
    ]


@pytest.fixture
def ai_test_config():
    """AI测试配置"""
    return {
        "test_timeout": 30,  # 测试超时时间（秒）
        "max_retries": 3,    # 最大重试次数
        "mock_responses": True,  # 是否使用模拟响应
        "skip_real_api": True   # 是否跳过真实API调用
    }


# 添加AI集成测试的标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "ai_integration: 标记AI集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: 标记需要API密钥的测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    import os
    
    # 如果没有API密钥，跳过相关测试
    if not os.getenv("DEEPSEEK_API_KEY"):
        skip_api = pytest.mark.skip(reason="需要DEEPSEEK_API_KEY环境变量")
        for item in items:
            if "requires_api_key" in item.keywords:
                item.add_marker(skip_api)
    
    # 为AI集成测试添加超时
    for item in items:
        if "ai_integration" in item.keywords:
            item.add_marker(pytest.mark.timeout(60))  # 60秒超时 