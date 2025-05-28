"""
评估报告API端点
提供面试评估报告的生成、查看和导出功能
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...services.assessment_report_generator import assessment_report_generator
from ...utils.exceptions import AssessmentError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessment-report", tags=["评估报告"])


class GenerateReportRequest(BaseModel):
    """生成报告请求模型"""
    interview_id: int = Field(..., description="面试ID")
    candidate_name: str = Field(..., description="候选人姓名")
    position: str = Field(..., description="面试职位")
    additional_data: Optional[Dict[str, Any]] = Field(default=None, description="额外数据")


class ReportResponse(BaseModel):
    """报告响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="报告数据")


@router.post("/generate", response_model=ReportResponse)
async def generate_assessment_report(request: GenerateReportRequest):
    """
    生成面试评估报告
    
    Args:
        request: 生成报告请求
        
    Returns:
        ReportResponse: 报告生成结果
    """
    try:
        logger.info(f"开始生成评估报告: 面试ID={request.interview_id}")
        
        # 生成报告
        report = await assessment_report_generator.generate_interview_report(
            interview_id=request.interview_id,
            candidate_name=request.candidate_name,
            position=request.position,
            additional_data=request.additional_data
        )
        
        # 转换为字典格式
        report_dict = assessment_report_generator.export_report_to_dict(report)
        
        return ReportResponse(
            success=True,
            message="评估报告生成成功",
            data=report_dict
        )
        
    except AssessmentError as e:
        logger.error(f"生成评估报告失败: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"生成评估报告异常: {e}")
        raise HTTPException(status_code=500, detail="报告生成服务暂时不可用")


@router.get("/view/{interview_id}")
async def view_assessment_report(interview_id: int):
    """
    查看面试评估报告
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict: 报告内容
    """
    try:
        logger.info(f"查看评估报告: 面试ID={interview_id}")
        
        # 这里可以从数据库或缓存中获取已生成的报告
        # 目前直接重新生成报告
        report = await assessment_report_generator.generate_interview_report(
            interview_id=interview_id,
            candidate_name="候选人",  # 实际应用中应从数据库获取
            position="面试职位"  # 实际应用中应从数据库获取
        )
        
        report_dict = assessment_report_generator.export_report_to_dict(report)
        
        return {
            "success": True,
            "data": report_dict
        }
        
    except AssessmentError as e:
        logger.error(f"查看评估报告失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"查看评估报告异常: {e}")
        raise HTTPException(status_code=500, detail="获取报告失败")


@router.get("/export/{interview_id}/json")
async def export_report_json(interview_id: int):
    """
    导出评估报告为JSON格式
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Response: JSON文件下载
    """
    try:
        logger.info(f"导出JSON报告: 面试ID={interview_id}")
        
        # 生成报告
        report = await assessment_report_generator.generate_interview_report(
            interview_id=interview_id,
            candidate_name="候选人",
            position="面试职位"
        )
        
        # 导出为JSON
        json_content = await assessment_report_generator.export_report_to_json(report)
        
        # 返回文件下载响应
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=interview_report_{interview_id}.json"
            }
        )
        
    except AssessmentError as e:
        logger.error(f"导出JSON报告失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"导出JSON报告异常: {e}")
        raise HTTPException(status_code=500, detail="导出报告失败")


@router.get("/summary/{interview_id}")
async def get_report_summary(interview_id: int):
    """
    获取评估报告摘要
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict: 报告摘要
    """
    try:
        logger.info(f"获取报告摘要: 面试ID={interview_id}")
        
        # 生成报告
        report = await assessment_report_generator.generate_interview_report(
            interview_id=interview_id,
            candidate_name="候选人",
            position="面试职位"
        )
        
        # 构建摘要
        summary = {
            "interview_id": report.interview_id,
            "candidate_name": report.candidate_name,
            "position": report.position,
            "overall_score": report.overall_assessment.overall_score,
            "performance_level": report.overall_assessment.performance_level,
            "final_recommendation": report.final_recommendation,
            "confidence_score": report.confidence_score,
            "interview_duration": report.overall_assessment.interview_duration,
            "total_messages": report.overall_assessment.total_messages,
            "key_insights_count": len(report.key_insights),
            "improvement_suggestions_count": len(report.improvement_suggestions),
            "dimension_count": len(report.dimension_analyses),
            "report_generated_at": report.report_generated_at.isoformat()
        }
        
        return {
            "success": True,
            "data": summary
        }
        
    except AssessmentError as e:
        logger.error(f"获取报告摘要失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取报告摘要异常: {e}")
        raise HTTPException(status_code=500, detail="获取摘要失败")


@router.get("/dimensions/{interview_id}")
async def get_dimension_analysis(interview_id: int):
    """
    获取维度分析详情
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict: 维度分析数据
    """
    try:
        logger.info(f"获取维度分析: 面试ID={interview_id}")
        
        # 生成报告
        report = await assessment_report_generator.generate_interview_report(
            interview_id=interview_id,
            candidate_name="候选人",
            position="面试职位"
        )
        
        # 构建维度分析数据
        dimension_data = {
            "overall_score": report.overall_assessment.overall_score,
            "dimensions": [],
            "dimension_summary": {
                "highest_score": 0,
                "lowest_score": 100,
                "average_score": 0,
                "score_variance": 0
            }
        }
        
        scores = []
        for analysis in report.dimension_analyses:
            dimension_info = {
                "dimension": analysis.dimension,
                "score": analysis.score,
                "level": analysis.level,
                "trend": analysis.trend,
                "strengths": analysis.strengths,
                "weaknesses": analysis.weaknesses,
                "recommendations": analysis.recommendations,
                "keyword_matches": analysis.keyword_matches
            }
            dimension_data["dimensions"].append(dimension_info)
            scores.append(analysis.score)
        
        # 计算统计信息
        if scores:
            import statistics
            dimension_data["dimension_summary"]["highest_score"] = max(scores)
            dimension_data["dimension_summary"]["lowest_score"] = min(scores)
            dimension_data["dimension_summary"]["average_score"] = statistics.mean(scores)
            if len(scores) > 1:
                dimension_data["dimension_summary"]["score_variance"] = statistics.variance(scores)
        
        return {
            "success": True,
            "data": dimension_data
        }
        
    except AssessmentError as e:
        logger.error(f"获取维度分析失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取维度分析异常: {e}")
        raise HTTPException(status_code=500, detail="获取维度分析失败")


@router.get("/insights/{interview_id}")
async def get_key_insights(interview_id: int):
    """
    获取关键洞察
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict: 关键洞察数据
    """
    try:
        logger.info(f"获取关键洞察: 面试ID={interview_id}")
        
        # 生成报告
        report = await assessment_report_generator.generate_interview_report(
            interview_id=interview_id,
            candidate_name="候选人",
            position="面试职位"
        )
        
        insights_data = {
            "key_insights": report.key_insights,
            "improvement_suggestions": report.improvement_suggestions,
            "final_recommendation": report.final_recommendation,
            "confidence_score": report.confidence_score,
            "trend_analysis": report.overall_assessment.trend_analysis,
            "performance_metrics": {
                "engagement_level": report.overall_assessment.engagement_level,
                "coherence_score": report.overall_assessment.coherence_score,
                "response_quality": report.overall_assessment.response_quality
            }
        }
        
        return {
            "success": True,
            "data": insights_data
        }
        
    except AssessmentError as e:
        logger.error(f"获取关键洞察失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取关键洞察异常: {e}")
        raise HTTPException(status_code=500, detail="获取洞察失败")


@router.get("/health")
async def assessment_report_health():
    """
    评估报告服务健康检查
    
    Returns:
        Dict: 服务状态
    """
    try:
        return {
            "status": "healthy",
            "service": "assessment_report",
            "version": "1.0.0",
            "features": [
                "report_generation",
                "dimension_analysis",
                "insights_extraction",
                "json_export"
            ]
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "assessment_report"
        }


# 添加路由到主应用
def include_assessment_report_routes(app):
    """将评估报告路由添加到主应用"""
    app.include_router(router) 