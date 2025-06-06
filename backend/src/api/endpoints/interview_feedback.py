"""
面试反馈API端点
提供获取面试评估结果的API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
import json

from ...db.database import get_db
from ...models.schemas import Interview, Message
# 使用新的CrewAI架构，不再需要InterviewerFactory
from ...services.ai.crewai_integration import get_crewai_integration

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/interviews",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{interview_id}/feedback", response_model=Dict[str, Any])
async def get_interview_feedback(interview_id: int, db: Session = Depends(get_db)):
    """
    获取面试评估反馈
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        面试评估反馈数据
    """
    logger.info(f"获取面试ID {interview_id} 的评估反馈")
    
    # 获取面试记录
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        logger.error(f"面试ID {interview_id} 不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试不存在"
        )
    
    # 检查面试是否已完成
    if interview.status != "completed":
        logger.error(f"面试ID {interview_id} 尚未完成，无法生成反馈")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试尚未完成，无法生成反馈"
        )
    
    try:
        # 从数据库中获取面试消息
        messages = db.query(Message).filter(Message.interview_id == interview_id).order_by(Message.timestamp).all()
        messages_data = [
            {
                "id": msg.id,
                "content": msg.content,
                "sender_type": msg.sender_type,
                "interviewer_id": msg.interviewer_id,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        
        # 按面试官分组消息
        interview_content_by_interviewer = {}
        for msg in messages_data:
            if msg.get("sender_type") == "interviewer":
                interviewer_id = msg.get("interviewer_id", "unknown")
                if interviewer_id not in interview_content_by_interviewer:
                    interview_content_by_interviewer[interviewer_id] = []
                interview_content_by_interviewer[interviewer_id].append(msg)
        
        # 使用CrewAI集成获取评估反馈
        crewai_integration = get_crewai_integration()
        feedback_data = {}
        
        if not crewai_integration.is_available():
            logger.warning("CrewAI不可用，返回基础反馈")
            return {
                "interview_id": interview_id,
                "position": interview.position,
                "interview_date": interview.created_at.isoformat(),
                "feedback_by_interviewer": {"message": "CrewAI服务不可用，无法生成详细反馈"},
                "final_assessment": {"message": "CrewAI服务不可用，无法生成最终评估"}
            }
        
        # 使用CrewAI进行完整的面试评估
        try:
            # 转换消息格式为CrewAI需要的格式
            message_history = []
            for msg in messages_data:
                message_history.append({
                    "sender": msg.get("sender_type", "user"),
                    "content": msg["content"],
                    "interviewer_id": msg.get("interviewer_id"),
                    "timestamp": msg["timestamp"]
                })
            
            # 使用CrewAI进行完整面试流程评估
            evaluation_result = await crewai_integration.conduct_interview(
                resume_context=interview.resume_content or "",
                position=interview.position,
                difficulty=interview.difficulty
            )
            
            # 解析评估结果
            if isinstance(evaluation_result, str):
                final_assessment = evaluation_result
                feedback_data = {
                    "technical": "基于CrewAI评估生成",
                    "hr": "基于CrewAI评估生成", 
                    "behavioral": "基于CrewAI评估生成",
                    "overall": evaluation_result
                }
            else:
                final_assessment = evaluation_result.get("final_assessment", "评估完成")
                feedback_data = evaluation_result.get("feedback_by_interviewer", {})
                
        except Exception as e:
            logger.error(f"CrewAI评估失败: {str(e)}")
            final_assessment = f"评估生成失败: {str(e)}"
            feedback_data = {"error": f"评估生成失败: {str(e)}"}
        
        # 整合反馈数据
        result = {
            "interview_id": interview_id,
            "position": interview.position,
            "interview_date": interview.created_at.isoformat(),
            "feedback_by_interviewer": feedback_data,
            "final_assessment": final_assessment
        }
        
        # 更新面试记录的反馈数据
        interview.feedback = json.dumps(result)
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"生成面试反馈失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成面试反馈失败: {str(e)}"
        )
