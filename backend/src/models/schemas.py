"""
数据库模型定义
使用SQLAlchemy ORM定义应用的数据结构
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


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
    

class Interview(Base):
    """面试会话模型"""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 允许匿名面试
    position = Column(String(100), index=True)  # 面试职位
    difficulty = Column(String(20))  # 面试难度：easy, medium, hard
    status = Column(String(20), default="active")  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    resume_filename = Column(String(255), nullable=True)  # 简历文件名
    resume_content = Column(Text, nullable=True)  # 简历文本内容
    overall_score = Column(Float, nullable=True)  # 总体评分
    
    # 关系
    user = relationship("User", back_populates="interviews")
    messages = relationship("Message", back_populates="interview")
    feedback = relationship("Feedback", back_populates="interview", uselist=False)


class Message(Base):
    """面试消息模型"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    content = Column(Text)
    sender_type = Column(String(20))  # user, interviewer, system
    interviewer_id = Column(String(50), nullable=True)  # 面试官ID
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关系
    interview = relationship("Interview", back_populates="messages")


class Feedback(Base):
    """面试反馈模型"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), unique=True)
    summary = Column(Text)
    overall_score = Column(Float)
    skill_scores = Column(JSON)  # 各项技能评分
    strengths = Column(JSON)  # 优势
    improvements = Column(JSON)  # 改进建议
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关系
    interview = relationship("Interview", back_populates="feedback")
    interviewer_feedbacks = relationship("InterviewerFeedback", back_populates="feedback")


class InterviewerFeedback(Base):
    """面试官反馈模型"""
    __tablename__ = "interviewer_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"))
    interviewer_id = Column(String(50))  # 面试官ID
    name = Column(String(100))  # 面试官名称
    role = Column(String(100))  # 面试官角色
    content = Column(Text)  # 反馈内容
    
    # 关系
    feedback = relationship("Feedback", back_populates="interviewer_feedbacks")
