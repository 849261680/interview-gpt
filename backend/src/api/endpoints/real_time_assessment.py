"""
实时评估API端点
提供面试过程中的实时评估和反馈功能
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from ...services.real_time_assessment import real_time_assessment_service
from ...utils.exceptions import AssessmentError
from ...config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/real-time-assessment", tags=["实时评估"])


class StartAssessmentRequest(BaseModel):
    """开始实时评估请求模型"""
    interview_id: int = Field(..., description="面试ID")
    position: str = Field(..., description="面试职位")
    difficulty: str = Field(..., description="面试难度")
    interviewer_type: str = Field(default="technical", description="面试官类型")


class ProcessMessageRequest(BaseModel):
    """处理消息请求模型"""
    interview_id: int = Field(..., description="面试ID")
    message: Dict[str, Any] = Field(..., description="消息内容")
    interviewer_type: Optional[str] = Field(default=None, description="面试官类型")


class AssessmentResponse(BaseModel):
    """评估响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")


@router.post("/start", response_model=AssessmentResponse)
async def start_real_time_assessment(
    request: StartAssessmentRequest,
    background_tasks: BackgroundTasks
):
    """
    开始实时评估会话
    
    Args:
        request: 开始评估请求
        background_tasks: 后台任务
        
    Returns:
        AssessmentResponse: 评估响应
    """
    try:
        logger.info(f"开始实时评估: 面试ID={request.interview_id}")
        
        # 启动实时评估会话
        result = await real_time_assessment_service.start_assessment_session(
            interview_id=request.interview_id,
            position=request.position,
            difficulty=request.difficulty,
            interviewer_type=request.interviewer_type
        )
        
        # 添加会话清理任务
        background_tasks.add_task(
            _schedule_session_cleanup,
            request.interview_id
        )
        
        return AssessmentResponse(
            success=True,
            message="实时评估会话已启动",
            data=result
        )
        
    except AssessmentError as e:
        logger.error(f"启动实时评估失败: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"启动实时评估异常: {e}")
        raise HTTPException(status_code=500, detail="实时评估服务暂时不可用")


@router.post("/process-message", response_model=AssessmentResponse)
async def process_message_for_assessment(request: ProcessMessageRequest):
    """
    处理消息并更新实时评估
    
    Args:
        request: 处理消息请求
        
    Returns:
        AssessmentResponse: 评估响应
    """
    try:
        logger.info(f"处理消息: 面试ID={request.interview_id}")
        
        # 处理消息并更新评估
        result = await real_time_assessment_service.process_message(
            interview_id=request.interview_id,
            message=request.message,
            interviewer_type=request.interviewer_type
        )
        
        return AssessmentResponse(
            success=True,
            message="消息处理完成",
            data=result
        )
        
    except AssessmentError as e:
        logger.error(f"处理消息失败: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"处理消息异常: {e}")
        raise HTTPException(status_code=500, detail="消息处理失败")


@router.get("/session/{interview_id}", response_model=AssessmentResponse)
async def get_assessment_session(interview_id: int):
    """
    获取实时评估会话信息
    
    Args:
        interview_id: 面试ID
        
    Returns:
        AssessmentResponse: 会话信息
    """
    try:
        logger.info(f"获取评估会话: 面试ID={interview_id}")
        
        # 获取会话摘要
        summary = await real_time_assessment_service.get_session_summary(interview_id)
        
        return AssessmentResponse(
            success=True,
            message="获取会话信息成功",
            data=summary
        )
        
    except AssessmentError as e:
        logger.error(f"获取会话信息失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取会话信息异常: {e}")
        raise HTTPException(status_code=500, detail="获取会话信息失败")


@router.post("/end/{interview_id}", response_model=AssessmentResponse)
async def end_assessment_session(interview_id: int):
    """
    结束实时评估会话
    
    Args:
        interview_id: 面试ID
        
    Returns:
        AssessmentResponse: 结束响应
    """
    try:
        logger.info(f"结束评估会话: 面试ID={interview_id}")
        
        # 结束评估会话
        result = await real_time_assessment_service.end_assessment_session(interview_id)
        
        return AssessmentResponse(
            success=True,
            message="实时评估会话已结束",
            data=result
        )
        
    except AssessmentError as e:
        logger.error(f"结束会话失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"结束会话异常: {e}")
        raise HTTPException(status_code=500, detail="结束会话失败")


@router.get("/health")
async def real_time_assessment_health():
    """
    实时评估服务健康检查
    
    Returns:
        Dict: 服务状态
    """
    try:
        # 获取活跃会话数量
        active_sessions = len(real_time_assessment_service.assessment_sessions)
        
        return {
            "status": "healthy",
            "active_sessions": active_sessions,
            "service": "real_time_assessment",
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "real_time_assessment"
        }


@router.post("/cleanup")
async def cleanup_expired_sessions():
    """
    清理过期的评估会话
    
    Returns:
        Dict: 清理结果
    """
    try:
        logger.info("开始清理过期会话")
        
        # 执行清理
        real_time_assessment_service.cleanup_expired_sessions()
        
        return {
            "success": True,
            "message": "过期会话清理完成",
            "active_sessions": len(real_time_assessment_service.assessment_sessions)
        }
        
    except Exception as e:
        logger.error(f"清理过期会话失败: {e}")
        raise HTTPException(status_code=500, detail="清理失败")


@router.get("/metrics/{interview_id}")
async def get_assessment_metrics(interview_id: int):
    """
    获取评估指标详情
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict: 评估指标
    """
    try:
        if interview_id not in real_time_assessment_service.assessment_sessions:
            raise HTTPException(status_code=404, detail="评估会话不存在")
        
        session = real_time_assessment_service.assessment_sessions[interview_id]
        
        # 构建详细指标
        metrics = {
            "conversation_metrics": session['conversation_metrics'],
            "dimension_scores": dict(session['dimension_scores']),
            "assessment_history": session['assessment_history'][-10:],  # 最近10次评估
            "feedback_history": session['feedback_history'][-5:],  # 最近5次反馈
            "performance_analysis": {
                "total_messages": session['message_count'],
                "user_messages": len(session['user_messages']),
                "interviewer_messages": len(session['interviewer_messages']),
                "session_duration": (
                    session['last_assessment_time'] - session['start_time']
                ).total_seconds(),
                "average_response_length": (
                    sum(msg['length'] for msg in session['user_messages']) / 
                    len(session['user_messages'])
                ) if session['user_messages'] else 0
            }
        }
        
        return {
            "success": True,
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"获取评估指标失败: {e}")
        raise HTTPException(status_code=500, detail="获取指标失败")


# 辅助函数

async def _schedule_session_cleanup(interview_id: int):
    """安排会话清理任务"""
    import asyncio
    
    # 等待最大会话时长
    await asyncio.sleep(settings.get('MAX_SESSION_DURATION', 7200))
    
    try:
        # 检查会话是否仍然存在
        if interview_id in real_time_assessment_service.assessment_sessions:
            await real_time_assessment_service.end_assessment_session(interview_id)
            logger.info(f"自动清理会话: {interview_id}")
    except Exception as e:
        logger.error(f"自动清理会话失败: {interview_id}, 错误: {e}")


# 添加路由到主应用
def include_real_time_assessment_routes(app):
    """将实时评估路由添加到主应用"""
    app.include_router(router) 