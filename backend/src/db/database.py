"""
数据库连接模块
负责管理与SQLite数据库的连接和会话
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from ..config.settings import settings

# 创建数据库URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类实例
Base = declarative_base()

# 获取数据库会话的依赖函数
def get_db():
    """
    FastAPI依赖函数，用于创建和管理数据库会话
    使用yield确保会话在请求结束后关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 导入初始化函数
from .init_db import init_db

# 数据库初始化函数
init_db()
