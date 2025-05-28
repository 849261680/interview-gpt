"""
评估报告生成服务
生成详细的面试评估报告，包含多维度分析和建议
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass, asdict
import asyncio

from ..config.settings import settings
from ..utils.exceptions import AssessmentError
from .ai.ai_service_manager import ai_service_manager
from .real_time_assessment import real_time_assessment_service

logger = logging.getLogger(__name__)


@dataclass
class DimensionAnalysis:
    """维度分析结果"""
    dimension: str
    score: float
    level: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    keyword_matches: int
    trend: str


@dataclass
class OverallAssessment:
    """总体评估结果"""
    overall_score: float
    performance_level: str
    interview_duration: float
    total_messages: int
    engagement_level: float
    coherence_score: float
    response_quality: float
    trend_analysis: str


@dataclass
class InterviewReport:
    """面试报告"""
    interview_id: int
    candidate_name: str
    position: str
    interviewer_type: str
    start_time: datetime
    end_time: datetime
    overall_assessment: OverallAssessment
    dimension_analyses: List[DimensionAnalysis]
    key_insights: List[str]
    improvement_suggestions: List[str]
    final_recommendation: str
    confidence_score: float
    report_generated_at: datetime


class AssessmentReportGenerator:
    """
    评估报告生成器
    基于实时评估数据生成详细的面试评估报告
    """
    
    def __init__(self):
        """初始化报告生成器"""
        self.logger = logging.getLogger(__name__)
        
        # 评分等级定义
        self.score_levels = {
            'excellent': {'min': 90, 'label': '优秀'},
            'good': {'min': 80, 'label': '良好'},
            'average': {'min': 70, 'label': '一般'},
            'below_average': {'min': 60, 'label': '待提高'},
            'poor': {'min': 0, 'label': '需改进'}
        }
        
        # 维度权重配置
        self.dimension_weights = {
            'technical': {
                'technical_knowledge': 0.3,
                'problem_solving': 0.25,
                'code_quality': 0.25,
                'system_design': 0.2
            },
            'hr': {
                'communication': 0.3,
                'professionalism': 0.25,
                'culture_fit': 0.25,
                'career_planning': 0.2
            },
            'behavioral': {
                'teamwork': 0.3,
                'leadership': 0.25,
                'adaptability': 0.25,
                'stress_handling': 0.2
            }
        }
        
        # 建议模板
        self.recommendation_templates = {
            'technical_knowledge': {
                'low': ['加强基础技术知识学习', '多做技术实践项目', '关注最新技术趋势'],
                'medium': ['深入学习核心技术', '提升技术深度', '扩展技术广度'],
                'high': ['保持技术敏锐度', '分享技术经验', '引领技术创新']
            },
            'problem_solving': {
                'low': ['练习算法和数据结构', '培养逻辑思维', '多做问题分析练习'],
                'medium': ['提升问题分解能力', '加强解决方案设计', '优化思考过程'],
                'high': ['挑战复杂问题', '指导他人解决问题', '创新解决方案']
            },
            'communication': {
                'low': ['提升表达清晰度', '练习逻辑表述', '增强沟通技巧'],
                'medium': ['完善沟通结构', '提升说服力', '加强倾听能力'],
                'high': ['发挥沟通优势', '帮助团队沟通', '成为沟通桥梁']
            }
        }
    
    async def generate_interview_report(
        self,
        interview_id: int,
        candidate_name: str,
        position: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> InterviewReport:
        """
        生成面试评估报告
        
        Args:
            interview_id: 面试ID
            candidate_name: 候选人姓名
            position: 面试职位
            additional_data: 额外数据
            
        Returns:
            InterviewReport: 完整的面试报告
        """
        try:
            self.logger.info(f"开始生成面试报告: 面试ID={interview_id}")
            
            # 获取实时评估数据
            assessment_data = await self._get_assessment_data(interview_id)
            
            if not assessment_data:
                raise AssessmentError(f"无法获取面试评估数据: {interview_id}")
            
            # 生成总体评估
            overall_assessment = await self._generate_overall_assessment(assessment_data)
            
            # 生成维度分析
            dimension_analyses = await self._generate_dimension_analyses(assessment_data)
            
            # 生成关键洞察
            key_insights = await self._generate_key_insights(assessment_data, dimension_analyses)
            
            # 生成改进建议
            improvement_suggestions = await self._generate_improvement_suggestions(dimension_analyses)
            
            # 生成最终推荐
            final_recommendation = await self._generate_final_recommendation(
                overall_assessment, dimension_analyses
            )
            
            # 计算置信度
            confidence_score = await self._calculate_confidence_score(assessment_data)
            
            # 构建报告
            report = InterviewReport(
                interview_id=interview_id,
                candidate_name=candidate_name,
                position=position,
                interviewer_type=assessment_data.get('current_interviewer', 'unknown'),
                start_time=datetime.fromisoformat(assessment_data['start_time']),
                end_time=datetime.now(),
                overall_assessment=overall_assessment,
                dimension_analyses=dimension_analyses,
                key_insights=key_insights,
                improvement_suggestions=improvement_suggestions,
                final_recommendation=final_recommendation,
                confidence_score=confidence_score,
                report_generated_at=datetime.now()
            )
            
            self.logger.info(f"面试报告生成完成: 面试ID={interview_id}")
            
            return report
            
        except Exception as e:
            error_msg = f"生成面试报告失败: {str(e)}"
            self.logger.error(error_msg)
            raise AssessmentError(error_msg)
    
    async def _get_assessment_data(self, interview_id: int) -> Dict[str, Any]:
        """获取评估数据"""
        try:
            # 从实时评估服务获取数据
            if interview_id in real_time_assessment_service.assessment_sessions:
                session = real_time_assessment_service.assessment_sessions[interview_id]
                return {
                    'interview_id': interview_id,
                    'start_time': session['start_time'].isoformat(),
                    'current_interviewer': session['current_interviewer'],
                    'message_count': session['message_count'],
                    'user_messages': session['user_messages'],
                    'interviewer_messages': session['interviewer_messages'],
                    'dimension_scores': dict(session['dimension_scores']),
                    'overall_score': session['overall_score'],
                    'assessment_history': session['assessment_history'],
                    'feedback_history': session['feedback_history'],
                    'conversation_metrics': session['conversation_metrics']
                }
            else:
                # 尝试从数据库或其他存储获取历史数据
                # 这里可以添加数据库查询逻辑
                raise AssessmentError(f"评估会话不存在: {interview_id}")
                
        except Exception as e:
            self.logger.error(f"获取评估数据失败: {e}")
            raise
    
    async def _generate_overall_assessment(self, data: Dict[str, Any]) -> OverallAssessment:
        """生成总体评估"""
        overall_score = data.get('overall_score', 0)
        start_time = datetime.fromisoformat(data['start_time'])
        duration = (datetime.now() - start_time).total_seconds()
        
        # 计算各项指标
        engagement_level = data.get('conversation_metrics', {}).get('engagement_level', 0)
        coherence_score = data.get('conversation_metrics', {}).get('coherence_score', 0)
        
        # 计算响应质量
        response_quality = await self._calculate_response_quality(data)
        
        # 分析趋势
        trend_analysis = await self._analyze_performance_trend(data)
        
        # 确定表现等级
        performance_level = self._get_performance_level(overall_score)
        
        return OverallAssessment(
            overall_score=overall_score,
            performance_level=performance_level,
            interview_duration=duration,
            total_messages=data.get('message_count', 0),
            engagement_level=engagement_level,
            coherence_score=coherence_score,
            response_quality=response_quality,
            trend_analysis=trend_analysis
        )
    
    async def _generate_dimension_analyses(self, data: Dict[str, Any]) -> List[DimensionAnalysis]:
        """生成维度分析"""
        analyses = []
        dimension_scores = data.get('dimension_scores', {})
        conversation_metrics = data.get('conversation_metrics', {})
        keyword_matches = conversation_metrics.get('keyword_matches', {})
        
        for dimension, score in dimension_scores.items():
            # 分析优势和劣势
            strengths, weaknesses = await self._analyze_dimension_performance(
                dimension, score, data
            )
            
            # 生成建议
            recommendations = await self._generate_dimension_recommendations(dimension, score)
            
            # 分析趋势
            trend = await self._analyze_dimension_trend(dimension, data)
            
            analysis = DimensionAnalysis(
                dimension=dimension,
                score=score,
                level=self._get_performance_level(score),
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                keyword_matches=keyword_matches.get(dimension, 0),
                trend=trend
            )
            
            analyses.append(analysis)
        
        return analyses
    
    async def _analyze_dimension_performance(
        self,
        dimension: str,
        score: float,
        data: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """分析维度表现的优势和劣势"""
        strengths = []
        weaknesses = []
        
        # 基于分数判断
        if score >= 80:
            strengths.append(f"{dimension}表现优秀")
            if score >= 90:
                strengths.append("展现了专业水准")
        elif score >= 70:
            strengths.append(f"{dimension}表现良好")
        else:
            weaknesses.append(f"{dimension}需要提升")
            if score < 60:
                weaknesses.append("存在明显不足")
        
        # 基于关键词匹配分析
        keyword_matches = data.get('conversation_metrics', {}).get('keyword_matches', {})
        matches = keyword_matches.get(dimension, 0)
        
        if matches > 3:
            strengths.append("相关知识点覆盖充分")
        elif matches < 1:
            weaknesses.append("相关知识点提及较少")
        
        # 基于消息质量分析
        user_messages = data.get('user_messages', [])
        if user_messages:
            avg_length = statistics.mean([msg['length'] for msg in user_messages])
            if avg_length > 200:
                strengths.append("回答详细充分")
            elif avg_length < 50:
                weaknesses.append("回答过于简短")
        
        return strengths, weaknesses
    
    async def _generate_dimension_recommendations(
        self,
        dimension: str,
        score: float
    ) -> List[str]:
        """生成维度建议"""
        recommendations = []
        
        # 确定分数等级
        if score >= 80:
            level = 'high'
        elif score >= 60:
            level = 'medium'
        else:
            level = 'low'
        
        # 获取模板建议
        if dimension in self.recommendation_templates:
            template_recs = self.recommendation_templates[dimension].get(level, [])
            recommendations.extend(template_recs)
        
        # 添加通用建议
        if score < 70:
            recommendations.append(f"重点关注{dimension}的提升")
        elif score >= 90:
            recommendations.append(f"继续发挥{dimension}的优势")
        
        return recommendations
    
    async def _analyze_dimension_trend(self, dimension: str, data: Dict[str, Any]) -> str:
        """分析维度趋势"""
        assessment_history = data.get('assessment_history', [])
        
        if len(assessment_history) < 2:
            return 'stable'
        
        # 获取该维度的历史分数
        dimension_scores = []
        for record in assessment_history[-5:]:  # 最近5次评估
            scores = record.get('dimension_scores', {})
            if dimension in scores:
                dimension_scores.append(scores[dimension])
        
        if len(dimension_scores) < 2:
            return 'stable'
        
        # 计算趋势
        trend = dimension_scores[-1] - dimension_scores[0]
        if trend > 5:
            return 'improving'
        elif trend < -5:
            return 'declining'
        else:
            return 'stable'
    
    async def _generate_key_insights(
        self,
        data: Dict[str, Any],
        dimension_analyses: List[DimensionAnalysis]
    ) -> List[str]:
        """生成关键洞察"""
        insights = []
        
        # 分析最强和最弱维度
        if dimension_analyses:
            best_dimension = max(dimension_analyses, key=lambda x: x.score)
            worst_dimension = min(dimension_analyses, key=lambda x: x.score)
            
            insights.append(f"最强项：{best_dimension.dimension}（{best_dimension.score:.1f}分）")
            insights.append(f"待提升项：{worst_dimension.dimension}（{worst_dimension.score:.1f}分）")
        
        # 分析参与度
        engagement = data.get('conversation_metrics', {}).get('engagement_level', 0)
        if engagement >= 80:
            insights.append("面试参与度很高，表现积极")
        elif engagement < 60:
            insights.append("面试参与度有待提升")
        
        # 分析响应时间
        response_times = data.get('conversation_metrics', {}).get('response_times', [])
        if response_times:
            avg_response_time = statistics.mean(response_times)
            if avg_response_time < 20:
                insights.append("响应速度快，思维敏捷")
            elif avg_response_time > 60:
                insights.append("思考时间较长，建议提升反应速度")
        
        # 分析消息质量
        user_messages = data.get('user_messages', [])
        if user_messages:
            total_length = sum(msg['length'] for msg in user_messages)
            avg_length = total_length / len(user_messages)
            
            if avg_length > 300:
                insights.append("回答详细，表达充分")
            elif avg_length < 100:
                insights.append("回答较简短，可以更详细地表达")
        
        return insights
    
    async def _generate_improvement_suggestions(
        self,
        dimension_analyses: List[DimensionAnalysis]
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 收集所有建议
        all_recommendations = []
        for analysis in dimension_analyses:
            all_recommendations.extend(analysis.recommendations)
        
        # 去重并排序
        unique_suggestions = list(set(all_recommendations))
        
        # 按重要性排序（分数低的维度优先）
        low_score_dimensions = [a for a in dimension_analyses if a.score < 70]
        
        if low_score_dimensions:
            suggestions.append("优先提升以下方面：")
            for dim in sorted(low_score_dimensions, key=lambda x: x.score):
                suggestions.extend(dim.recommendations[:2])  # 每个维度取前2个建议
        
        # 添加通用建议
        suggestions.extend([
            "多练习面试技巧，提升表达能力",
            "关注行业动态，保持知识更新",
            "积累项目经验，丰富实践案例"
        ])
        
        return suggestions[:10]  # 限制建议数量
    
    async def _generate_final_recommendation(
        self,
        overall_assessment: OverallAssessment,
        dimension_analyses: List[DimensionAnalysis]
    ) -> str:
        """生成最终推荐"""
        overall_score = overall_assessment.overall_score
        
        # 基于总分给出推荐
        if overall_score >= 85:
            recommendation = "强烈推荐录用"
            reason = "各方面表现优秀，符合岗位要求"
        elif overall_score >= 75:
            recommendation = "推荐录用"
            reason = "整体表现良好，具备岗位胜任能力"
        elif overall_score >= 65:
            recommendation = "谨慎考虑"
            reason = "表现一般，需要进一步评估或培训"
        else:
            recommendation = "不推荐录用"
            reason = "表现不足，不符合当前岗位要求"
        
        # 考虑维度平衡性
        if dimension_analyses:
            scores = [a.score for a in dimension_analyses]
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            
            if score_variance > 400:  # 分数差异较大
                reason += "，但各维度表现不够均衡"
        
        return f"{recommendation}：{reason}"
    
    async def _calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """计算置信度分数"""
        confidence_factors = []
        
        # 基于消息数量
        message_count = data.get('message_count', 0)
        if message_count >= 20:
            confidence_factors.append(0.9)
        elif message_count >= 10:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # 基于面试时长
        start_time = datetime.fromisoformat(data['start_time'])
        duration = (datetime.now() - start_time).total_seconds()
        if duration >= 1800:  # 30分钟
            confidence_factors.append(0.9)
        elif duration >= 900:  # 15分钟
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # 基于评估次数
        assessment_count = len(data.get('assessment_history', []))
        if assessment_count >= 5:
            confidence_factors.append(0.9)
        elif assessment_count >= 3:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # 计算平均置信度
        return statistics.mean(confidence_factors) if confidence_factors else 0.5
    
    async def _calculate_response_quality(self, data: Dict[str, Any]) -> float:
        """计算响应质量"""
        user_messages = data.get('user_messages', [])
        
        if not user_messages:
            return 0.0
        
        quality_scores = []
        
        for message in user_messages:
            length = message['length']
            
            # 基于长度评分
            if 100 <= length <= 500:
                length_score = 100
            elif length < 100:
                length_score = max(50, length * 0.5)
            else:
                length_score = max(70, 100 - (length - 500) * 0.1)
            
            quality_scores.append(length_score)
        
        return statistics.mean(quality_scores)
    
    async def _analyze_performance_trend(self, data: Dict[str, Any]) -> str:
        """分析表现趋势"""
        assessment_history = data.get('assessment_history', [])
        
        if len(assessment_history) < 3:
            return "数据不足，无法分析趋势"
        
        # 获取最近几次的总分
        recent_scores = [record['overall_score'] for record in assessment_history[-5:]]
        
        # 计算趋势
        if len(recent_scores) >= 3:
            early_avg = statistics.mean(recent_scores[:2])
            late_avg = statistics.mean(recent_scores[-2:])
            
            trend = late_avg - early_avg
            
            if trend > 10:
                return "表现持续改善，适应能力强"
            elif trend > 5:
                return "表现稳步提升"
            elif trend < -10:
                return "表现有所下滑，可能存在疲劳"
            elif trend < -5:
                return "表现略有波动"
            else:
                return "表现稳定"
        
        return "表现基本稳定"
    
    def _get_performance_level(self, score: float) -> str:
        """获取表现等级"""
        for level, config in self.score_levels.items():
            if score >= config['min']:
                return config['label']
        return '需改进'
    
    def export_report_to_dict(self, report: InterviewReport) -> Dict[str, Any]:
        """将报告导出为字典格式"""
        return {
            'interview_id': report.interview_id,
            'candidate_name': report.candidate_name,
            'position': report.position,
            'interviewer_type': report.interviewer_type,
            'start_time': report.start_time.isoformat(),
            'end_time': report.end_time.isoformat(),
            'overall_assessment': asdict(report.overall_assessment),
            'dimension_analyses': [asdict(analysis) for analysis in report.dimension_analyses],
            'key_insights': report.key_insights,
            'improvement_suggestions': report.improvement_suggestions,
            'final_recommendation': report.final_recommendation,
            'confidence_score': report.confidence_score,
            'report_generated_at': report.report_generated_at.isoformat()
        }
    
    async def export_report_to_json(self, report: InterviewReport) -> str:
        """将报告导出为JSON格式"""
        report_dict = self.export_report_to_dict(report)
        return json.dumps(report_dict, ensure_ascii=False, indent=2)


# 创建全局报告生成器实例
assessment_report_generator = AssessmentReportGenerator() 