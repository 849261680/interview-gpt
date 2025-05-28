"""
评估系统测试
测试面试评估和反馈生成功能
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.assessment_service import assessment_service
from src.models.schemas import Interview, Feedback, InterviewerFeedback
from src.utils.exceptions import ValidationError, AIServiceError


class TestAssessmentService:
    """评估系统服务测试"""
    
    @pytest.fixture
    def sample_messages(self):
        """模拟面试消息"""
        return [
            {
                'sender_type': 'interviewer',
                'content': '请介绍一下您的Python开发经验',
                'timestamp': '2023-12-01T10:00:00'
            },
            {
                'sender_type': 'user',
                'content': '我有3年的Python开发经验，主要使用Django框架开发Web应用',
                'timestamp': '2023-12-01T10:01:00'
            },
            {
                'sender_type': 'interviewer',
                'content': '能详细说说您在项目中遇到的技术挑战吗？',
                'timestamp': '2023-12-01T10:02:00'
            },
            {
                'sender_type': 'user',
                'content': '在一个电商项目中，我们遇到了高并发问题，通过使用Redis缓存和数据库优化解决了性能瓶颈',
                'timestamp': '2023-12-01T10:03:00'
            }
        ]
    
    @pytest.fixture
    def sample_resume_data(self):
        """模拟简历数据"""
        return {
            'personal_info': {
                'name': '张三',
                'email': 'zhangsan@example.com',
                'phone': '13800138000'
            },
            'education': [
                {'school': '清华大学', 'degree': '学士', 'year': '2020'}
            ],
            'work_experience': [
                {'company': 'ABC科技', 'position': 'Python工程师', 'duration': '2020-2023'}
            ],
            'skills': {
                'programming_languages': ['Python', 'Java'],
                'frameworks': ['Django', 'Flask'],
                'databases': ['MySQL', 'Redis'],
                'tools': ['Git', 'Docker']
            },
            'summary': {'quality_score': 85}
        }
    
    @pytest.fixture
    def mock_interview(self):
        """模拟面试对象"""
        interview = MagicMock(spec=Interview)
        interview.id = 1
        interview.position = 'Python后端工程师'
        interview.difficulty = 'intermediate'
        interview.resume_path = '/path/to/resume.pdf'
        return interview
    
    @pytest.fixture
    def mock_db_session(self):
        """模拟数据库会话"""
        db = MagicMock()
        return db
    
    @pytest.mark.asyncio
    async def test_analyze_conversation(self, sample_messages):
        """测试对话分析"""
        analysis = await assessment_service._analyze_conversation(sample_messages)
        
        assert analysis['total_messages'] == 4
        assert analysis['user_messages'] == 2
        assert analysis['interviewer_messages'] == 2
        assert analysis['average_response_length'] > 0
        assert analysis['engagement_level'] > 0
        assert analysis['response_quality'] > 0
    
    @pytest.mark.asyncio
    async def test_extract_demonstrated_skills(self, sample_messages):
        """测试提取展示的技能"""
        skills = await assessment_service._extract_demonstrated_skills(sample_messages)
        
        assert 'python' in skills
        assert 'django' in skills
        assert any('redis' in skill.lower() for skill in skills)
    
    @pytest.mark.asyncio
    async def test_analyze_skill_match(self, sample_messages, sample_resume_data):
        """测试技能匹配分析"""
        skill_analysis = await assessment_service._analyze_skill_match(
            messages=sample_messages,
            resume_data=sample_resume_data,
            position='Python后端工程师'
        )
        
        assert 'position_requirements' in skill_analysis
        assert 'demonstrated_skills' in skill_analysis
        assert 'resume_skills' in skill_analysis
        assert 'skill_gaps' in skill_analysis
        assert 'skill_strengths' in skill_analysis
        assert 'match_score' in skill_analysis
        assert 0 <= skill_analysis['match_score'] <= 100
    
    @pytest.mark.asyncio
    async def test_get_position_requirements(self):
        """测试获取职位要求"""
        requirements = await assessment_service._get_position_requirements('Python后端工程师')
        
        assert 'required_skills' in requirements
        assert 'preferred_skills' in requirements
        assert 'experience_years' in requirements
        assert 'Python' in requirements['required_skills']
    
    @pytest.mark.asyncio
    async def test_calculate_overall_assessment(self):
        """测试计算综合评估"""
        interviewer_assessments = {
            'technical': {
                'weighted_score': 85,
                'dimensions': {
                    'technical_knowledge': {'score': 80},
                    'problem_solving': {'score': 90}
                }
            },
            'hr': {
                'weighted_score': 75,
                'dimensions': {
                    'communication': {'score': 75},
                    'professionalism': {'score': 75}
                }
            }
        }
        
        overall = await assessment_service._calculate_overall_assessment(interviewer_assessments)
        
        assert 'overall_score' in overall
        assert 'score_level' in overall
        assert 'dimension_scores' in overall
        assert 'interviewer_weights' in overall
        assert 0 <= overall['overall_score'] <= 100
    
    @pytest.mark.asyncio
    async def test_generate_improvement_plan(self):
        """测试生成改进计划"""
        interviewer_assessments = {
            'technical': {
                'improvements': ['加强算法基础', '提升系统设计能力'],
                'dimensions': {
                    'technical_knowledge': {'score': 60},
                    'problem_solving': {'score': 70}
                }
            }
        }
        
        skill_analysis = {
            'skill_gaps': ['Kubernetes', 'AWS', '微服务架构']
        }
        
        plan = await assessment_service._generate_improvement_plan(
            interviewer_assessments, skill_analysis
        )
        
        assert 'priority_areas' in plan
        assert 'skill_development' in plan
        assert 'learning_resources' in plan
        assert 'timeline' in plan
        assert 'action_items' in plan
    
    @pytest.mark.asyncio
    async def test_generate_interview_summary(self):
        """测试生成面试总结"""
        conversation_analysis = {
            'total_messages': 10,
            'engagement_level': 80
        }
        
        overall_assessment = {
            'overall_score': 85,
            'score_level': {'description': '良好', 'recommendation': 'Hire'}
        }
        
        summary = await assessment_service._generate_interview_summary(
            conversation_analysis, overall_assessment, 'Python后端工程师'
        )
        
        assert 'position' in summary
        assert 'interview_duration_estimate' in summary
        assert 'participation_level' in summary
        assert 'overall_performance' in summary
        assert 'key_highlights' in summary
        assert 'recommendation_summary' in summary
    
    def test_get_score_level(self):
        """测试获取评分等级"""
        # 测试优秀等级
        level_90 = assessment_service._get_score_level(95)
        assert level_90['level'] == 'Outstanding'
        assert level_90['recommendation'] == 'Strong Hire'
        
        # 测试良好等级
        level_80 = assessment_service._get_score_level(85)
        assert level_80['level'] == 'Good'
        assert level_80['recommendation'] == 'Hire'
        
        # 测试一般等级
        level_70 = assessment_service._get_score_level(75)
        assert level_70['level'] == 'Average'
        assert level_70['recommendation'] == 'Borderline'
        
        # 测试偏低等级
        level_60 = assessment_service._get_score_level(65)
        assert level_60['level'] == 'Below Average'
        assert level_60['recommendation'] == 'No Hire'
        
        # 测试较差等级
        level_poor = assessment_service._get_score_level(45)
        assert level_poor['level'] == 'Poor'
        assert level_poor['recommendation'] == 'Strong No Hire'
    
    def test_get_recommendation(self):
        """测试获取推荐决策"""
        # 测试强烈推荐
        rec_high = assessment_service._get_recommendation(95)
        assert rec_high['decision'] == 'Strong Hire'
        assert rec_high['confidence'] == 'High'
        
        # 测试推荐
        rec_good = assessment_service._get_recommendation(85)
        assert rec_good['decision'] == 'Hire'
        assert rec_good['confidence'] == 'High'
        
        # 测试边界情况
        rec_border = assessment_service._get_recommendation(75)
        assert rec_border['decision'] == 'Borderline'
        assert rec_border['confidence'] == 'Medium'
        
        # 测试不推荐
        rec_low = assessment_service._get_recommendation(55)
        assert rec_low['decision'] == 'No Hire'
        assert rec_low['confidence'] == 'High'
    
    def test_get_next_steps(self):
        """测试获取下一步建议"""
        steps_hire = assessment_service._get_next_steps('Strong Hire')
        assert '安排与团队负责人面谈' in steps_hire
        
        steps_no_hire = assessment_service._get_next_steps('No Hire')
        assert '感谢候选人参与' in steps_no_hire
    
    @pytest.mark.asyncio
    async def test_comprehensive_assessment_integration(
        self, 
        sample_messages, 
        sample_resume_data, 
        mock_interview, 
        mock_db_session
    ):
        """测试全面评估集成"""
        # 模拟数据库查询
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_interview
        
        # 模拟面试官评估
        with patch.object(assessment_service, '_get_interviewer_assessments') as mock_assessments:
            mock_assessments.return_value = {
                'technical': {
                    'interviewer_id': 'technical',
                    'interviewer_name': '技术面试官',
                    'weighted_score': 85,
                    'strengths': ['技术基础扎实'],
                    'improvements': ['需要加强算法'],
                    'dimensions': {'technical_knowledge': {'score': 85}}
                }
            }
            
            # 模拟保存到数据库
            with patch.object(assessment_service, '_save_assessment_to_db') as mock_save:
                mock_save.return_value = None
                
                result = await assessment_service.generate_comprehensive_assessment(
                    interview_id=1,
                    messages=sample_messages,
                    resume_data=sample_resume_data,
                    db=mock_db_session
                )
                
                assert result['interview_id'] == 1
                assert result['position'] == 'Python后端工程师'
                assert 'overall_assessment' in result
                assert 'conversation_analysis' in result
                assert 'interviewer_assessments' in result
                assert 'skill_analysis' in result
                assert 'improvement_plan' in result
                assert 'interview_summary' in result
                assert 'recommendation' in result
    
    @pytest.mark.asyncio
    async def test_assessment_with_missing_interview(self, mock_db_session):
        """测试面试不存在的情况"""
        # 模拟面试不存在
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValidationError) as exc_info:
            await assessment_service.generate_comprehensive_assessment(
                interview_id=999,
                messages=[],
                db=mock_db_session
            )
        
        assert "面试不存在" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_recommend_learning_resources(self):
        """测试推荐学习资源"""
        skill_gaps = ['Python', 'Django', 'Machine Learning']
        low_score_dimensions = ['communication', 'problem_solving']
        
        resources = await assessment_service._recommend_learning_resources(
            skill_gaps, low_score_dimensions
        )
        
        assert isinstance(resources, list)
        # 检查是否包含相关资源
        if resources:
            assert any('type' in resource for resource in resources)
            assert any('name' in resource for resource in resources)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 