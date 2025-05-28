"""
反馈服务
负责生成和管理面试评估反馈
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..models.schemas import Feedback, InterviewerFeedback, Interview
from ..schemas.interview import FeedbackCreate
from ..agents.interviewer_factory import InterviewerFactory

# 设置日志
logger = logging.getLogger(__name__)


async def generate_feedback_service(
    interview_id: int,
    messages: List[Dict[str, Any]],
    db: Session
) -> Dict[str, Any]:
    """
    生成面试评估反馈
    
    Args:
        interview_id: 面试ID
        messages: 面试消息历史
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 生成的评估反馈
    """
    logger.info(f"生成面试评估反馈服务: 面试ID={interview_id}")
    
    # 查询面试记录
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise ValueError(f"面试不存在: ID={interview_id}")
    
    # 获取所有面试官类型
    interviewer_sequence = InterviewerFactory.get_interviewer_sequence()
    
    # 从每个面试官获取评估
    interviewer_feedbacks = []
    skill_scores = []
    strengths = []
    improvements = []
    
    # 评分总和和计数（用于计算平均分）
    total_score = 0
    score_count = 0
    
    # 获取每个面试官的评估
    for interviewer_id in interviewer_sequence:
        try:
            # 获取面试官实例
            interviewer = InterviewerFactory.get_interviewer(interviewer_id)
            
            # 生成评估
            feedback = await interviewer.generate_feedback(messages)
            
            # 处理技术面试官评估
            if interviewer_id == "technical":
                tech_scores = [
                    {"name": "技术知识", "score": feedback["technical_knowledge"]["score"], 
                     "feedback": feedback["technical_knowledge"]["feedback"]},
                    {"name": "问题解决", "score": feedback["problem_solving"]["score"], 
                     "feedback": feedback["problem_solving"]["feedback"]},
                    {"name": "代码质量", "score": feedback["code_quality"]["score"], 
                     "feedback": feedback["code_quality"]["feedback"]}
                ]
                skill_scores.extend(tech_scores)
                
                # 更新总分
                total_score += feedback["technical_knowledge"]["score"]
                total_score += feedback["problem_solving"]["score"]
                total_score += feedback["code_quality"]["score"]
                score_count += 3
            
            # 处理HR面试官评估
            elif interviewer_id == "hr":
                hr_scores = [
                    {"name": "沟通表达", "score": feedback["communication"]["score"], 
                     "feedback": feedback["communication"]["feedback"]},
                    {"name": "职业素养", "score": feedback["professionalism"]["score"], 
                     "feedback": feedback["professionalism"]["feedback"]},
                    {"name": "文化匹配", "score": feedback["culture_fit"]["score"], 
                     "feedback": feedback["culture_fit"]["feedback"]},
                    {"name": "职业规划", "score": feedback["career_planning"]["score"], 
                     "feedback": feedback["career_planning"]["feedback"]}
                ]
                skill_scores.extend(hr_scores)
                
                # 更新总分
                total_score += feedback["communication"]["score"]
                total_score += feedback["professionalism"]["score"]
                total_score += feedback["culture_fit"]["score"]
                total_score += feedback["career_planning"]["score"]
                score_count += 4
            
            # 处理行为面试官评估
            elif interviewer_id == "behavioral":
                behavior_scores = [
                    {"name": "团队协作", "score": feedback["teamwork"]["score"], 
                     "feedback": feedback["teamwork"]["feedback"]},
                    {"name": "问题解决方法", "score": feedback["problem_solving"]["score"], 
                     "feedback": feedback["problem_solving"]["feedback"]},
                    {"name": "人际能力", "score": feedback["communication"]["score"], 
                     "feedback": feedback["communication"]["feedback"]},
                    {"name": "压力处理", "score": feedback["stress_handling"]["score"], 
                     "feedback": feedback["stress_handling"]["feedback"]}
                ]
                skill_scores.extend(behavior_scores)
                
                # 更新总分
                total_score += feedback["teamwork"]["score"]
                total_score += feedback["problem_solving"]["score"]
                total_score += feedback["communication"]["score"]
                total_score += feedback["stress_handling"]["score"]
                score_count += 4
            
            # 添加优势和改进建议
            strengths.extend(feedback["strengths"])
            improvements.extend(feedback["improvements"])
            
            # 创建面试官反馈记录
            interviewer_feedbacks.append({
                "interviewer_id": interviewer_id,
                "name": interviewer.name,
                "role": interviewer.role,
                "feedback": feedback["overall_feedback"]
            })
            
        except Exception as e:
            logger.error(f"获取面试官评估失败: {interviewer_id}, 错误: {str(e)}")
    
    # 计算总体评分
    overall_score = round(total_score / score_count) if score_count > 0 else 0
    
    # 生成总体评价
    summary = "候选人在面试中表现出色，展示了扎实的技术基础、良好的沟通能力和团队协作精神。具有清晰的职业规划和积极的学习态度。在技术深度和系统设计方面有进一步提升的空间。整体而言，是一位有潜力的候选人。"
    
    # 创建评估反馈记录
    feedback_db = Feedback(
        interview_id=interview_id,
        summary=summary,
        overall_score=overall_score,
        skill_scores=skill_scores,
        strengths=strengths,
        improvements=improvements,
        created_at=datetime.utcnow()
    )
    
    # 保存到数据库
    db.add(feedback_db)
    db.commit()
    db.refresh(feedback_db)
    
    # 保存面试官反馈
    for feedback_item in interviewer_feedbacks:
        interviewer_feedback = InterviewerFeedback(
            feedback_id=feedback_db.id,
            interviewer_id=feedback_item["interviewer_id"],
            name=feedback_item["name"],
            role=feedback_item["role"],
            content=feedback_item["feedback"]
        )
        db.add(interviewer_feedback)
    
    # 更新面试总体评分
    interview.overall_score = overall_score
    db.commit()
    
    # 返回评估反馈
    return {
        "id": feedback_db.id,
        "interview_id": feedback_db.interview_id,
        "summary": feedback_db.summary,
        "overall_score": feedback_db.overall_score,
        "skill_scores": feedback_db.skill_scores,
        "strengths": feedback_db.strengths,
        "improvements": feedback_db.improvements,
        "interviewer_feedbacks": interviewer_feedbacks,
        "created_at": feedback_db.created_at
    }


async def get_feedback_service(
    interview_id: int,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    获取面试评估反馈
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        Optional[Dict[str, Any]]: 评估反馈数据，不存在则返回None
    """
    logger.info(f"获取面试评估反馈服务: 面试ID={interview_id}")
    
    # 查询评估反馈记录
    feedback = db.query(Feedback).filter(Feedback.interview_id == interview_id).first()
    
    if not feedback:
        return None
    
    # 查询面试官反馈
    interviewer_feedbacks = db.query(InterviewerFeedback)\
        .filter(InterviewerFeedback.feedback_id == feedback.id)\
        .all()
    
    # 转换为字典列表
    interviewer_feedbacks_list = [
        {
            "interviewer_id": item.interviewer_id,
            "name": item.name,
            "role": item.role,
            "feedback": item.content
        }
        for item in interviewer_feedbacks
    ]
    
    # 返回评估反馈
    return {
        "id": feedback.id,
        "interview_id": feedback.interview_id,
        "summary": feedback.summary,
        "overall_score": feedback.overall_score,
        "skill_scores": feedback.skill_scores,
        "strengths": feedback.strengths,
        "improvements": feedback.improvements,
        "interviewer_feedbacks": interviewer_feedbacks_list,
        "created_at": feedback.created_at
    }
