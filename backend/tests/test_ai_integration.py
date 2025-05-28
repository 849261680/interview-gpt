"""
AI集成测试
测试AI服务管理器、CrewAI集成、面试官功能和DEEPSEEK API
"""
import pytest
import asyncio
from typing import Dict, Any, List

from src.services.ai.ai_service_manager import ai_service_manager
from src.services.ai.crewai_integration import crewai_integration
from src.agents.interviewer_factory import InterviewerFactory


class TestAIServiceManager:
    """AI服务管理器测试"""
    
    @pytest.mark.asyncio
    async def test_get_services(self):
        """测试获取可用服务"""
        primary_service = ai_service_manager.get_primary_service()
        available_services = ai_service_manager.get_available_services()
        
        assert primary_service in available_services
        assert "deepseek" in available_services
        assert "mock" in available_services
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试服务健康检查"""
        health_status = await ai_service_manager.health_check()
        
        assert isinstance(health_status, dict)
        assert "deepseek" in health_status
        assert "mock" in health_status
        
        for service, status in health_status.items():
            assert status in ["healthy", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_chat_completion(self):
        """测试聊天完成功能"""
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "你好"}],
            service="deepseek"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_fallback_service(self):
        """测试服务降级"""
        # 测试不存在的服务会降级到默认服务
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "测试"}],
            service="nonexistent"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0


class TestCrewAIIntegration:
    """CrewAI集成测试"""
    
    def test_crewai_availability(self):
        """测试CrewAI可用性检查"""
        is_available = crewai_integration.is_crewai_available()
        assert isinstance(is_available, bool)
    
    def test_get_available_interviewers(self):
        """测试获取可用面试官"""
        interviewers = crewai_integration.get_available_interviewers()
        
        assert isinstance(interviewers, list)
        assert "technical" in interviewers
        assert "hr" in interviewers
        assert "behavioral" in interviewers
        assert "senior" in interviewers
    
    @pytest.mark.asyncio
    async def test_conduct_interview_round(self):
        """测试面试轮次"""
        response = await crewai_integration.conduct_interview_round(
            interviewer_type="technical",
            candidate_response="我有3年Python后端开发经验",
            position="Python后端工程师",
            difficulty="medium"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_generate_final_evaluation(self):
        """测试生成最终评估"""
        test_messages = [
            {"sender_type": "user", "content": "我有3年Python开发经验"},
            {"sender_type": "interviewer", "content": "请介绍一下您的项目经验"}
        ]
        
        evaluation = await crewai_integration.generate_final_evaluation(
            interview_messages=test_messages,
            position="Python后端工程师"
        )
        
        assert isinstance(evaluation, dict)
        assert "summary" in evaluation
        assert "overall_score" in evaluation
        assert "recommendation" in evaluation


class TestInterviewerFactory:
    """面试官工厂测试"""
    
    def test_get_available_types(self):
        """测试获取可用面试官类型"""
        types = InterviewerFactory.get_available_types()
        
        assert isinstance(types, dict)
        assert "technical" in types
        assert "hr" in types
        assert "behavioral" in types
    
    def test_create_interviewer(self):
        """测试创建面试官"""
        # 测试技术面试官
        technical = InterviewerFactory.create_interviewer("technical")
        assert technical is not None
        assert technical.role == "技术面试官"
        assert technical.name == "张工"
        
        # 测试HR面试官
        hr = InterviewerFactory.create_interviewer("hr")
        assert hr is not None
        assert hr.role == "HR面试官"
        assert hr.name == "李萍"
        
        # 测试行为面试官
        behavioral = InterviewerFactory.create_interviewer("behavioral")
        assert behavioral is not None
        assert behavioral.role == "行为面试官"
        assert behavioral.name == "王总"
    
    def test_create_interview_sequence(self):
        """测试创建面试序列"""
        sequence = InterviewerFactory.create_interview_sequence()
        
        assert isinstance(sequence, list)
        assert len(sequence) > 0
        assert all(interviewer_type in ["technical", "hr", "behavioral"] 
                  for interviewer_type in sequence)
    
    def test_invalid_interviewer_type(self):
        """测试无效面试官类型"""
        with pytest.raises(ValueError):
            InterviewerFactory.create_interviewer("invalid_type")


class TestInterviewerFunctionality:
    """面试官功能测试"""
    
    @pytest.mark.asyncio
    async def test_generate_questions(self):
        """测试生成面试问题"""
        technical = InterviewerFactory.create_interviewer("technical")
        
        questions = await technical.generate_questions(
            position="Python后端工程师",
            difficulty="medium"
        )
        
        assert isinstance(questions, list)
        assert len(questions) > 0
        assert all(isinstance(q, str) for q in questions)
    
    @pytest.mark.asyncio
    async def test_generate_response(self):
        """测试生成面试回复"""
        technical = InterviewerFactory.create_interviewer("technical")
        
        test_messages = [
            {"sender_type": "user", "content": "我有3年Python开发经验，熟悉Django和FastAPI"}
        ]
        
        response = await technical.generate_response(
            messages=test_messages,
            position="Python后端工程师",
            difficulty="medium"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_generate_feedback(self):
        """测试生成面试反馈"""
        technical = InterviewerFactory.create_interviewer("technical")
        
        test_messages = [
            {"sender_type": "user", "content": "我有3年Python开发经验"},
            {"sender_type": "interviewer", "content": "请介绍一下您的项目经验"},
            {"sender_type": "user", "content": "我主要负责后端API开发和数据库设计"}
        ]
        
        feedback = await technical.generate_feedback(messages=test_messages)
        
        assert isinstance(feedback, dict)
        assert "technical_knowledge" in feedback or "score" in feedback
    
    @pytest.mark.asyncio
    async def test_all_interviewer_types(self):
        """测试所有面试官类型的基本功能"""
        for interviewer_type in ["technical", "hr", "behavioral"]:
            interviewer = InterviewerFactory.create_interviewer(interviewer_type)
            
            # 测试生成问题
            questions = await interviewer.generate_questions(
                position="测试职位",
                difficulty="medium"
            )
            assert isinstance(questions, list)
            assert len(questions) > 0
            
            # 测试生成回复
            response = await interviewer.generate_response(
                messages=[{"sender_type": "user", "content": "测试消息"}]
            )
            assert isinstance(response, str)
            assert len(response) > 0


class TestDeepSeekAPI:
    """DEEPSEEK API测试"""
    
    @pytest.mark.asyncio
    async def test_deepseek_health_check(self):
        """测试DEEPSEEK健康检查"""
        health_status = await ai_service_manager.health_check()
        
        assert "deepseek" in health_status
        # 注意：如果没有配置API密钥，可能返回unhealthy
        assert health_status["deepseek"] in ["healthy", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_deepseek_chat_completion(self):
        """测试DEEPSEEK聊天完成"""
        try:
            response = await ai_service_manager.chat_completion(
                messages=[{"role": "user", "content": "什么是Python？"}],
                service="deepseek"
            )
            
            assert isinstance(response, str)
            assert len(response) > 0
            assert "Python" in response
        except Exception as e:
            # 如果API密钥未配置，跳过测试
            pytest.skip(f"DEEPSEEK API不可用: {e}")
    
    @pytest.mark.asyncio
    async def test_deepseek_stream_chat(self):
        """测试DEEPSEEK流式聊天"""
        try:
            response = await ai_service_manager.stream_chat_completion(
                messages=[{"role": "user", "content": "简单介绍Python"}],
                service="deepseek"
            )
            
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            # 如果API密钥未配置，跳过测试
            pytest.skip(f"DEEPSEEK流式API不可用: {e}")


class TestIntegrationScenarios:
    """集成场景测试"""
    
    @pytest.mark.asyncio
    async def test_complete_interview_flow(self):
        """测试完整面试流程"""
        # 1. 创建面试官
        technical = InterviewerFactory.create_interviewer("technical")
        
        # 2. 生成面试问题
        questions = await technical.generate_questions(
            position="Python后端工程师",
            difficulty="medium"
        )
        assert len(questions) > 0
        
        # 3. 模拟面试对话
        messages = [
            {"sender_type": "interviewer", "content": questions[0]},
            {"sender_type": "user", "content": "我有3年Python开发经验，熟悉Django框架"}
        ]
        
        # 4. 生成面试官回复
        response = await technical.generate_response(messages)
        assert isinstance(response, str)
        assert len(response) > 0
        
        # 5. 生成面试反馈
        messages.append({"sender_type": "interviewer", "content": response})
        feedback = await technical.generate_feedback(messages)
        assert isinstance(feedback, dict)
    
    @pytest.mark.asyncio
    async def test_multi_interviewer_sequence(self):
        """测试多面试官序列"""
        sequence = InterviewerFactory.create_interview_sequence()
        
        for interviewer_type in sequence:
            interviewer = InterviewerFactory.create_interviewer(interviewer_type)
            
            # 每个面试官都能正常工作
            questions = await interviewer.generate_questions(
                position="测试职位",
                difficulty="medium"
            )
            assert len(questions) > 0
            
            response = await interviewer.generate_response(
                messages=[{"sender_type": "user", "content": "测试回答"}]
            )
            assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的面试官类型
        with pytest.raises(ValueError):
            InterviewerFactory.create_interviewer("invalid")
        
        # 测试空消息列表
        technical = InterviewerFactory.create_interviewer("technical")
        response = await technical.generate_response(messages=[])
        assert isinstance(response, str)  # 应该返回默认回复
        
        # 测试无效的服务名称（应该降级到默认服务）
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "测试"}],
            service="invalid_service"
        )
        assert isinstance(response, str)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 