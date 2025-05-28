"""
面试相关数据库模型
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
import datetime
from ..db.database import Base

class Interview(Base):
    """面试会话模型"""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    position = Column(String(100))
    candidate_name = Column(String(100))
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    messages = Column(JSON, nullable=True)
    feedback = Column(JSON, nullable=True)
    resume_text = Column(Text, nullable=True)
    duration = Column(Integer, default=0)  # 面试时长（秒）
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="interviews")
    
    
class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关系
    interviews = relationship("Interview", back_populates="user")
