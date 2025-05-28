"""
面试API端点
处理面试会话的创建、获取、更新和消息交互
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

# 正确的相对导入路径
from ...db.database import get_db
from ...models.interview import Interview
from ...models.pydantic_models import InterviewCreate, InterviewResponse, MessageCreate, MessageResponse, FeedbackResponse
from ...agents.interviewer_factory import InterviewerFactory
from ...services.interview_service import (
    create_interview_service,
    get_interview_service,
    send_message_service,
    get_interview_messages_service,
    end_interview_service
)
import logging

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()


@router.post("/", response_model=InterviewResponse)
async def create_interview(
    position: str = Form(...),
    difficulty: str = Form(...),
    resume: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    创建新的面试会话
    
    - **position**: 面试职位
    - **difficulty**: 面试难度 (easy, medium, hard)
    - **resume**: 可选的简历文件
    """
    logger.info(f"创建面试会话: 职位={position}, 难度={difficulty}")
    
    try:
        # 调用服务层创建面试
        interview_data = InterviewCreate(
            position=position,
            difficulty=difficulty
        )
        interview = await create_interview_service(interview_data, resume, db)
        return interview
    except Exception as e:
        logger.error(f"创建面试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建面试失败: {str(e)}")


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    获取面试会话详情
    
    - **interview_id**: 面试ID
    """
    logger.info(f"获取面试会话: ID={interview_id}")
    
    interview = await get_interview_service(interview_id, db)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    return interview


@router.post("/{interview_id}/messages", response_model=MessageResponse)
async def send_message(
    interview_id: int,
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    发送面试消息
    
    - **interview_id**: 面试ID
    - **message**: 消息内容
    """
    logger.info(f"发送面试消息: 面试ID={interview_id}")
    
    try:
        # 获取面试会话
        interview = await get_interview_service(interview_id, db)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 发送消息
        user_message = await send_message_service(interview_id, message, db)
        
        # 后台任务生成AI回复
        background_tasks.add_task(
            process_ai_response,
            interview_id,
            message.interviewer_id,
            db
        )
        
        return user_message
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")


@router.get("/{interview_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    获取面试消息历史
    
    - **interview_id**: 面试ID
    """
    logger.info(f"获取面试消息: 面试ID={interview_id}")
    
    messages = await get_interview_messages_service(interview_id, db)
    return messages


@router.post("/{interview_id}/end", response_model=InterviewResponse)
async def end_interview(
    interview_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    结束面试会话并生成评估
    
    - **interview_id**: 面试ID
    """
    logger.info(f"结束面试: ID={interview_id}")
    
    try:
        # 标记面试为已完成
        interview = await end_interview_service(interview_id, db)
        
        # 后台任务生成面试评估
        background_tasks.add_task(
            generate_interview_feedback,
            interview_id,
            db
        )
        
        return interview
    except Exception as e:
        logger.error(f"结束面试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"结束面试失败: {str(e)}")


# 后台任务：处理AI回复
async def process_ai_response(interview_id: int, interviewer_id: str, db: Session):
    """处理AI面试官回复的后台任务"""
    try:
        logger.info(f"生成AI回复: 面试ID={interview_id}, 面试官ID={interviewer_id}")
        
        # 获取面试历史消息
        messages = await get_interview_messages_service(interview_id, db)
        
        # 使用面试官工厂获取对应面试官
        interviewer = InterviewerFactory.get_interviewer(interviewer_id)
        
        # 生成回复
        response = await interviewer.generate_response(messages)
        
        # 保存回复
        message_data = MessageCreate(
            content=response,
            sender_type="interviewer",
            interviewer_id=interviewer_id
        )
        await send_message_service(interview_id, message_data, db)
        
    except Exception as e:
        logger.error(f"生成AI回复失败: {str(e)}")


# 后台任务：生成面试评估
async def generate_interview_feedback(interview_id: int, db: Session):
    """生成面试评估的后台任务"""
    try:
        logger.info(f"生成面试评估: 面试ID={interview_id}")
        
        # 获取面试会话和历史消息
        interview = await get_interview_service(interview_id, db)
        messages = await get_interview_messages_service(interview_id, db)
        
        # TODO: 实现评估生成逻辑
        # 这里将在后续实现，使用CrewAI和DEEPSEEK API生成综合评估
        
    except Exception as e:
        logger.error(f"生成面试评估失败: {str(e)}")
