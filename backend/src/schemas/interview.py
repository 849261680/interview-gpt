"""
面试相关的Pydantic模型
定义API请求和响应的数据结构
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class InterviewBase(BaseModel):
    """面试基础模型"""
    position: str = Field(..., description="面试职位")
    difficulty: str = Field(..., description="面试难度: easy, medium, hard")


class InterviewCreate(InterviewBase):
    """创建面试请求模型"""
    pass


class InterviewResponse(InterviewBase):
    """面试响应模型"""
    id: int
    status: str = Field(..., description="面试状态: active, completed, cancelled")
    created_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[float] = None
    
    class Config:
        """Pydantic配置"""
        from_attributes = True


class MessageBase(BaseModel):
    """消息基础模型"""
    content: str = Field(..., description="消息内容")
    sender_type: str = Field(..., description="发送者类型: user, interviewer, system")
    interviewer_id: Optional[str] = Field(None, description="面试官ID (当sender_type为interviewer时需要)")


class MessageCreate(MessageBase):
    """创建消息请求模型"""
    pass


class MessageResponse(MessageBase):
    """消息响应模型"""
    id: int
    interview_id: int
    timestamp: datetime
    
    class Config:
        """Pydantic配置"""
        from_attributes = True


class SkillScore(BaseModel):
    """技能评分模型"""
    name: str = Field(..., description="技能名称")
    score: float = Field(..., description="评分 (0-100)")
    feedback: str = Field(..., description="评价内容")


class InterviewerFeedbackItem(BaseModel):
    """面试官评价项"""
    interviewer_id: str
    name: str
    role: str
    feedback: str


class FeedbackBase(BaseModel):
    """评估反馈基础模型"""
    summary: str = Field(..., description="总体评价")
    overall_score: float = Field(..., description="总体评分 (0-100)")
    skill_scores: List[SkillScore] = Field(..., description="各项技能评分")
    strengths: List[str] = Field(..., description="优势列表")
    improvements: List[str] = Field(..., description="改进建议列表")
    interviewer_feedbacks: List[InterviewerFeedbackItem] = Field(..., description="各面试官评价")


class FeedbackCreate(FeedbackBase):
    """创建评估反馈请求模型"""
    pass


class FeedbackResponse(FeedbackBase):
    """评估反馈响应模型"""
    id: int
    interview_id: int
    created_at: datetime
    
    class Config:
        """Pydantic配置"""
        from_attributes = True


class AudioProcessRequest(BaseModel):
    """语音处理请求模型"""
    audio_data: str = Field(..., description="Base64编码的音频数据")
    target_language: str = Field("zh", description="目标语言")


class AudioProcessResponse(BaseModel):
    """语音处理响应模型"""
    text: str = Field(..., description="转换后的文本")
    confidence: float = Field(..., description="识别置信度")
