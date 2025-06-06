"""
评估系统服务
提供详细的面试评估和反馈生成功能
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import statistics
from sqlalchemy.orm import Session

from ..models.schemas import Interview, Message, Feedback, InterviewerFeedback
# 使用新的CrewAI架构，不再需要InterviewerFactory
from .ai.crewai_integration import get_crewai_integration
from ..utils.exceptions import ValidationError, AIServiceError

# 设置日志
logger = logging.getLogger(__name__)

class AssessmentService:
    """
    评估系统服务
    提供全面的面试评估和反馈生成功能
    """
    
    def __init__(self):
        """初始化评估服务"""
        # 评估维度权重配置
        self.assessment_weights = {
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
                'problem_solving': 0.25,
                'communication': 0.25,
                'stress_handling': 0.2
            },
            'product_manager': {
                'product_thinking': 0.3,
                'user_perspective': 0.25,
                'cross_functional': 0.25,
                'business_value': 0.2
            }
        }
        
        # 评分等级定义
        self.score_levels = {
            90: {'level': 'Outstanding', 'description': '优秀', 'recommendation': 'Strong Hire'},
            80: {'level': 'Good', 'description': '良好', 'recommendation': 'Hire'},
            70: {'level': 'Average', 'description': '一般', 'recommendation': 'Borderline'},
            60: {'level': 'Below Average', 'description': '偏低', 'recommendation': 'No Hire'},
            0: {'level': 'Poor', 'description': '较差', 'recommendation': 'Strong No Hire'}
        }
    
    async def generate_comprehensive_assessment(
        self,
        interview_id: int,
        messages: List[Dict[str, Any]],
        resume_data: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        生成全面的面试评估
        
        Args:
            interview_id: 面试ID
            messages: 面试消息历史
            resume_data: 简历解析数据（可选）
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 全面的评估结果
        """
        logger.info(f"开始生成全面评估: 面试ID={interview_id}")
        
        try:
            # 获取面试信息
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise ValidationError(f"面试不存在: ID={interview_id}")
            
            # 分析面试对话
            conversation_analysis = await self._analyze_conversation(messages)
            
            # 获取各面试官的详细评估
            interviewer_assessments = await self._get_interviewer_assessments(messages, interview.position)
            
            # 计算综合评分
            overall_assessment = await self._calculate_overall_assessment(interviewer_assessments)
            
            # 生成技能匹配分析
            skill_analysis = await self._analyze_skill_match(messages, resume_data, interview.position)
            
            # 生成改进建议
            improvement_plan = await self._generate_improvement_plan(interviewer_assessments, skill_analysis)
            
            # 生成面试总结
            interview_summary = await self._generate_interview_summary(
                conversation_analysis, overall_assessment, interview.position
            )
            
            # 构建完整评估结果
            comprehensive_assessment = {
                'interview_id': interview_id,
                'position': interview.position,
                'difficulty': interview.difficulty,
                'assessment_time': datetime.utcnow().isoformat(),
                
                # 总体评估
                'overall_assessment': overall_assessment,
                
                # 对话分析
                'conversation_analysis': conversation_analysis,
                
                # 各面试官评估
                'interviewer_assessments': interviewer_assessments,
                
                # 技能分析
                'skill_analysis': skill_analysis,
                
                # 改进计划
                'improvement_plan': improvement_plan,
                
                # 面试总结
                'interview_summary': interview_summary,
                
                # 推荐决策
                'recommendation': self._get_recommendation(overall_assessment['overall_score'])
            }
            
            # 保存评估结果到数据库
            await self._save_assessment_to_db(comprehensive_assessment, db)
            
            logger.info(f"全面评估生成完成: 面试ID={interview_id}, 总分={overall_assessment['overall_score']}")
            return comprehensive_assessment
            
        except Exception as e:
            logger.error(f"生成全面评估失败: 面试ID={interview_id}, 错误: {str(e)}")
            raise AIServiceError(f"评估生成失败: {str(e)}")
    
    async def _analyze_conversation(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析面试对话"""
        analysis = {
            'total_messages': len(messages),
            'user_messages': 0,
            'interviewer_messages': 0,
            'system_messages': 0,
            'average_response_length': 0,
            'conversation_flow': [],
            'engagement_level': 0,
            'response_quality': 0
        }
        
        user_responses = []
        conversation_flow = []
        
        for msg in messages:
            sender_type = msg.get('sender_type', '')
            content = msg.get('content', '')
            
            if sender_type == 'user':
                analysis['user_messages'] += 1
                user_responses.append(len(content))
                conversation_flow.append('user')
            elif sender_type == 'interviewer':
                analysis['interviewer_messages'] += 1
                conversation_flow.append('interviewer')
            elif sender_type == 'system':
                analysis['system_messages'] += 1
                conversation_flow.append('system')
        
        # 计算平均回复长度
        if user_responses:
            analysis['average_response_length'] = statistics.mean(user_responses)
        
        # 分析对话流程
        analysis['conversation_flow'] = conversation_flow
        
        # 评估参与度（基于回复数量和长度）
        if analysis['user_messages'] > 0:
            engagement_score = min(100, (analysis['user_messages'] * 10) + (analysis['average_response_length'] / 10))
            analysis['engagement_level'] = round(engagement_score)
        
        # 评估回复质量（基于长度和多样性）
        if user_responses:
            length_score = min(50, analysis['average_response_length'] / 4)  # 最多50分
            variety_score = min(50, len(set(user_responses)) * 5)  # 最多50分
            analysis['response_quality'] = round(length_score + variety_score)
        
        return analysis
    
    async def _get_interviewer_assessments(
        self, 
        messages: List[Dict[str, Any]], 
        position: str
    ) -> Dict[str, Any]:
        """获取各面试官的详细评估"""
        assessments = {}
        
        # 获取面试官序列
        # 使用CrewAI获取面试官序列
        crewai_integration = get_crewai_integration()
        interviewer_sequence = crewai_integration.get_available_interviewers()
        
        for interviewer_id in interviewer_sequence:
            try:
                # 获取面试官实例
                # 使用CrewAI进行面试轮次评估
            # interviewer = InterviewerFactory.get_interviewer(interviewer_id)  # 已删除
                
                # 生成评估
                feedback = await interviewer.generate_feedback(messages)
                
                # 处理评估结果
                assessment = await self._process_interviewer_feedback(interviewer_id, feedback)
                assessments[interviewer_id] = assessment
                
            except Exception as e:
                logger.error(f"获取面试官评估失败: {interviewer_id}, 错误: {str(e)}")
                # 使用默认评估
                assessments[interviewer_id] = self._get_default_assessment(interviewer_id)
        
        return assessments
    
    async def _process_interviewer_feedback(
        self, 
        interviewer_id: str, 
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理面试官反馈"""
        assessment = {
            'interviewer_id': interviewer_id,
            'interviewer_name': feedback.get('name', ''),
            'interviewer_role': feedback.get('role', ''),
            'dimensions': {},
            'strengths': feedback.get('strengths', []),
            'improvements': feedback.get('improvements', []),
            'overall_feedback': feedback.get('overall_feedback', ''),
            'weighted_score': 0
        }
        
        # 获取该面试官的评估维度权重
        weights = self.assessment_weights.get(interviewer_id, {})
        
        total_weighted_score = 0
        total_weight = 0
        
        # 处理各个维度的评分
        for dimension, weight in weights.items():
            if dimension in feedback:
                dimension_data = feedback[dimension]
                score = dimension_data.get('score', 0)
                feedback_text = dimension_data.get('feedback', '')
                
                assessment['dimensions'][dimension] = {
                    'score': score,
                    'feedback': feedback_text,
                    'weight': weight,
                    'weighted_score': score * weight
                }
                
                total_weighted_score += score * weight
                total_weight += weight
        
        # 计算加权平均分
        if total_weight > 0:
            assessment['weighted_score'] = round(total_weighted_score / total_weight, 1)
        
        return assessment
    
    async def _calculate_overall_assessment(
        self, 
        interviewer_assessments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算综合评估"""
        # 面试官权重（可配置）
        interviewer_weights = {
            'technical': 0.4,
            'hr': 0.3,
            'behavioral': 0.2,
            'product_manager': 0.1
        }
        
        total_weighted_score = 0
        total_weight = 0
        dimension_scores = {}
        
        # 计算各面试官的加权分数
        for interviewer_id, assessment in interviewer_assessments.items():
            weight = interviewer_weights.get(interviewer_id, 0.1)
            score = assessment.get('weighted_score', 0)
            
            total_weighted_score += score * weight
            total_weight += weight
            
            # 收集各维度分数
            for dimension, dim_data in assessment.get('dimensions', {}).items():
                if dimension not in dimension_scores:
                    dimension_scores[dimension] = []
                dimension_scores[dimension].append(dim_data['score'])
        
        # 计算总体分数
        overall_score = round(total_weighted_score / total_weight, 1) if total_weight > 0 else 0
        
        # 计算各维度平均分
        dimension_averages = {}
        for dimension, scores in dimension_scores.items():
            dimension_averages[dimension] = round(statistics.mean(scores), 1)
        
        # 获取评分等级
        score_level = self._get_score_level(overall_score)
        
        return {
            'overall_score': overall_score,
            'score_level': score_level,
            'dimension_scores': dimension_averages,
            'interviewer_weights': interviewer_weights,
            'assessment_breakdown': {
                interviewer_id: {
                    'score': assessment.get('weighted_score', 0),
                    'weight': interviewer_weights.get(interviewer_id, 0.1),
                    'contribution': round(assessment.get('weighted_score', 0) * interviewer_weights.get(interviewer_id, 0.1), 1)
                }
                for interviewer_id, assessment in interviewer_assessments.items()
            }
        }
    
    async def _analyze_skill_match(
        self, 
        messages: List[Dict[str, Any]], 
        resume_data: Optional[Dict[str, Any]], 
        position: str
    ) -> Dict[str, Any]:
        """分析技能匹配度"""
        skill_analysis = {
            'position_requirements': await self._get_position_requirements(position),
            'demonstrated_skills': await self._extract_demonstrated_skills(messages),
            'resume_skills': resume_data.get('skills', {}) if resume_data else {},
            'skill_gaps': [],
            'skill_strengths': [],
            'match_score': 0
        }
        
        # 分析技能匹配
        requirements = skill_analysis['position_requirements']
        demonstrated = skill_analysis['demonstrated_skills']
        resume_skills = skill_analysis['resume_skills']
        
        # 计算匹配分数
        total_requirements = len(requirements.get('required_skills', []))
        matched_skills = 0
        
        for required_skill in requirements.get('required_skills', []):
            # 检查是否在面试中展示了该技能
            if any(required_skill.lower() in skill.lower() for skill in demonstrated):
                skill_analysis['skill_strengths'].append(required_skill)
                matched_skills += 1
            # 检查是否在简历中提到了该技能
            elif resume_skills and any(
                required_skill.lower() in str(skill_list).lower() 
                for skill_list in resume_skills.values()
            ):
                skill_analysis['skill_strengths'].append(f"{required_skill} (简历中提及)")
                matched_skills += 0.5
            else:
                skill_analysis['skill_gaps'].append(required_skill)
        
        # 计算匹配分数
        if total_requirements > 0:
            skill_analysis['match_score'] = round((matched_skills / total_requirements) * 100, 1)
        
        return skill_analysis
    
    async def _get_position_requirements(self, position: str) -> Dict[str, Any]:
        """获取职位要求（可以从数据库或配置文件获取）"""
        # 这里是示例数据，实际应该从职位数据库获取
        position_requirements = {
            'Python后端工程师': {
                'required_skills': ['Python', 'Django', 'FastAPI', 'SQL', 'Redis', 'Git'],
                'preferred_skills': ['Docker', 'Kubernetes', 'AWS', 'MongoDB'],
                'experience_years': 3
            },
            'AI应用工程师': {
                'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'SQL'],
                'preferred_skills': ['Deep Learning', 'NLP', 'Computer Vision', 'MLOps'],
                'experience_years': 2
            },
            '产品经理': {
                'required_skills': ['产品规划', '用户研究', '数据分析', '项目管理'],
                'preferred_skills': ['原型设计', 'A/B测试', 'SQL', 'Python'],
                'experience_years': 3
            }
        }
        
        return position_requirements.get(position, {
            'required_skills': ['沟通能力', '学习能力', '团队协作'],
            'preferred_skills': [],
            'experience_years': 1
        })
    
    async def _extract_demonstrated_skills(self, messages: List[Dict[str, Any]]) -> List[str]:
        """从面试对话中提取展示的技能"""
        demonstrated_skills = []
        
        # 技能关键词（可以扩展）
        skill_keywords = [
            'python', 'java', 'javascript', 'sql', 'django', 'flask', 'fastapi',
            'react', 'vue', 'angular', 'docker', 'kubernetes', 'aws', 'git',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            '项目管理', '团队协作', '沟通', '领导力', '问题解决'
        ]
        
        # 分析用户回复中的技能关键词
        for msg in messages:
            if msg.get('sender_type') == 'user':
                content = msg.get('content', '').lower()
                for skill in skill_keywords:
                    if skill in content and skill not in demonstrated_skills:
                        demonstrated_skills.append(skill)
        
        return demonstrated_skills
    
    async def _generate_improvement_plan(
        self, 
        interviewer_assessments: Dict[str, Any], 
        skill_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成改进计划"""
        improvement_plan = {
            'priority_areas': [],
            'skill_development': [],
            'learning_resources': [],
            'timeline': '3-6个月',
            'action_items': []
        }
        
        # 收集所有改进建议
        all_improvements = []
        for assessment in interviewer_assessments.values():
            all_improvements.extend(assessment.get('improvements', []))
        
        # 分析技能差距
        skill_gaps = skill_analysis.get('skill_gaps', [])
        
        # 确定优先改进领域
        # 基于评分较低的维度
        low_score_dimensions = []
        for assessment in interviewer_assessments.values():
            for dimension, dim_data in assessment.get('dimensions', {}).items():
                if dim_data['score'] < 70:
                    low_score_dimensions.append(dimension)
        
        improvement_plan['priority_areas'] = list(set(low_score_dimensions))
        
        # 技能发展建议
        improvement_plan['skill_development'] = skill_gaps[:5]  # 前5个技能差距
        
        # 学习资源推荐
        improvement_plan['learning_resources'] = await self._recommend_learning_resources(
            skill_gaps, low_score_dimensions
        )
        
        # 行动项目
        improvement_plan['action_items'] = all_improvements[:10]  # 前10个改进建议
        
        return improvement_plan
    
    async def _recommend_learning_resources(
        self, 
        skill_gaps: List[str], 
        low_score_dimensions: List[str]
    ) -> List[Dict[str, Any]]:
        """推荐学习资源"""
        resources = []
        
        # 技能相关资源
        skill_resources = {
            'python': {'type': '在线课程', 'name': 'Python官方教程', 'url': 'https://docs.python.org/3/tutorial/'},
            'django': {'type': '在线课程', 'name': 'Django官方文档', 'url': 'https://docs.djangoproject.com/'},
            'machine learning': {'type': '在线课程', 'name': 'Coursera机器学习课程', 'url': 'https://www.coursera.org/learn/machine-learning'},
        }
        
        # 软技能资源
        soft_skill_resources = {
            'communication': {'type': '书籍', 'name': '《非暴力沟通》', 'description': '提升沟通技巧'},
            'teamwork': {'type': '在线课程', 'name': '团队协作最佳实践', 'description': '学习团队合作技能'},
            'problem_solving': {'type': '练习平台', 'name': 'LeetCode', 'description': '算法和问题解决能力训练'}
        }
        
        # 添加技能相关资源
        for skill in skill_gaps[:3]:  # 前3个技能差距
            if skill.lower() in skill_resources:
                resources.append(skill_resources[skill.lower()])
        
        # 添加软技能资源
        for dimension in low_score_dimensions[:2]:  # 前2个低分维度
            if dimension in soft_skill_resources:
                resources.append(soft_skill_resources[dimension])
        
        return resources
    
    async def _generate_interview_summary(
        self, 
        conversation_analysis: Dict[str, Any], 
        overall_assessment: Dict[str, Any], 
        position: str
    ) -> Dict[str, Any]:
        """生成面试总结"""
        summary = {
            'position': position,
            'interview_duration_estimate': f"{conversation_analysis['total_messages'] * 2}分钟",
            'participation_level': self._get_participation_level(conversation_analysis['engagement_level']),
            'overall_performance': overall_assessment['score_level']['description'],
            'key_highlights': [],
            'main_concerns': [],
            'recommendation_summary': overall_assessment['score_level']['recommendation']
        }
        
        # 基于分数生成关键亮点和主要关注点
        overall_score = overall_assessment['overall_score']
        
        if overall_score >= 80:
            summary['key_highlights'] = [
                '候选人表现出色，技术能力强',
                '沟通表达清晰，逻辑思维良好',
                '具备良好的职业素养和团队协作能力'
            ]
        elif overall_score >= 70:
            summary['key_highlights'] = [
                '候选人基础扎实，有一定经验',
                '学习能力和适应能力较强'
            ]
            summary['main_concerns'] = [
                '在某些技术领域需要进一步提升',
                '可以加强实际项目经验的积累'
            ]
        else:
            summary['main_concerns'] = [
                '技术基础需要加强',
                '缺乏相关项目经验',
                '沟通表达能力有待提升'
            ]
        
        return summary
    
    def _get_participation_level(self, engagement_level: int) -> str:
        """获取参与度等级"""
        if engagement_level >= 80:
            return '积极参与'
        elif engagement_level >= 60:
            return '正常参与'
        elif engagement_level >= 40:
            return '参与度一般'
        else:
            return '参与度较低'
    
    def _get_score_level(self, score: float) -> Dict[str, str]:
        """获取评分等级"""
        for threshold in sorted(self.score_levels.keys(), reverse=True):
            if score >= threshold:
                return self.score_levels[threshold]
        return self.score_levels[0]
    
    def _get_recommendation(self, overall_score: float) -> Dict[str, Any]:
        """获取推荐决策"""
        score_level = self._get_score_level(overall_score)
        
        return {
            'decision': score_level['recommendation'],
            'confidence': 'High' if overall_score >= 80 or overall_score <= 60 else 'Medium',
            'next_steps': self._get_next_steps(score_level['recommendation']),
            'additional_notes': self._get_additional_notes(overall_score)
        }
    
    def _get_next_steps(self, recommendation: str) -> List[str]:
        """获取下一步建议"""
        next_steps_map = {
            'Strong Hire': [
                '安排与团队负责人面谈',
                '准备offer谈判',
                '进行背景调查'
            ],
            'Hire': [
                '安排最终轮面试',
                '确认薪资期望',
                '了解入职时间'
            ],
            'Borderline': [
                '安排额外技术测试',
                '与其他候选人对比',
                '考虑岗位匹配度'
            ],
            'No Hire': [
                '感谢候选人参与',
                '提供改进建议',
                '保持人才库联系'
            ],
            'Strong No Hire': [
                '礼貌拒绝',
                '提供详细反馈'
            ]
        }
        
        return next_steps_map.get(recommendation, ['进一步评估'])
    
    def _get_additional_notes(self, overall_score: float) -> str:
        """获取附加说明"""
        if overall_score >= 90:
            return '优秀候选人，强烈推荐录用'
        elif overall_score >= 80:
            return '合格候选人，建议录用'
        elif overall_score >= 70:
            return '基本符合要求，需要进一步考虑'
        elif overall_score >= 60:
            return '存在一些不足，不建议录用'
        else:
            return '不符合岗位要求，不推荐录用'
    
    def _get_default_assessment(self, interviewer_id: str) -> Dict[str, Any]:
        """获取默认评估（当面试官评估失败时使用）"""
        return {
            'interviewer_id': interviewer_id,
            'interviewer_name': f'面试官_{interviewer_id}',
            'interviewer_role': f'{interviewer_id}面试官',
            'dimensions': {},
            'strengths': ['基础能力尚可'],
            'improvements': ['需要进一步提升'],
            'overall_feedback': '评估数据不完整，建议重新评估',
            'weighted_score': 60
        }
    
    async def _save_assessment_to_db(
        self, 
        assessment: Dict[str, Any], 
        db: Session
    ) -> None:
        """保存评估结果到数据库"""
        try:
            interview_id = assessment['interview_id']
            
            # 创建或更新Feedback记录
            feedback = db.query(Feedback).filter(Feedback.interview_id == interview_id).first()
            
            if not feedback:
                feedback = Feedback(interview_id=interview_id)
                db.add(feedback)
            
            # 更新反馈数据
            feedback.summary = assessment['interview_summary']['recommendation_summary']
            feedback.overall_score = assessment['overall_assessment']['overall_score']
            feedback.skill_scores = assessment['overall_assessment']['dimension_scores']
            
            # 收集所有优势和改进建议
            all_strengths = []
            all_improvements = []
            
            for interviewer_assessment in assessment['interviewer_assessments'].values():
                all_strengths.extend(interviewer_assessment.get('strengths', []))
                all_improvements.extend(interviewer_assessment.get('improvements', []))
            
            feedback.strengths = list(set(all_strengths))  # 去重
            feedback.improvements = list(set(all_improvements))  # 去重
            
            db.commit()
            db.refresh(feedback)
            
            # 删除旧的面试官反馈
            db.query(InterviewerFeedback).filter(InterviewerFeedback.feedback_id == feedback.id).delete()
            
            # 保存面试官反馈
            for interviewer_id, interviewer_assessment in assessment['interviewer_assessments'].items():
                interviewer_feedback = InterviewerFeedback(
                    feedback_id=feedback.id,
                    interviewer_id=interviewer_id,
                    name=interviewer_assessment.get('interviewer_name', ''),
                    role=interviewer_assessment.get('interviewer_role', ''),
                    content=interviewer_assessment.get('overall_feedback', '')
                )
                db.add(interviewer_feedback)
            
            # 更新面试的总体评分
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if interview:
                interview.overall_score = assessment['overall_assessment']['overall_score']
            
            db.commit()
            
            logger.info(f"评估结果已保存到数据库: 面试ID={interview_id}")
            
        except Exception as e:
            logger.error(f"保存评估结果失败: {str(e)}")
            db.rollback()
            raise


# 全局评估服务实例
assessment_service = AssessmentService() 