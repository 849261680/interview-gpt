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
from ...models.schemas import Interview
from ...models.pydantic_models import InterviewCreate, InterviewResponse, MessageCreate, MessageResponse, FeedbackResponse
# 使用新的CrewAI架构，不再需要InterviewerFactory
from ...services.ai.crewai_integration import get_crewai_integration
from ...services.interview_service import (
    create_interview_service,
    get_interview_service,
    send_message_service,
    get_interview_messages_service,
    end_interview_service
)
import logging
from datetime import datetime

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()


@router.post("/", response_model=InterviewResponse)
async def create_interview(
    background_tasks: BackgroundTasks,
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
        # 立即创建面试记录，不等待CrewAI执行
        interview_data = InterviewCreate(
            position=position,
            difficulty=difficulty
        )
        
        logger.info(f"调用create_interview_service，execute_crewai=False")
        # 调用服务层创建面试（只创建记录，不执行CrewAI）
        interview = await create_interview_service(interview_data, resume, db, execute_crewai=False)
        logger.info(f"create_interview_service完成，面试ID={interview.id}")
        
        # 后台任务异步启动CrewAI流程
        background_tasks.add_task(
            start_crewai_interview_background,
            interview.id,
            position,
            difficulty,
            interview.resume_content or ""
        )
        
        logger.info(f"面试创建成功，ID={interview.id}，CrewAI流程已在后台启动")
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
    """处理AI面试官回复的后台任务 - 使用CrewAI Flow架构优先"""
    try:
        logger.info(f"生成AI回复: 面试ID={interview_id}, 面试官ID={interviewer_id}")
        
        # 获取面试历史消息
        messages = await get_interview_messages_service(interview_id, db)
        
        # 使用CrewAI集成获取面试官回复
        crewai_integration = get_crewai_integration()
        
        if not crewai_integration.is_available():
            logger.warning("CrewAI不可用，使用默认回复")
            response = f"感谢您的回答。作为{interviewer_id}面试官，我需要进一步了解您的情况。"
        else:
            # 获取面试会话信息
            interview = await get_interview_service(interview_id, db)
            if not interview:
                logger.error(f"面试会话不存在: {interview_id}")
                return
            
            # 检查是否使用Flow架构
            status = crewai_integration.get_status()
            if status.get('architecture_mode') == 'flow':
                logger.info(f"使用Flow架构处理面试回复: {interview_id}")
                
                # 获取Flow状态
                flow_status = crewai_integration.get_interview_status(str(interview_id))
                if flow_status.get('status') == 'not_found':
                    # 如果Flow不存在，创建新的Flow
                    logger.info(f"创建新的面试Flow: {interview_id}")
                    result = await crewai_integration.conduct_interview(
                        resume_context=interview.resume_content or "",
                        position=interview.position,
                        difficulty=interview.difficulty,
                        interview_id=str(interview_id)
                    )
                    
                    if result.get('status') == 'success':
                        response = "面试Flow已启动，正在进行全面评估..."
                    else:
                        response = f"面试Flow启动失败: {result.get('error', '未知错误')}"
                else:
                    # Flow已存在，获取当前状态信息
                    report = crewai_integration.get_interview_report(str(interview_id))
                    if report:
                        current_stage = report.get('current_stage', 'unknown')
                        response = f"面试正在进行中，当前阶段: {current_stage}"
                    else:
                        response = "面试Flow正在处理中，请稍候..."
            else:
                # 使用传统Crew架构
                logger.info(f"使用传统Crew架构处理面试回复: {interview_id}")
                
                # 转换消息格式为CrewAI需要的格式
                message_history = []
                for msg in messages:
                    message_history.append({
                        "sender": msg.sender,
                        "content": msg.content,
                        "message_type": msg.message_type,
                        "created_at": msg.created_at.isoformat() if msg.created_at else None
                    })
                
                # 使用传统CrewAI进行面试轮次
                response = await crewai_integration.conduct_interview_round(
                    interviewer_type=interviewer_id,
                    messages=message_history,
                    position=interview.position,
                    difficulty=interview.difficulty
                )
        
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
    """生成面试评估的后台任务 - 使用CrewAI Flow架构优先"""
    try:
        logger.info(f"生成面试评估: 面试ID={interview_id}")
        
        # 获取面试会话和历史消息
        interview = await get_interview_service(interview_id, db)
        messages = await get_interview_messages_service(interview_id, db)
        
        if not interview:
            logger.error(f"面试会话不存在: {interview_id}")
            return
        
        # 使用CrewAI集成生成综合评估
        crewai_integration = get_crewai_integration()
        
        if not crewai_integration.is_available():
            logger.warning("CrewAI不可用，跳过评估生成")
            return
        
        try:
            # 检查是否使用Flow架构
            status = crewai_integration.get_status()
            if status.get('architecture_mode') == 'flow':
                logger.info(f"使用Flow架构生成评估: {interview_id}")
                
                # 获取Flow报告
                report = crewai_integration.get_interview_report(str(interview_id))
                if report and report.get('status') == 'completed':
                    logger.info(f"✅ Flow面试评估已完成: 面试ID={interview_id}")
                    # TODO: 保存Flow评估结果到数据库
                else:
                    logger.info(f"Flow面试尚未完成，当前状态: {report.get('status') if report else 'unknown'}")
            else:
                # 使用传统Crew架构
                logger.info(f"使用传统Crew架构生成评估: {interview_id}")
                
                # 转换消息格式
                message_history = []
                for msg in messages:
                    message_history.append({
                        "sender": msg.sender,
                        "content": msg.content,
                        "message_type": msg.message_type,
                        "created_at": msg.created_at.isoformat() if msg.created_at else None
                    })
                
                # 使用CrewAI进行完整面试流程
                evaluation_result = await crewai_integration.conduct_interview(
                    resume_context=interview.resume_content or "",
                    position=interview.position,
                    difficulty=interview.difficulty
                )
                
                logger.info(f"✅ 传统面试评估生成完成: 面试ID={interview_id}")
                # TODO: 保存传统评估结果到数据库
            
        except Exception as e:
            logger.error(f"CrewAI评估生成失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"生成面试评估失败: {str(e)}")


# === CrewAI Flow 相关API端点 ===

@router.get("/{interview_id}/flow/status")
async def get_flow_status(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    获取面试Flow状态
    
    - **interview_id**: 面试ID
    """
    logger.info(f"获取Flow状态: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = await get_interview_service(interview_id, db)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 获取CrewAI集成服务
        crewai_integration = get_crewai_integration()
        
        if not crewai_integration.is_available():
            raise HTTPException(status_code=503, detail="CrewAI服务不可用")
        
        # 获取Flow状态
        status = crewai_integration.get_interview_status(str(interview_id))
        
        return {
            "interview_id": interview_id,
            "flow_status": status,
            "architecture_mode": crewai_integration.get_status().get('architecture_mode', 'unknown')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Flow状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取Flow状态失败: {str(e)}")


@router.get("/{interview_id}/flow/report")
async def get_flow_report(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    获取面试Flow报告
    
    - **interview_id**: 面试ID
    """
    logger.info(f"获取Flow报告: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = await get_interview_service(interview_id, db)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 获取CrewAI集成服务
        crewai_integration = get_crewai_integration()
        
        if not crewai_integration.is_available():
            raise HTTPException(status_code=503, detail="CrewAI服务不可用")
        
        # 获取Flow报告
        report = crewai_integration.get_interview_report(str(interview_id))
        
        if not report:
            raise HTTPException(status_code=404, detail="Flow报告不存在")
        
        return {
            "interview_id": interview_id,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Flow报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取Flow报告失败: {str(e)}")


@router.post("/{interview_id}/flow/start")
async def start_flow(
    interview_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    启动面试Flow
    
    - **interview_id**: 面试ID
    """
    logger.info(f"启动面试Flow: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = await get_interview_service(interview_id, db)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 获取CrewAI集成服务
        crewai_integration = get_crewai_integration()
        
        if not crewai_integration.is_available():
            raise HTTPException(status_code=503, detail="CrewAI服务不可用")
        
        # 检查Flow是否已存在
        status = crewai_integration.get_interview_status(str(interview_id))
        if status.get('status') != 'not_found':
            return {
                "message": "Flow已存在",
                "interview_id": interview_id,
                "current_status": status
            }
        
        # 后台任务启动Flow
        background_tasks.add_task(
            start_flow_background,
            interview_id,
            interview.position,
            interview.difficulty,
            interview.resume_content or "",
            crewai_integration
        )
        
        return {
            "message": "Flow启动中",
            "interview_id": interview_id,
            "status": "starting"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动Flow失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动Flow失败: {str(e)}")


@router.delete("/{interview_id}/flow")
async def cleanup_flow(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    清理面试Flow
    
    - **interview_id**: 面试ID
    """
    logger.info(f"清理面试Flow: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = await get_interview_service(interview_id, db)
        if not interview:
            raise HTTPException(status_code=404, detail="面试不存在")
        
        # 获取CrewAI集成服务
        crewai_integration = get_crewai_integration()
        
        if not crewai_integration.is_available():
            raise HTTPException(status_code=503, detail="CrewAI服务不可用")
        
        # 清理Flow
        success = crewai_integration.cleanup_interview(str(interview_id))
        
        return {
            "message": "Flow清理完成" if success else "Flow清理失败",
            "interview_id": interview_id,
            "success": success
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清理Flow失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理Flow失败: {str(e)}")


# 后台任务：启动Flow
async def start_flow_background(
    interview_id: int,
    position: str,
    difficulty: str,
    resume_context: str,
    crewai_integration
):
    """启动Flow的后台任务"""
    try:
        logger.info(f"后台启动Flow: 面试ID={interview_id}")
        
        # 启动面试Flow
        result = await crewai_integration.conduct_interview(
            resume_context=resume_context,
            position=position,
            difficulty=difficulty,
            interview_id=str(interview_id)
        )
        
        if result.get('status') == 'success':
            logger.info(f"✅ Flow启动成功: 面试ID={interview_id}")
        else:
            logger.error(f"❌ Flow启动失败: 面试ID={interview_id}, 错误: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"后台启动Flow失败: 面试ID={interview_id}, 错误: {str(e)}")


async def start_crewai_interview_background(
    interview_id: int,
    position: str,
    difficulty: str,
    resume_content: str
):
    """
    后台任务：异步启动CrewAI面试流程
    
    Args:
        interview_id: 面试ID
        position: 面试职位
        difficulty: 面试难度
        resume_content: 简历内容
    """
    try:
        logger.info(f"后台启动CrewAI面试流程: 面试ID={interview_id}")
        
        # 获取CrewAI集成服务
        crewai_integration = get_crewai_integration()
        
        if not crewai_integration.is_available():
            logger.warning(f"CrewAI不可用，面试ID={interview_id}将使用传统模式")
            return
        
        # 异步执行CrewAI面试流程
        result = await crewai_integration.conduct_interview(
            resume_context=resume_content,
            position=position,
            difficulty=difficulty,
            interview_id=str(interview_id)
        )
        
        if result.get('status') == 'success':
            logger.info(f"CrewAI面试流程启动成功: 面试ID={interview_id}")
            
            # 创建新的数据库会话来更新状态
            from ...db.database import SessionLocal
            db = SessionLocal()
            try:
                interview = db.query(Interview).filter(Interview.id == interview_id).first()
                if interview:
                    interview.status = "active"
                    db.commit()
                    logger.info(f"面试状态已更新为active: 面试ID={interview_id}")
            finally:
                db.close()
                
        else:
            logger.error(f"CrewAI面试流程启动失败: 面试ID={interview_id}, 错误={result.get('error')}")
            
    except Exception as e:
        logger.error(f"后台CrewAI流程执行失败: 面试ID={interview_id}, 错误={str(e)}")
        
        # 更新面试状态为错误
        try:
            from ...db.database import SessionLocal
            db = SessionLocal()
            try:
                interview = db.query(Interview).filter(Interview.id == interview_id).first()
                if interview:
                    interview.status = "error"
                    db.commit()
                    logger.info(f"面试状态已更新为error: 面试ID={interview_id}")
            finally:
                db.close()
        except Exception as db_error:
            logger.error(f"更新面试状态失败: {str(db_error)}")
