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
from ...agents.interviewer_factory import InterviewerFactory

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
        
        # 获取各面试官的评估反馈
        interviewer_factory = InterviewerFactory()
        feedback_data = {}
        
        # 技术面试官反馈
        if "technical" in interview_content_by_interviewer:
            technical_interviewer = interviewer_factory.get_interviewer("technical")
            technical_content = "\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                          else f"候选人: {msg['content']}" 
                                          for msg in messages_data if msg.get('interviewer_id') == 'technical' 
                                          or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'technical')])
            feedback_data["technical"] = await technical_interviewer.generate_feedback(technical_content)
        
        # HR面试官反馈
        if "hr" in interview_content_by_interviewer:
            hr_interviewer = interviewer_factory.get_interviewer("hr")
            hr_content = "\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                   else f"候选人: {msg['content']}" 
                                   for msg in messages_data if msg.get('interviewer_id') == 'hr' 
                                   or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'hr')])
            feedback_data["hr"] = await hr_interviewer.generate_feedback(hr_content)
        
        # 产品经理面试官反馈
        if "product_manager" in interview_content_by_interviewer:
            product_interviewer = interviewer_factory.get_interviewer("product_manager")
            product_content = "\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                        else f"候选人: {msg['content']}" 
                                        for msg in messages_data if msg.get('interviewer_id') == 'product_manager' 
                                        or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'product_manager')])
            feedback_data["product_manager"] = await product_interviewer.generate_feedback(product_content)
        
        # 行为面试官反馈
        if "behavioral" in interview_content_by_interviewer:
            behavioral_interviewer = interviewer_factory.get_interviewer("behavioral")
            behavioral_content = "\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                           else f"候选人: {msg['content']}" 
                                           for msg in messages_data if msg.get('interviewer_id') == 'behavioral' 
                                           or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'behavioral')])
            feedback_data["behavioral"] = await behavioral_interviewer.generate_feedback(behavioral_content)
        
        # 总面试官生成最终评估报告
        senior_interviewer = interviewer_factory.get_interviewer("senior")
        final_assessment = await senior_interviewer.generate_final_assessment(
            technical_content="\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                       else f"候选人: {msg['content']}" 
                                       for msg in messages_data if msg.get('interviewer_id') == 'technical' 
                                       or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'technical')]),
            hr_content="\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                else f"候选人: {msg['content']}" 
                                for msg in messages_data if msg.get('interviewer_id') == 'hr' 
                                or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'hr')]),
            product_content="\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                     else f"候选人: {msg['content']}" 
                                     for msg in messages_data if msg.get('interviewer_id') == 'product_manager' 
                                     or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'product_manager')]),
            behavioral_content="\n".join([f"面试官: {msg['content']}" if msg['sender_type'] == 'interviewer' 
                                        else f"候选人: {msg['content']}" 
                                        for msg in messages_data if msg.get('interviewer_id') == 'behavioral' 
                                        or (msg.get('sender_type') == 'user' and messages_data[messages_data.index(msg)-1].get('interviewer_id') == 'behavioral')])
        )
        
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
