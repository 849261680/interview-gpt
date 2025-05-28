"""
面试服务
实现面试相关的业务逻辑，处理面试会话的创建、管理和交互
"""
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
import logging
import os
from datetime import datetime
from fastapi import UploadFile
import uuid

from ..models.schemas import Interview, Message
from ..models.pydantic_models import InterviewCreate, InterviewResponse, MessageCreate, MessageResponse

# 设置日志
logger = logging.getLogger(__name__)


async def create_interview_service(
    interview_data: InterviewCreate,
    resume: Optional[UploadFile] = None,
    db: Session = None
) -> InterviewResponse:
    """
    创建新的面试会话
    
    Args:
        interview_data: 面试创建数据
        resume: 简历文件（可选）
        db: 数据库会话
        
    Returns:
        InterviewResponse: 创建的面试会话数据
    """
    logger.info(f"创建面试会话服务: {interview_data.position}, 难度={interview_data.difficulty}")
    
    # 处理简历上传（如果有）
    resume_path = None
    if resume:
        # 创建上传目录（如果不存在）
        upload_dir = os.path.join("uploads", "resumes")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_extension = os.path.splitext(resume.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        resume_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(resume_path, "wb") as f:
            content = await resume.read()
            f.write(content)
        
        logger.info(f"简历已保存: {resume_path}")
    
    # 创建面试记录
    interview = Interview(
        position=interview_data.position,
        difficulty=interview_data.difficulty,
        status="active",
        resume_path=resume_path
    )
    
    # 保存到数据库
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    # 生成系统消息作为欢迎
    welcome_message = Message(
        interview_id=interview.id,
        content="欢迎参加模拟面试！我们将从技术面试开始，请放松并准备好回答问题。",
        sender_type="system"
    )
    db.add(welcome_message)
    
    # 生成初始面试官消息
    initial_message = Message(
        interview_id=interview.id,
        content=f"你好，我是张工，技术面试官。今天我们将就{interview_data.position}职位进行面试。首先，请简单介绍一下你的技术背景和相关经验。",
        sender_type="interviewer",
        interviewer_id="technical"
    )
    db.add(initial_message)
    db.commit()
    
    # 返回InterviewResponse模型对象
    return InterviewResponse(
        id=interview.id,
        position=interview.position,
        difficulty=interview.difficulty,
        status=interview.status,
        created_at=interview.created_at,
        completed_at=interview.completed_at,
        resume_path=interview.resume_path,
        overall_score=interview.overall_score
    )


async def get_interview_service(interview_id: int, db: Session) -> Optional[InterviewResponse]:
    """
    获取面试会话
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        Optional[InterviewResponse]: 面试会话数据，不存在则返回None
    """
    logger.info(f"获取面试会话服务: ID={interview_id}")
    
    # 查询面试记录
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        return None
    
    # 返回InterviewResponse模型对象
    return InterviewResponse(
        id=interview.id,
        position=interview.position,
        difficulty=interview.difficulty,
        status=interview.status,
        created_at=interview.created_at,
        completed_at=interview.completed_at,
        resume_path=interview.resume_path,
        overall_score=interview.overall_score
    )


async def send_message_service(
    interview_id: int,
    message_data: MessageCreate,
    db: Session
) -> MessageResponse:
    """
    发送面试消息
    
    Args:
        interview_id: 面试ID
        message_data: 消息数据
        db: 数据库会话
        
    Returns:
        MessageResponse: 保存的消息数据
    """
    logger.info(f"发送面试消息服务: 面试ID={interview_id}")
    
    # 创建消息记录
    message = Message(
        interview_id=interview_id,
        content=message_data.content,
        sender_type=message_data.sender_type
    )
    
    # 如果有面试官ID，添加到消息中
    if hasattr(message_data, 'interviewer_id') and message_data.interviewer_id:
        message.interviewer_id = message_data.interviewer_id
    
    # 保存到数据库
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # 返回MessageResponse模型对象
    return MessageResponse(
        id=message.id,
        content=message.content,
        sender_type=message.sender_type,
        interviewer_id=message.interviewer_id,
        timestamp=message.timestamp,
        metadata=None  # 默认无元数据
    )


async def get_interview_messages_service(
    interview_id: int,
    db: Session
) -> List[MessageResponse]:
    """
    获取面试消息历史
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        List[MessageResponse]: 消息列表
    """
    logger.info(f"获取面试消息历史服务: 面试ID={interview_id}")
    
    # 查询消息记录
    messages = db.query(Message)\
        .filter(Message.interview_id == interview_id)\
        .order_by(Message.timestamp)\
        .all()
    
    # 返回MessageResponse列表
    return [
        MessageResponse(
            id=message.id,
            content=message.content,
            sender_type=message.sender_type,
            interviewer_id=message.interviewer_id,
            timestamp=message.timestamp,
            metadata=None  # 默认无元数据
        )
        for message in messages
    ]


async def end_interview_service(
    interview_id: int,
    db: Session
) -> InterviewResponse:
    """
    结束面试会话
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        InterviewResponse: 更新后的面试会话数据
    """
    logger.info(f"结束面试服务: ID={interview_id}")
    
    # 查询面试记录
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise ValueError(f"面试不存在: ID={interview_id}")
    
    # 更新面试状态
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    
    # 保存到数据库
    db.commit()
    db.refresh(interview)
    
    # 返回InterviewResponse模型对象
    return InterviewResponse(
        id=interview.id,
        position=interview.position,
        difficulty=interview.difficulty,
        status=interview.status,
        created_at=interview.created_at,
        completed_at=interview.completed_at,
        resume_path=interview.resume_path,
        overall_score=interview.overall_score
    )
