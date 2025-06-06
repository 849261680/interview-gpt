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
import tempfile
import aiofiles

from ..models.schemas import Interview, Message
from ..models.pydantic_models import InterviewCreate, InterviewResponse, MessageCreate, MessageResponse

# 🔄 使用AI集成服务（Flow架构优先）
from .ai.crewai_integration import get_crewai_integration

# 设置日志
logger = logging.getLogger(__name__)


async def create_interview_service(
    interview_data: InterviewCreate,
    resume: Optional[UploadFile] = None,
    db: Session = None,
    execute_crewai: bool = True
) -> InterviewResponse:
    """
    创建新的面试会话
    
    Args:
        interview_data: 面试创建数据
        resume: 简历文件（可选）
        db: 数据库会话
        execute_crewai: 是否立即执行CrewAI流程，默认为True
        
    Returns:
        InterviewResponse: 创建的面试会话数据
    """
    logger.info(f"创建面试会话服务: {interview_data.position}, execute_crewai={execute_crewai}")
    
    try:
        # 处理简历文件
        resume_content = None
        resume_filename = None
        
        if resume:
            logger.info(f"处理简历文件: {resume.filename}")
            
            # 验证文件类型
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/plain']
            
            if resume.content_type not in allowed_types:
                raise ValueError(f"不支持的文件类型: {resume.content_type}")
            
            # 验证文件大小 (10MB)
            content = await resume.read()
            if len(content) > 10 * 1024 * 1024:
                raise ValueError("文件大小不能超过10MB")
            
            # 保存文件
            upload_dir = "uploads/resumes"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_extension = os.path.splitext(resume.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            resume_filename = unique_filename
            
            # 提取简历文本内容（用于CrewAI处理）
            try:
                if resume.content_type == 'application/pdf':
                    # 处理PDF文件
                    import PyPDF2
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        resume_content = ""
                        for page in pdf_reader.pages:
                            resume_content += page.extract_text()
                elif resume.content_type == 'text/plain':
                    # 处理文本文件
                    with open(file_path, 'r', encoding='utf-8') as txt_file:
                        resume_content = txt_file.read()
                else:
                    # 对于Word文档，暂时使用文件路径
                    resume_content = f"简历文件路径: {file_path}"
                    
                logger.info(f"简历内容提取成功，长度: {len(resume_content) if resume_content else 0}")
                
            except Exception as e:
                logger.warning(f"简历内容提取失败: {str(e)}，将使用文件路径")
                resume_content = f"简历文件路径: {file_path}"
        
        # 创建面试记录
        interview = Interview(
            position=interview_data.position,
            difficulty=interview_data.difficulty,
            status="pending",  # 初始状态为pending
            resume_filename=resume_filename,
            resume_content=resume_content,
            created_at=datetime.now()
        )
        
        db.add(interview)
        db.commit()
        db.refresh(interview)
        
        logger.info(f"面试记录创建成功: ID={interview.id}")
        
        # 根据execute_crewai参数决定是否立即执行CrewAI流程
        if execute_crewai:
            logger.info(f"立即执行CrewAI流程: 面试ID={interview.id}")
            
            # 🔄 使用AI集成服务（Flow架构优先）
            crewai_integration = get_crewai_integration()
            
            if crewai_integration.is_available():
                try:
                    # 执行CrewAI面试流程
                    result = await crewai_integration.conduct_interview(
                        resume_context=resume_content or "",
                        position=interview_data.position,
                        difficulty=interview_data.difficulty,
                        interview_id=str(interview.id)
                    )
                    
                    if result.get('status') == 'success':
                        interview.status = "active"
                        db.commit()
                        logger.info(f"CrewAI面试流程启动成功: 面试ID={interview.id}")
                    else:
                        logger.error(f"CrewAI面试流程启动失败: {result.get('error')}")
                        
                except Exception as e:
                    logger.error(f"CrewAI执行失败: {str(e)}")
            else:
                logger.warning("CrewAI不可用，面试将使用传统模式")
                interview.status = "active"
                db.commit()
        else:
            logger.info(f"跳过CrewAI执行，面试ID={interview.id}保持pending状态")
        
        # 返回面试响应
        return InterviewResponse(
            id=interview.id,
            position=interview.position,
            difficulty=interview.difficulty,
            status=interview.status,
            resume_filename=interview.resume_filename,
            resume_content=interview.resume_content,
            created_at=interview.created_at
        )
        
    except Exception as e:
        logger.error(f"创建面试服务失败: {str(e)}")
        if db:
            db.rollback()
        raise


async def get_interview_service(interview_id: int, db: Session) -> Optional[InterviewResponse]:
    """
    获取面试会话信息
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        InterviewResponse: 面试会话数据
    """
    try:
        # 获取面试记录
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            logger.warning(f"面试会话不存在: {interview_id}")
            return None
        
        # 获取消息记录
        messages = db.query(Message).filter(Message.interview_id == interview_id).order_by(Message.created_at).all()
        
        message_responses = [
            MessageResponse(
                id=msg.id,
                interview_id=msg.interview_id,
                sender=msg.sender,
                content=msg.content,
                message_type=msg.message_type,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
        return InterviewResponse(
            id=interview.id,
            position=interview.position,
            difficulty=interview.difficulty,
            status=interview.status,
            created_at=interview.created_at,
            messages=message_responses
        )
        
    except Exception as e:
        logger.error(f"❌ 获取面试会话失败: {str(e)}")
        raise


async def send_message_service(
    interview_id: int,
    message_data: MessageCreate,
    db: Session
) -> Optional[MessageResponse]:
    """
    发送消息到面试会话
    
    Args:
        interview_id: 面试ID
        message_data: 消息数据
        db: 数据库会话
        
    Returns:
        MessageResponse: 消息响应数据
    """
    logger.info(f"发送消息到面试 {interview_id}: {message_data.content[:50]}...")
    
    try:
        # 验证面试是否存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            logger.warning(f"面试会话不存在: {interview_id}")
            return None
        
        # 保存用户消息
        user_message = Message(
            interview_id=interview_id,
            sender="user",
            content=message_data.content,
            message_type="text"
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # 🔄 使用AI集成服务处理消息（Flow架构优先）
        response_content = f"收到您的消息：{message_data.content}\n\n我们的AI面试团队正在分析中，请稍候..."
        try:
            ai_integration = get_crewai_integration()
            if ai_integration.is_available():
                # TODO: 实现具体的消息处理逻辑
                logger.info(f"✅ AI集成服务可用，架构模式: {ai_integration.architecture_mode}")
                # response_content = await ai_integration.process_message(interview_id, message_data.content)
            else:
                logger.warning("⚠️ AI集成服务不可用，使用简化回复")
        except Exception as e:
            logger.warning(f"⚠️ AI集成服务处理失败: {str(e)}，使用简化回复")
        
        # 保存AI响应消息
        if response_content:
            ai_message = Message(
                interview_id=interview_id,
                sender="assistant",
                content=response_content,
                message_type="text"
            )
            db.add(ai_message)
            db.commit()
            db.refresh(ai_message)
            
            return MessageResponse(
                id=ai_message.id,
                interview_id=ai_message.interview_id,
                sender=ai_message.sender,
                content=ai_message.content,
                message_type=ai_message.message_type,
                created_at=ai_message.created_at
            )
        
        return MessageResponse(
            id=user_message.id,
            interview_id=user_message.interview_id,
            sender=user_message.sender,
            content=user_message.content,
            message_type=user_message.message_type,
            created_at=user_message.created_at
        )
        
    except Exception as e:
        logger.error(f"❌ 发送消息失败: {str(e)}")
        db.rollback()
        raise


async def get_interview_status_service(interview_id: int, db: Session) -> Dict[str, Any]:
    """
    获取面试状态信息
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        Dict: 面试状态信息
    """
    try:
        # 验证面试是否存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return {"error": "面试会话不存在"}
        
        # 🔄 使用YAML配置的顺序流程管理器获取状态
        # TODO: 暂时简化，返回基本状态
        # manager = CrewAIYAMLSequentialManager(interview_id, db)
        
        return {
            "interview_id": interview_id,
            "position": interview.position,
            "difficulty": interview.difficulty,
            "status": interview.status,
            "current_stage": "基础面试阶段",  # 暂时固定
            "is_completed": interview.status == "completed",
            "execution_summary": {"status": "简化模式"},
            "architecture": "sequential"  # 🔄 标识使用顺序流程
        }
        
    except Exception as e:
        logger.error(f"❌ 获取面试状态失败: {str(e)}")
        return {"error": f"获取面试状态失败: {str(e)}"}


async def list_interviews_service(db: Session, limit: int = 10, offset: int = 0) -> List[InterviewResponse]:
    """
    获取面试列表
    
    Args:
        db: 数据库会话
        limit: 限制数量
        offset: 偏移量
        
    Returns:
        List[InterviewResponse]: 面试列表
    """
    try:
        interviews = db.query(Interview).order_by(Interview.created_at.desc()).offset(offset).limit(limit).all()
        
        interview_responses = []
        for interview in interviews:
            # 获取每个面试的消息数量
            message_count = db.query(Message).filter(Message.interview_id == interview.id).count()
            
            interview_responses.append(InterviewResponse(
                id=interview.id,
                position=interview.position,
                difficulty=interview.difficulty,
                status=interview.status,
                created_at=interview.created_at,
                messages=[],  # 列表中不包含具体消息，只显示基本信息
                message_count=message_count
            ))
        
        return interview_responses
        
    except Exception as e:
        logger.error(f"❌ 获取面试列表失败: {str(e)}")
        raise


async def delete_interview_service(interview_id: int, db: Session) -> bool:
    """
    删除面试会话
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        bool: 删除是否成功
    """
    try:
        # 验证面试是否存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            logger.warning(f"面试会话不存在: {interview_id}")
            return False
        
        # 删除相关消息
        db.query(Message).filter(Message.interview_id == interview_id).delete()
        
        # 删除面试记录
        db.delete(interview)
        db.commit()
        
        logger.info(f"✅ 面试会话删除成功: {interview_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 删除面试会话失败: {str(e)}")
        db.rollback()
        raise


async def get_interview_messages_service(interview_id: int, db: Session) -> List[MessageResponse]:
    """
    获取面试消息历史
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        List[MessageResponse]: 消息列表
    """
    try:
        # 验证面试是否存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            logger.warning(f"面试会话不存在: {interview_id}")
            return []
        
        # 获取消息记录
        messages = db.query(Message).filter(Message.interview_id == interview_id).order_by(Message.created_at).all()
        
        message_responses = [
            MessageResponse(
                id=msg.id,
                interview_id=msg.interview_id,
                sender=msg.sender,
                content=msg.content,
                message_type=msg.message_type,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
        logger.info(f"✅ 获取面试消息成功: {interview_id}, 消息数量: {len(message_responses)}")
        return message_responses
        
    except Exception as e:
        logger.error(f"❌ 获取面试消息失败: {str(e)}")
        raise


async def end_interview_service(interview_id: int, db: Session) -> Optional[InterviewResponse]:
    """
    结束面试会话
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        InterviewResponse: 更新后的面试会话数据
    """
    try:
        # 验证面试是否存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            logger.warning(f"面试会话不存在: {interview_id}")
            return None
        
        # 更新面试状态为已完成
        interview.status = "completed"
        
        db.commit()
        db.refresh(interview)
        
        # 🔄 使用YAML配置的顺序流程管理器完成面试
        # TODO: 暂时简化，跳过CrewAI处理
        # manager = CrewAIYAMLSequentialManager(interview_id, db)
        # await manager.finalize_interview()
        
        # 获取消息记录
        messages = db.query(Message).filter(Message.interview_id == interview_id).order_by(Message.created_at).all()
        
        message_responses = [
            MessageResponse(
                id=msg.id,
                interview_id=msg.interview_id,
                sender=msg.sender,
                content=msg.content,
                message_type=msg.message_type,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
        logger.info(f"✅ 面试会话结束成功: {interview_id}")
        
        return InterviewResponse(
            id=interview.id,
            position=interview.position,
            difficulty=interview.difficulty,
            status=interview.status,
            created_at=interview.created_at,
            messages=message_responses
        )
        
    except Exception as e:
        logger.error(f"❌ 结束面试会话失败: {str(e)}")
        db.rollback()
        raise
