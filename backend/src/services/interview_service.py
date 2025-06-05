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

# 🔄 使用YAML配置的顺序流程管理器
from .interview.crewai_yaml_sequential_manager import CrewAIYAMLSequentialManager

# 导入简历解析器
from .resume_parser import resume_parser

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
    logger.info(f"创建面试会话服务: {interview_data.position}")
    
    try:
        # 处理简历文件
        resume_context = ""
        resume_path = None
        if resume:
            logger.info(f"处理简历文件: {resume.filename}")
            
            try:
                # 创建临时文件保存上传的简历
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume.filename)[1]) as temp_file:
                    resume_content = await resume.read()
                    temp_file.write(resume_content)
                    temp_file_path = temp_file.name
                
                # 使用简历解析器提取文本内容
                parsed_result = resume_parser.parse_resume(temp_file_path)
                
                if parsed_result.get('success', False):
                    resume_context = parsed_result.get('raw_text', '')
                    logger.info(f"✅ 简历解析成功: {len(resume_context)} 字符")
                    
                    # 保存简历文件到永久位置
                    upload_dir = "uploads/resumes"
                    os.makedirs(upload_dir, exist_ok=True)
                    permanent_filename = f"{uuid.uuid4()}_{resume.filename}"
                    resume_path = os.path.join(upload_dir, permanent_filename)
                    
                    # 复制临时文件到永久位置
                    import shutil
                    shutil.copy2(temp_file_path, resume_path)
                    logger.info(f"✅ 简历文件已保存: {resume_path}")
                else:
                    logger.error(f"❌ 简历解析失败: {parsed_result.get('error', '未知错误')}")
                    resume_context = f"简历文件解析失败: {parsed_result.get('error', '未知错误')}"
                
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"❌ 简历文件处理失败: {str(e)}")
                resume_context = f"简历文件处理失败: {str(e)}"
        
        # 创建面试记录
        interview = Interview(
            position=interview_data.position,
            difficulty=interview_data.difficulty,
            resume_context=resume_context,
            resume_path=resume_path,
            status="active"
        )
        
        db.add(interview)
        db.commit()
        db.refresh(interview)
        
        logger.info(f"✅ 面试会话创建成功: ID={interview.id}")
        
        # 🔄 使用YAML配置的顺序流程管理器初始化面试
        try:
            manager = CrewAIYAMLSequentialManager(interview.id, db)
            await manager.initialize_interview()
            logger.info(f"✅ 顺序架构面试管理器初始化成功: ID={interview.id}")
        except Exception as e:
            logger.warning(f"⚠️ 顺序架构管理器初始化失败: {str(e)}，将继续使用基础功能")
        
        return InterviewResponse(
            id=interview.id,
            position=interview.position,
            difficulty=interview.difficulty,
            status=interview.status,
            created_at=interview.created_at,
            messages=[]
        )
        
    except Exception as e:
        logger.error(f"❌ 创建面试会话失败: {str(e)}")
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
        
        # 🔄 使用YAML配置的顺序流程管理器处理消息
        try:
            manager = CrewAIYAMLSequentialManager(interview_id, db)
            response_content = await manager.process_user_message(message_data.content)
            logger.info(f"✅ 顺序架构处理用户消息成功: {message_data.content[:50]}...")
        except Exception as e:
            logger.warning(f"⚠️ 顺序架构处理失败: {str(e)}，使用简化回复")
        response_content = f"收到您的消息：{message_data.content}\n\n我们的AI面试团队正在分析中，请稍候..."
        
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
