"""
数据库初始化模块
负责创建数据库表结构和初始数据
"""
import logging
from sqlalchemy.orm import Session
from .database import engine, SessionLocal

# 避免循环导入
import importlib

# 设置日志
logger = logging.getLogger(__name__)

def init_db():
    """
    初始化数据库，创建表结构
    在应用启动时调用
    """
    try:
        # 动态导入模型，使用schemas.py中的完整模型定义
        schemas_module = importlib.import_module("..models.schemas", package="src.db")
        Base = schemas_module.Base
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表结构已创建")
        
        # 创建数据库会话
        db = SessionLocal()
        
        # 初始化基础数据（如有需要）
        _init_data(db)
        
        # 关闭会话
        db.close()
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


def _init_data(db: Session):
    """
    初始化基础数据
    如果需要在应用启动时创建一些基础数据，可以在这里添加
    """
    try:
        # 动态导入User模型，使用schemas.py中的模型
        schemas_module = importlib.import_module("..models.schemas", package="src.db")
        User = schemas_module.User
        
        # 检查是否需要创建默认用户
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("创建默认测试用户")
            # 创建一个测试用户，实际生产环境应删除
            test_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                is_active=True
            )
            db.add(test_user)
            db.commit()
            logger.info("测试用户已创建")
    except Exception as e:
        logger.error(f"初始化数据失败: {str(e)}")
        # 不抛出异常，以免阻止应用启动
