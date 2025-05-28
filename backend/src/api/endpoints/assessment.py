"""
评估系统API端点
处理面试评估和反馈生成
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from ...db.database import get_db
from ...services.assessment_service import assessment_service
from ...services.interview_service import get_interview_messages_service
from ...services.resume_parser import resume_parser
from ...models.schemas import Interview, Feedback
from ...utils.exceptions import ValidationError, AIServiceError

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/assessment", tags=["评估系统"])


@router.post("/generate/{interview_id}")
async def generate_comprehensive_assessment(
    interview_id: int = Path(..., description="面试ID"),
    include_resume: bool = Query(True, description="是否包含简历分析"),
    db: Session = Depends(get_db)
):
    """
    生成全面的面试评估
    
    Args:
        interview_id: 面试ID
        include_resume: 是否包含简历分析
        db: 数据库会话
        
    Returns:
        全面的评估结果
    """
    logger.info(f"生成全面评估: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail=f"面试不存在: ID={interview_id}")
        
        # 获取面试消息历史
        messages = await get_interview_messages_service(interview_id, db)
        
        # 转换消息格式
        message_list = []
        for msg in messages:
            message_dict = {
                'sender_type': msg.sender_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
            }
            if msg.interviewer_id:
                message_dict['interviewer_id'] = msg.interviewer_id
            message_list.append(message_dict)
        
        # 获取简历数据（如果需要）
        resume_data = None
        if include_resume and interview.resume_path:
            try:
                resume_data = await resume_parser.parse_resume(interview.resume_path)
            except Exception as e:
                logger.warning(f"简历解析失败: {e}")
        
        # 生成全面评估
        assessment = await assessment_service.generate_comprehensive_assessment(
            interview_id=interview_id,
            messages=message_list,
            resume_data=resume_data,
            db=db
        )
        
        response = {
            "success": True,
            "message": "评估生成成功",
            "data": assessment
        }
        
        logger.info(f"评估生成成功: 面试ID={interview_id}, 总分={assessment['overall_assessment']['overall_score']}")
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.warning(f"评估生成验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        logger.error(f"AI服务错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")
    except Exception as e:
        logger.error(f"评估生成异常: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/result/{interview_id}")
async def get_assessment_result(
    interview_id: int = Path(..., description="面试ID"),
    db: Session = Depends(get_db)
):
    """
    获取面试评估结果
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        评估结果
    """
    logger.info(f"获取评估结果: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail=f"面试不存在: ID={interview_id}")
        
        # 获取反馈记录
        feedback = db.query(Feedback).filter(Feedback.interview_id == interview_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="评估结果不存在，请先生成评估")
        
        # 构建评估结果
        result = {
            "interview_id": interview_id,
            "position": interview.position,
            "difficulty": interview.difficulty,
            "overall_score": feedback.overall_score,
            "summary": feedback.summary,
            "skill_scores": feedback.skill_scores,
            "strengths": feedback.strengths,
            "improvements": feedback.improvements,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
            
            # 面试官反馈
            "interviewer_feedbacks": [
                {
                    "interviewer_id": ifb.interviewer_id,
                    "name": ifb.name,
                    "role": ifb.role,
                    "content": ifb.content
                }
                for ifb in feedback.interviewer_feedbacks
            ]
        }
        
        response = {
            "success": True,
            "message": "获取评估结果成功",
            "data": result
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评估结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/summary/{interview_id}")
async def get_assessment_summary(
    interview_id: int = Path(..., description="面试ID"),
    db: Session = Depends(get_db)
):
    """
    获取评估摘要
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        评估摘要
    """
    logger.info(f"获取评估摘要: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail=f"面试不存在: ID={interview_id}")
        
        # 获取反馈记录
        feedback = db.query(Feedback).filter(Feedback.interview_id == interview_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="评估结果不存在")
        
        # 生成评估等级
        score_level = assessment_service._get_score_level(feedback.overall_score)
        recommendation = assessment_service._get_recommendation(feedback.overall_score)
        
        summary = {
            "interview_id": interview_id,
            "position": interview.position,
            "overall_score": feedback.overall_score,
            "score_level": score_level,
            "recommendation": recommendation,
            "key_strengths": feedback.strengths[:3] if feedback.strengths else [],
            "main_improvements": feedback.improvements[:3] if feedback.improvements else [],
            "assessment_date": feedback.created_at.isoformat() if feedback.created_at else None
        }
        
        response = {
            "success": True,
            "message": "获取评估摘要成功",
            "data": summary
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评估摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/analytics/{interview_id}")
async def get_assessment_analytics(
    interview_id: int = Path(..., description="面试ID"),
    db: Session = Depends(get_db)
):
    """
    获取评估分析数据
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        评估分析数据
    """
    logger.info(f"获取评估分析: 面试ID={interview_id}")
    
    try:
        # 验证面试存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail=f"面试不存在: ID={interview_id}")
        
        # 获取反馈记录
        feedback = db.query(Feedback).filter(Feedback.interview_id == interview_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="评估结果不存在")
        
        # 获取面试消息进行分析
        messages = await get_interview_messages_service(interview_id, db)
        message_list = [
            {
                'sender_type': msg.sender_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in messages
        ]
        
        # 分析对话
        conversation_analysis = await assessment_service._analyze_conversation(message_list)
        
        # 构建分析数据
        analytics = {
            "interview_id": interview_id,
            "conversation_analysis": conversation_analysis,
            "skill_breakdown": feedback.skill_scores,
            "score_distribution": await _calculate_score_distribution(feedback.skill_scores),
            "performance_radar": await _generate_performance_radar(feedback.skill_scores),
            "improvement_priority": await _calculate_improvement_priority(
                feedback.skill_scores, feedback.improvements
            )
        }
        
        response = {
            "success": True,
            "message": "获取评估分析成功",
            "data": analytics
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评估分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/compare")
async def compare_assessments(
    interview_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    比较多个面试的评估结果
    
    Args:
        interview_ids: 面试ID列表
        db: 数据库会话
        
    Returns:
        比较结果
    """
    logger.info(f"比较评估结果: {interview_ids}")
    
    try:
        if len(interview_ids) < 2:
            raise HTTPException(status_code=400, detail="至少需要2个面试进行比较")
        
        if len(interview_ids) > 5:
            raise HTTPException(status_code=400, detail="最多支持比较5个面试")
        
        # 获取所有面试的评估数据
        comparisons = []
        
        for interview_id in interview_ids:
            # 验证面试存在
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise HTTPException(status_code=404, detail=f"面试不存在: ID={interview_id}")
            
            # 获取反馈记录
            feedback = db.query(Feedback).filter(Feedback.interview_id == interview_id).first()
            if not feedback:
                raise HTTPException(status_code=404, detail=f"面试{interview_id}的评估结果不存在")
            
            # 构建比较数据
            comparison_data = {
                "interview_id": interview_id,
                "position": interview.position,
                "difficulty": interview.difficulty,
                "overall_score": feedback.overall_score,
                "skill_scores": feedback.skill_scores,
                "strengths_count": len(feedback.strengths) if feedback.strengths else 0,
                "improvements_count": len(feedback.improvements) if feedback.improvements else 0,
                "assessment_date": feedback.created_at.isoformat() if feedback.created_at else None
            }
            
            comparisons.append(comparison_data)
        
        # 生成比较分析
        comparison_analysis = await _generate_comparison_analysis(comparisons)
        
        response = {
            "success": True,
            "message": "评估比较成功",
            "data": {
                "comparisons": comparisons,
                "analysis": comparison_analysis
            }
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"评估比较失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/report/{interview_id}")
async def generate_assessment_report(
    interview_id: int = Path(..., description="面试ID"),
    format: str = Query("json", description="报告格式: json, pdf"),
    db: Session = Depends(get_db)
):
    """
    生成评估报告
    
    Args:
        interview_id: 面试ID
        format: 报告格式
        db: 数据库会话
        
    Returns:
        评估报告
    """
    logger.info(f"生成评估报告: 面试ID={interview_id}, 格式={format}")
    
    try:
        # 验证面试存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail=f"面试不存在: ID={interview_id}")
        
        # 获取完整评估数据
        feedback = db.query(Feedback).filter(Feedback.interview_id == interview_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="评估结果不存在")
        
        # 构建完整报告
        report = {
            "report_info": {
                "interview_id": interview_id,
                "position": interview.position,
                "difficulty": interview.difficulty,
                "generated_at": datetime.utcnow().isoformat(),
                "report_version": "1.0"
            },
            "executive_summary": {
                "overall_score": feedback.overall_score,
                "recommendation": assessment_service._get_recommendation(feedback.overall_score),
                "key_highlights": feedback.strengths[:5] if feedback.strengths else [],
                "main_concerns": feedback.improvements[:5] if feedback.improvements else []
            },
            "detailed_assessment": {
                "skill_scores": feedback.skill_scores,
                "strengths": feedback.strengths,
                "improvements": feedback.improvements,
                "interviewer_feedbacks": [
                    {
                        "interviewer": ifb.name,
                        "role": ifb.role,
                        "feedback": ifb.content
                    }
                    for ifb in feedback.interviewer_feedbacks
                ]
            },
            "recommendations": {
                "hiring_decision": assessment_service._get_recommendation(feedback.overall_score)['decision'],
                "next_steps": assessment_service._get_next_steps(
                    assessment_service._get_recommendation(feedback.overall_score)['decision']
                ),
                "development_areas": feedback.improvements[:3] if feedback.improvements else []
            }
        }
        
        if format.lower() == "pdf":
            # TODO: 实现PDF生成
            raise HTTPException(status_code=501, detail="PDF格式暂未实现")
        
        response = {
            "success": True,
            "message": "评估报告生成成功",
            "data": report
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成评估报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


# 辅助函数

async def _calculate_score_distribution(skill_scores: Dict[str, float]) -> Dict[str, Any]:
    """计算分数分布"""
    if not skill_scores:
        return {}
    
    scores = list(skill_scores.values())
    return {
        "average": round(sum(scores) / len(scores), 1),
        "highest": max(scores),
        "lowest": min(scores),
        "range": max(scores) - min(scores),
        "above_80": len([s for s in scores if s >= 80]),
        "below_60": len([s for s in scores if s < 60])
    }


async def _generate_performance_radar(skill_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """生成性能雷达图数据"""
    radar_data = []
    
    for skill, score in skill_scores.items():
        radar_data.append({
            "skill": skill,
            "score": score,
            "max_score": 100
        })
    
    return radar_data


async def _calculate_improvement_priority(
    skill_scores: Dict[str, float], 
    improvements: List[str]
) -> List[Dict[str, Any]]:
    """计算改进优先级"""
    priority_list = []
    
    # 基于分数确定优先级
    if skill_scores:
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1])
        
        for i, (skill, score) in enumerate(sorted_skills[:3]):  # 前3个最低分
            priority = "High" if i == 0 else "Medium" if i == 1 else "Low"
            priority_list.append({
                "area": skill,
                "current_score": score,
                "priority": priority,
                "improvement_potential": 100 - score
            })
    
    return priority_list


async def _generate_comparison_analysis(comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成比较分析"""
    if not comparisons:
        return {}
    
    # 计算统计数据
    scores = [c['overall_score'] for c in comparisons]
    
    analysis = {
        "statistics": {
            "total_interviews": len(comparisons),
            "average_score": round(sum(scores) / len(scores), 1),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "score_range": max(scores) - min(scores)
        },
        "ranking": sorted(
            [(c['interview_id'], c['overall_score']) for c in comparisons],
            key=lambda x: x[1],
            reverse=True
        ),
        "performance_levels": {
            "excellent": len([s for s in scores if s >= 90]),
            "good": len([s for s in scores if 80 <= s < 90]),
            "average": len([s for s in scores if 70 <= s < 80]),
            "below_average": len([s for s in scores if s < 70])
        }
    }
    
    return analysis 