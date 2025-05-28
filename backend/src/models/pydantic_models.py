"""
Pydantic模型定义
用于API请求和响应的数据验证和序列化
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


# 面试请求和响应模型
class InterviewCreate(BaseModel):
    """创建面试的请求模型"""
    position: str
    difficulty: str
    resume_path: Optional[str] = None


class InterviewResponse(BaseModel):
    """面试响应模型"""
    id: int
    position: str
    difficulty: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    resume_path: Optional[str] = None
    overall_score: Optional[float] = None

    class Config:
        orm_mode = True


# 消息请求和响应模型
class MessageCreate(BaseModel):
    """创建消息的请求模型"""
    content: str
    sender_type: str = "user"
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """消息响应模型"""
    id: int
    content: str
    sender_type: str
    interviewer_id: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


# 反馈响应模型
class InterviewerFeedbackResponse(BaseModel):
    """面试官反馈响应模型"""
    interviewer_id: str
    name: str
    role: str
    content: str

    class Config:
        orm_mode = True


class FeedbackResponse(BaseModel):
    """面试反馈响应模型"""
    id: int
    interview_id: int
    summary: str
    overall_score: float
    skill_scores: Dict[str, Any]
    strengths: List[str]
    improvements: List[str]
    created_at: datetime
    interviewer_feedbacks: List[InterviewerFeedbackResponse]

    class Config:
        orm_mode = True
