"""
实时评估服务
在面试过程中提供实时评分和反馈
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, deque

from ..config.settings import settings
from ..utils.exceptions import AssessmentError
from .ai.ai_service_manager import ai_service_manager

logger = logging.getLogger(__name__)


class RealTimeAssessmentService:
    """
    实时评估服务
    在面试过程中持续评估候选人表现并提供实时反馈
    """
    
    def __init__(self):
        """初始化实时评估服务"""
        self.logger = logging.getLogger(__name__)
        
        # 评估会话存储 {interview_id: session_data}
        self.assessment_sessions = {}
        
        # 评估维度配置
        self.assessment_dimensions = {
            'technical': {
                'technical_knowledge': {'weight': 0.3, 'keywords': ['算法', '数据结构', '设计模式', '架构']},
                'problem_solving': {'weight': 0.25, 'keywords': ['分析', '解决', '思路', '方案']},
                'code_quality': {'weight': 0.25, 'keywords': ['代码', '优化', '性能', '可读性']},
                'system_design': {'weight': 0.2, 'keywords': ['系统', '设计', '扩展', '架构']}
            },
            'hr': {
                'communication': {'weight': 0.3, 'keywords': ['表达', '沟通', '清晰', '逻辑']},
                'professionalism': {'weight': 0.25, 'keywords': ['专业', '态度', '礼貌', '准时']},
                'culture_fit': {'weight': 0.25, 'keywords': ['团队', '文化', '价值观', '合作']},
                'career_planning': {'weight': 0.2, 'keywords': ['规划', '目标', '发展', '学习']}
            },
            'behavioral': {
                'teamwork': {'weight': 0.3, 'keywords': ['团队', '协作', '配合', '支持']},
                'leadership': {'weight': 0.25, 'keywords': ['领导', '带领', '指导', '影响']},
                'adaptability': {'weight': 0.25, 'keywords': ['适应', '变化', '灵活', '调整']},
                'stress_handling': {'weight': 0.2, 'keywords': ['压力', '挑战', '困难', '应对']}
            }
        }
        
        # 评分阈值配置
        self.score_thresholds = {
            'excellent': 90,
            'good': 80,
            'average': 70,
            'below_average': 60,
            'poor': 0
        }
        
        # 实时反馈配置
        self.feedback_config = {
            'min_messages_for_assessment': 3,  # 最少消息数才开始评估
            'assessment_interval': 5,  # 每5条消息进行一次评估
            'feedback_cooldown': 30,  # 反馈冷却时间（秒）
            'max_session_duration': 7200  # 最大会话时长（秒）
        }
    
    async def start_assessment_session(
        self,
        interview_id: int,
        position: str,
        difficulty: str,
        interviewer_type: str = 'technical'
    ) -> Dict[str, Any]:
        """
        开始实时评估会话
        
        Args:
            interview_id: 面试ID
            position: 面试职位
            difficulty: 面试难度
            interviewer_type: 当前面试官类型
            
        Returns:
            Dict[str, Any]: 会话初始化结果
        """
        try:
            self.logger.info(f"开始实时评估会话: 面试ID={interview_id}")
            
            # 初始化会话数据
            session_data = {
                'interview_id': interview_id,
                'position': position,
                'difficulty': difficulty,
                'current_interviewer': interviewer_type,
                'start_time': datetime.now(),
                'last_assessment_time': datetime.now(),
                'last_feedback_time': datetime.now(),
                'message_count': 0,
                'user_messages': [],
                'interviewer_messages': [],
                'real_time_scores': defaultdict(list),
                'dimension_scores': defaultdict(float),
                'overall_score': 0.0,
                'assessment_history': [],
                'feedback_history': [],
                'conversation_metrics': {
                    'response_times': deque(maxlen=10),
                    'response_lengths': deque(maxlen=10),
                    'engagement_level': 0,
                    'coherence_score': 0,
                    'keyword_matches': defaultdict(int)
                }
            }
            
            # 存储会话
            self.assessment_sessions[interview_id] = session_data
            
            self.logger.info(f"实时评估会话初始化完成: 面试ID={interview_id}")
            
            return {
                'session_id': interview_id,
                'status': 'active',
                'start_time': session_data['start_time'].isoformat(),
                'initial_scores': dict(session_data['dimension_scores']),
                'message': '实时评估已开始'
            }
            
        except Exception as e:
            error_msg = f"启动实时评估会话失败: {str(e)}"
            self.logger.error(error_msg)
            raise AssessmentError(error_msg)
    
    async def process_message(
        self,
        interview_id: int,
        message: Dict[str, Any],
        interviewer_type: str = None
    ) -> Dict[str, Any]:
        """
        处理新消息并更新实时评估
        
        Args:
            interview_id: 面试ID
            message: 消息内容
            interviewer_type: 面试官类型（如果有变化）
            
        Returns:
            Dict[str, Any]: 实时评估结果
        """
        try:
            if interview_id not in self.assessment_sessions:
                raise AssessmentError(f"评估会话不存在: {interview_id}")
            
            session = self.assessment_sessions[interview_id]
            
            # 更新面试官类型
            if interviewer_type and interviewer_type != session['current_interviewer']:
                session['current_interviewer'] = interviewer_type
                self.logger.info(f"面试官切换: {interviewer_type}")
            
            # 处理消息
            await self._process_message_content(session, message)
            
            # 检查是否需要进行评估
            should_assess = await self._should_perform_assessment(session)
            
            assessment_result = None
            if should_assess:
                assessment_result = await self._perform_real_time_assessment(session)
            
            # 检查是否需要提供反馈
            feedback_result = None
            should_feedback = await self._should_provide_feedback(session)
            if should_feedback:
                feedback_result = await self._generate_real_time_feedback(session)
            
            # 构建返回结果
            result = {
                'interview_id': interview_id,
                'message_count': session['message_count'],
                'current_scores': dict(session['dimension_scores']),
                'overall_score': session['overall_score'],
                'engagement_level': session['conversation_metrics']['engagement_level'],
                'assessment_performed': assessment_result is not None,
                'feedback_provided': feedback_result is not None
            }
            
            if assessment_result:
                result['assessment'] = assessment_result
            
            if feedback_result:
                result['feedback'] = feedback_result
            
            return result
            
        except Exception as e:
            error_msg = f"处理消息失败: {str(e)}"
            self.logger.error(error_msg)
            raise AssessmentError(error_msg)
    
    async def _process_message_content(
        self,
        session: Dict[str, Any],
        message: Dict[str, Any]
    ) -> None:
        """处理消息内容并更新会话数据"""
        sender_type = message.get('sender_type', '')
        content = message.get('content', '')
        timestamp = datetime.fromisoformat(message.get('timestamp', datetime.now().isoformat()))
        
        session['message_count'] += 1
        
        if sender_type == 'user':
            # 处理用户消息
            session['user_messages'].append({
                'content': content,
                'timestamp': timestamp,
                'length': len(content)
            })
            
            # 更新对话指标
            await self._update_conversation_metrics(session, content, timestamp)
            
            # 分析关键词匹配
            await self._analyze_keywords(session, content)
            
        elif sender_type == 'interviewer':
            # 处理面试官消息
            session['interviewer_messages'].append({
                'content': content,
                'timestamp': timestamp,
                'interviewer_type': session['current_interviewer']
            })
    
    async def _update_conversation_metrics(
        self,
        session: Dict[str, Any],
        content: str,
        timestamp: datetime
    ) -> None:
        """更新对话指标"""
        metrics = session['conversation_metrics']
        
        # 计算响应时间
        if session['interviewer_messages']:
            last_interviewer_msg = session['interviewer_messages'][-1]
            response_time = (timestamp - last_interviewer_msg['timestamp']).total_seconds()
            metrics['response_times'].append(response_time)
        
        # 记录响应长度
        metrics['response_lengths'].append(len(content))
        
        # 计算参与度（基于响应长度和频率）
        if metrics['response_lengths']:
            avg_length = statistics.mean(metrics['response_lengths'])
            length_score = min(100, avg_length / 2)  # 假设200字符为满分
            
            # 响应时间评分（30秒内响应为满分）
            time_score = 100
            if metrics['response_times']:
                avg_time = statistics.mean(metrics['response_times'])
                time_score = max(0, 100 - (avg_time - 30) * 2)  # 超过30秒开始扣分
            
            metrics['engagement_level'] = round((length_score + time_score) / 2)
        
        # 计算连贯性评分（基于内容复杂度）
        coherence_score = await self._calculate_coherence_score(content)
        metrics['coherence_score'] = coherence_score
    
    async def _analyze_keywords(
        self,
        session: Dict[str, Any],
        content: str
    ) -> None:
        """分析关键词匹配"""
        current_interviewer = session['current_interviewer']
        if current_interviewer not in self.assessment_dimensions:
            return
        
        dimensions = self.assessment_dimensions[current_interviewer]
        content_lower = content.lower()
        
        for dimension, config in dimensions.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                if keyword in content_lower:
                    session['conversation_metrics']['keyword_matches'][dimension] += 1
    
    async def _calculate_coherence_score(self, content: str) -> float:
        """计算内容连贯性评分"""
        try:
            # 简单的连贯性评分算法
            sentences = content.split('。')
            if len(sentences) < 2:
                return 70.0  # 单句默认分数
            
            # 基于句子数量和平均长度
            avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences)
            
            # 连贯性评分
            coherence_score = min(100, 50 + avg_sentence_length * 2)
            return round(coherence_score, 1)
            
        except Exception:
            return 70.0  # 默认分数
    
    async def _should_perform_assessment(self, session: Dict[str, Any]) -> bool:
        """判断是否应该进行评估"""
        # 检查消息数量
        if session['message_count'] < self.feedback_config['min_messages_for_assessment']:
            return False
        
        # 检查评估间隔
        if session['message_count'] % self.feedback_config['assessment_interval'] != 0:
            return False
        
        # 检查时间间隔
        time_since_last = (datetime.now() - session['last_assessment_time']).total_seconds()
        if time_since_last < 60:  # 至少间隔1分钟
            return False
        
        return True
    
    async def _perform_real_time_assessment(
        self,
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行实时评估"""
        try:
            current_interviewer = session['current_interviewer']
            
            # 获取最近的用户消息
            recent_messages = session['user_messages'][-5:]  # 最近5条消息
            
            if not recent_messages:
                return None
            
            # 计算各维度评分
            dimension_scores = await self._calculate_dimension_scores(
                session, recent_messages, current_interviewer
            )
            
            # 更新会话评分
            for dimension, score in dimension_scores.items():
                session['real_time_scores'][dimension].append(score)
                # 计算移动平均
                recent_scores = session['real_time_scores'][dimension][-3:]
                session['dimension_scores'][dimension] = statistics.mean(recent_scores)
            
            # 计算总体评分
            overall_score = await self._calculate_overall_score(session, current_interviewer)
            session['overall_score'] = overall_score
            
            # 记录评估历史
            assessment_record = {
                'timestamp': datetime.now(),
                'interviewer_type': current_interviewer,
                'dimension_scores': dict(dimension_scores),
                'overall_score': overall_score,
                'message_count': session['message_count']
            }
            session['assessment_history'].append(assessment_record)
            session['last_assessment_time'] = datetime.now()
            
            self.logger.info(f"实时评估完成: 面试ID={session['interview_id']}, 总分={overall_score}")
            
            return {
                'timestamp': assessment_record['timestamp'].isoformat(),
                'dimension_scores': dimension_scores,
                'overall_score': overall_score,
                'assessment_trend': await self._calculate_assessment_trend(session),
                'performance_level': await self._get_performance_level(overall_score)
            }
            
        except Exception as e:
            self.logger.error(f"实时评估失败: {str(e)}")
            return None
    
    async def _calculate_dimension_scores(
        self,
        session: Dict[str, Any],
        recent_messages: List[Dict[str, Any]],
        interviewer_type: str
    ) -> Dict[str, float]:
        """计算各维度评分"""
        if interviewer_type not in self.assessment_dimensions:
            return {}
        
        dimensions = self.assessment_dimensions[interviewer_type]
        scores = {}
        
        for dimension, config in dimensions.items():
            # 基础评分（基于关键词匹配）
            keyword_score = self._calculate_keyword_score(session, dimension, config)
            
            # 对话质量评分
            quality_score = await self._calculate_quality_score(recent_messages, dimension)
            
            # 参与度评分
            engagement_score = session['conversation_metrics']['engagement_level']
            
            # 综合评分
            final_score = (
                keyword_score * 0.4 +
                quality_score * 0.4 +
                engagement_score * 0.2
            )
            
            scores[dimension] = round(final_score, 1)
        
        return scores
    
    def _calculate_keyword_score(
        self,
        session: Dict[str, Any],
        dimension: str,
        config: Dict[str, Any]
    ) -> float:
        """计算关键词匹配评分"""
        keyword_matches = session['conversation_metrics']['keyword_matches'].get(dimension, 0)
        keywords_count = len(config.get('keywords', []))
        
        if keywords_count == 0:
            return 70.0  # 默认分数
        
        # 基于匹配比例计算分数
        match_ratio = min(1.0, keyword_matches / keywords_count)
        score = 50 + match_ratio * 50  # 50-100分范围
        
        return round(score, 1)
    
    async def _calculate_quality_score(
        self,
        recent_messages: List[Dict[str, Any]],
        dimension: str
    ) -> float:
        """计算回答质量评分"""
        if not recent_messages:
            return 70.0
        
        # 计算平均长度
        avg_length = statistics.mean([msg['length'] for msg in recent_messages])
        
        # 长度评分（假设100-300字符为最佳）
        if 100 <= avg_length <= 300:
            length_score = 100
        elif avg_length < 100:
            length_score = max(50, avg_length * 0.5)
        else:
            length_score = max(70, 100 - (avg_length - 300) * 0.1)
        
        # 这里可以添加更复杂的质量评估逻辑
        # 例如使用AI模型分析回答的相关性和深度
        
        return round(length_score, 1)
    
    async def _calculate_overall_score(
        self,
        session: Dict[str, Any],
        interviewer_type: str
    ) -> float:
        """计算总体评分"""
        if interviewer_type not in self.assessment_dimensions:
            return 70.0
        
        dimensions = self.assessment_dimensions[interviewer_type]
        total_weighted_score = 0
        total_weight = 0
        
        for dimension, config in dimensions.items():
            weight = config['weight']
            score = session['dimension_scores'].get(dimension, 70.0)
            
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 70.0
        
        overall_score = total_weighted_score / total_weight
        return round(overall_score, 1)
    
    async def _calculate_assessment_trend(self, session: Dict[str, Any]) -> str:
        """计算评估趋势"""
        history = session['assessment_history']
        if len(history) < 2:
            return 'stable'
        
        recent_scores = [record['overall_score'] for record in history[-3:]]
        
        if len(recent_scores) >= 2:
            trend = recent_scores[-1] - recent_scores[0]
            if trend > 5:
                return 'improving'
            elif trend < -5:
                return 'declining'
        
        return 'stable'
    
    async def _get_performance_level(self, score: float) -> str:
        """获取表现等级"""
        for level, threshold in self.score_thresholds.items():
            if score >= threshold:
                return level
        return 'poor'
    
    async def _should_provide_feedback(self, session: Dict[str, Any]) -> bool:
        """判断是否应该提供反馈"""
        # 检查冷却时间
        time_since_last = (datetime.now() - session['last_feedback_time']).total_seconds()
        if time_since_last < self.feedback_config['feedback_cooldown']:
            return False
        
        # 检查是否有显著变化
        if len(session['assessment_history']) >= 2:
            recent_trend = await self._calculate_assessment_trend(session)
            if recent_trend in ['improving', 'declining']:
                return True
        
        # 定期反馈
        if session['message_count'] % 10 == 0:  # 每10条消息
            return True
        
        return False
    
    async def _generate_real_time_feedback(
        self,
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成实时反馈"""
        try:
            current_interviewer = session['current_interviewer']
            overall_score = session['overall_score']
            trend = await self._calculate_assessment_trend(session)
            
            # 生成反馈内容
            feedback_content = await self._create_feedback_content(
                session, current_interviewer, overall_score, trend
            )
            
            # 记录反馈历史
            feedback_record = {
                'timestamp': datetime.now(),
                'content': feedback_content,
                'score': overall_score,
                'trend': trend
            }
            session['feedback_history'].append(feedback_record)
            session['last_feedback_time'] = datetime.now()
            
            return {
                'timestamp': feedback_record['timestamp'].isoformat(),
                'content': feedback_content,
                'score': overall_score,
                'trend': trend,
                'type': 'real_time_feedback'
            }
            
        except Exception as e:
            self.logger.error(f"生成实时反馈失败: {str(e)}")
            return None
    
    async def _create_feedback_content(
        self,
        session: Dict[str, Any],
        interviewer_type: str,
        overall_score: float,
        trend: str
    ) -> str:
        """创建反馈内容"""
        # 基于评分和趋势生成反馈
        if overall_score >= 85:
            base_feedback = "表现优秀！继续保持这种状态。"
        elif overall_score >= 75:
            base_feedback = "表现良好，可以进一步提升回答的深度。"
        elif overall_score >= 65:
            base_feedback = "表现一般，建议更加详细地回答问题。"
        else:
            base_feedback = "需要改进，请尝试提供更具体和相关的回答。"
        
        # 添加趋势反馈
        if trend == 'improving':
            trend_feedback = "您的表现正在持续改善，很好！"
        elif trend == 'declining':
            trend_feedback = "注意保持专注，避免表现下滑。"
        else:
            trend_feedback = "保持稳定的表现。"
        
        # 添加具体建议
        dimension_scores = session['dimension_scores']
        if dimension_scores:
            lowest_dimension = min(dimension_scores.items(), key=lambda x: x[1])
            specific_feedback = f"建议重点关注{lowest_dimension[0]}方面的表现。"
        else:
            specific_feedback = ""
        
        return f"{base_feedback} {trend_feedback} {specific_feedback}".strip()
    
    async def get_session_summary(self, interview_id: int) -> Dict[str, Any]:
        """获取会话摘要"""
        if interview_id not in self.assessment_sessions:
            raise AssessmentError(f"评估会话不存在: {interview_id}")
        
        session = self.assessment_sessions[interview_id]
        
        return {
            'interview_id': interview_id,
            'duration': (datetime.now() - session['start_time']).total_seconds(),
            'message_count': session['message_count'],
            'final_scores': dict(session['dimension_scores']),
            'overall_score': session['overall_score'],
            'assessment_count': len(session['assessment_history']),
            'feedback_count': len(session['feedback_history']),
            'engagement_level': session['conversation_metrics']['engagement_level'],
            'performance_trend': await self._calculate_assessment_trend(session)
        }
    
    async def end_assessment_session(self, interview_id: int) -> Dict[str, Any]:
        """结束评估会话"""
        if interview_id not in self.assessment_sessions:
            raise AssessmentError(f"评估会话不存在: {interview_id}")
        
        session = self.assessment_sessions[interview_id]
        summary = await self.get_session_summary(interview_id)
        
        # 清理会话数据
        del self.assessment_sessions[interview_id]
        
        self.logger.info(f"实时评估会话结束: 面试ID={interview_id}")
        
        return {
            'session_ended': True,
            'summary': summary,
            'message': '实时评估会话已结束'
        }
    
    def cleanup_expired_sessions(self) -> None:
        """清理过期的会话"""
        current_time = datetime.now()
        expired_sessions = []
        
        for interview_id, session in self.assessment_sessions.items():
            session_duration = (current_time - session['start_time']).total_seconds()
            if session_duration > self.feedback_config['max_session_duration']:
                expired_sessions.append(interview_id)
        
        for interview_id in expired_sessions:
            del self.assessment_sessions[interview_id]
            self.logger.info(f"清理过期会话: {interview_id}")


# 创建全局实时评估服务实例
real_time_assessment_service = RealTimeAssessmentService() 