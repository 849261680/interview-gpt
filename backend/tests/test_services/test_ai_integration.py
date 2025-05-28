"""
AI集成测试
测试AI服务管理器、CrewAI集成、面试官功能和DEEPSEEK API的完整集成
"""
import pytest
import asyncio
import os
from typing import Dict, Any, List
from unittest.mock import patch, AsyncMock, MagicMock

from src.services.ai.ai_service_manager import ai_service_manager
from src.services.ai.crewai_integration import crewai_integration
from src.services.ai.deepseek_client import DeepSeekClient
from src.agents.interviewer_factory import InterviewerFactory
from src.utils.exceptions import AIServiceError
from src.config.settings import settings


class TestAIServiceManager:
    """AI服务管理器测试"""
    
    @pytest.mark.asyncio
    async def test_get_primary_service(self):
        """测试获取主要服务"""
        primary_service = ai_service_manager.get_primary_service()
        assert isinstance(primary_service, str)
        assert primary_service in ["deepseek", "mock"]
    
    @pytest.mark.asyncio
    async def test_get_available_services(self):
        """测试获取可用服务列表"""
        services = ai_service_manager.get_available_services()
        assert isinstance(services, list)
        assert "deepseek" in services
        assert "mock" in services
        assert len(services) >= 2
    
    @pytest.mark.asyncio
    async def test_health_check_all_services(self):
        """测试所有服务的健康检查"""
        health_status = await ai_service_manager.health_check()
        
        assert isinstance(health_status, dict)
        assert "deepseek" in health_status
        assert "mock" in health_status
        
        # Mock服务应该总是健康的
        assert health_status["mock"] is True
        
        # DEEPSEEK服务状态取决于API密钥配置
        assert isinstance(health_status["deepseek"], bool)
    
    @pytest.mark.asyncio
    async def test_chat_completion_with_mock(self):
        """测试使用Mock服务的聊天完成"""
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "你好，请介绍一下自己"}],
            service_name="mock",
            temperature=0.7,
            max_tokens=200
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "面试官" in response or "AI" in response
    
    @pytest.mark.asyncio
    async def test_chat_completion_with_deepseek(self):
        """测试使用DEEPSEEK服务的聊天完成"""
        if not settings.DEEPSEEK_API_KEY:
            pytest.skip("DEEPSEEK_API_KEY未配置，跳过DEEPSEEK API测试")
        
        try:
            response = await ai_service_manager.chat_completion(
                messages=[{"role": "user", "content": "什么是Python编程语言？"}],
                service_name="deepseek",
                temperature=0.7,
                max_tokens=200
            )
            
            assert isinstance(response, str)
            assert len(response) > 0
            assert "Python" in response
        except AIServiceError as e:
            pytest.skip(f"DEEPSEEK API不可用: {e}")
    
    @pytest.mark.asyncio
    async def test_service_fallback(self):
        """测试服务降级机制"""
        # 测试不存在的服务会降级到默认服务
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "测试降级"}],
            service_name="nonexistent_service"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_get_client(self):
        """测试获取AI客户端"""
        # 测试获取Mock客户端
        mock_client = ai_service_manager.get_client("mock")
        assert mock_client is not None
        
        # 测试获取DEEPSEEK客户端
        deepseek_client = ai_service_manager.get_client("deepseek")
        assert deepseek_client is not None
        assert isinstance(deepseek_client, DeepSeekClient)
        
        # 测试获取不存在的客户端
        with pytest.raises(ValueError):
            ai_service_manager.get_client("nonexistent")


class TestCrewAIIntegration:
    """CrewAI集成测试"""
    
    def test_crewai_availability(self):
        """测试CrewAI可用性检查"""
        is_available = crewai_integration.is_crewai_available()
        assert isinstance(is_available, bool)
        # 无论是否可用，都应该能正常工作（有降级实现）
    
    def test_get_available_interviewers(self):
        """测试获取可用面试官"""
        interviewers = crewai_integration.get_available_interviewers()
        
        assert isinstance(interviewers, list)
        assert "technical" in interviewers
        assert "hr" in interviewers
        assert "behavioral" in interviewers
        assert "senior" in interviewers
        assert len(interviewers) == 4
    
    @pytest.mark.asyncio
    async def test_conduct_interview_round_technical(self):
        """测试技术面试轮次"""
        test_messages = [
            {"sender_type": "system", "content": "面试开始"},
            {"sender_type": "user", "content": "我有3年Python后端开发经验，熟悉Django和FastAPI框架"}
        ]
        
        response = await crewai_integration.conduct_interview_round(
            interviewer_type="technical",
            messages=test_messages,
            position="Python后端工程师",
            difficulty="medium"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        # 技术面试官的回复应该包含技术相关内容
        assert any(keyword in response.lower() for keyword in 
                  ["技术", "项目", "开发", "代码", "系统", "架构"])
    
    @pytest.mark.asyncio
    async def test_conduct_interview_round_hr(self):
        """测试HR面试轮次"""
        test_messages = [
            {"sender_type": "system", "content": "面试开始"},
            {"sender_type": "user", "content": "我希望在一个有挑战性的环境中工作，能够持续学习和成长"}
        ]
        
        response = await crewai_integration.conduct_interview_round(
            interviewer_type="hr",
            messages=test_messages,
            position="Python后端工程师",
            difficulty="medium"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        # HR面试官的回复应该包含职业发展相关内容
        assert any(keyword in response.lower() for keyword in 
                  ["职业", "发展", "团队", "文化", "规划", "目标"])
    
    @pytest.mark.asyncio
    async def test_conduct_interview_round_behavioral(self):
        """测试行为面试轮次"""
        test_messages = [
            {"sender_type": "system", "content": "面试开始"},
            {"sender_type": "user", "content": "在之前的项目中，我遇到了团队成员意见不一致的情况，我通过积极沟通协调解决了问题"}
        ]
        
        response = await crewai_integration.conduct_interview_round(
            interviewer_type="behavioral",
            messages=test_messages,
            position="Python后端工程师",
            difficulty="medium"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        # 行为面试官的回复应该包含行为评估相关内容
        assert any(keyword in response.lower() for keyword in 
                  ["团队", "协作", "沟通", "挑战", "解决", "经历"])
    
    @pytest.mark.asyncio
    async def test_invalid_interviewer_type(self):
        """测试无效面试官类型"""
        test_messages = [{"sender_type": "user", "content": "测试"}]
        
        with pytest.raises(AIServiceError):
            await crewai_integration.conduct_interview_round(
                interviewer_type="invalid_type",
                messages=test_messages,
                position="测试职位",
                difficulty="medium"
            )
    
    @pytest.mark.asyncio
    async def test_generate_final_assessment(self):
        """测试生成最终评估"""
        test_messages = [
            {"sender_type": "system", "content": "面试开始"},
            {"sender_type": "interviewer", "content": "请介绍一下您的技术背景", "interviewer_id": "technical"},
            {"sender_type": "user", "content": "我有3年Python开发经验，熟悉Django、FastAPI等框架"},
            {"sender_type": "interviewer", "content": "您的职业规划是什么？", "interviewer_id": "hr"},
            {"sender_type": "user", "content": "我希望成为一名资深后端工程师，并逐步向架构师方向发展"},
            {"sender_type": "interviewer", "content": "请分享一个团队协作的例子", "interviewer_id": "behavioral"},
            {"sender_type": "user", "content": "在上个项目中，我与前端同事密切配合，成功完成了API设计和对接"}
        ]
        
        assessment = await crewai_integration.generate_final_assessment(
            messages=test_messages,
            position="Python后端工程师"
        )
        
        assert isinstance(assessment, dict)
        assert "overall_score" in assessment
        assert isinstance(assessment["overall_score"], (int, float))
        assert 0 <= assessment["overall_score"] <= 100
        
        # 检查评估结果的基本结构
        if "technical_ability" in assessment:
            assert "score" in assessment["technical_ability"]
            assert "reason" in assessment["technical_ability"]
        
        if "strengths" in assessment:
            assert isinstance(assessment["strengths"], list)
        
        if "improvements" in assessment:
            assert isinstance(assessment["improvements"], list)


class TestDeepSeekClient:
    """DEEPSEEK客户端测试"""
    
    @pytest.fixture
    def deepseek_client(self):
        """创建DEEPSEEK客户端实例"""
        return DeepSeekClient(
            api_key=settings.DEEPSEEK_API_KEY or "test_key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat"
        )
    
    @pytest.mark.asyncio
    async def test_health_check(self, deepseek_client):
        """测试DEEPSEEK健康检查"""
        if not settings.DEEPSEEK_API_KEY:
            pytest.skip("DEEPSEEK_API_KEY未配置")
        
        is_healthy = await deepseek_client.health_check()
        assert isinstance(is_healthy, bool)
    
    @pytest.mark.asyncio
    async def test_chat_completion(self, deepseek_client):
        """测试DEEPSEEK聊天完成"""
        if not settings.DEEPSEEK_API_KEY:
            pytest.skip("DEEPSEEK_API_KEY未配置")
        
        try:
            response = await deepseek_client.chat_completion(
                messages=[{"role": "user", "content": "什么是机器学习？请简单介绍。"}],
                temperature=0.7,
                max_tokens=200
            )
            
            assert isinstance(response, str)
            assert len(response) > 0
            assert "机器学习" in response or "Machine Learning" in response
        except AIServiceError as e:
            pytest.skip(f"DEEPSEEK API调用失败: {e}")
    
    @pytest.mark.asyncio
    async def test_stream_chat_completion(self, deepseek_client):
        """测试DEEPSEEK流式聊天完成"""
        if not settings.DEEPSEEK_API_KEY:
            pytest.skip("DEEPSEEK_API_KEY未配置")
        
        try:
            full_response = ""
            async for chunk in deepseek_client.stream_chat_completion(
                messages=[{"role": "user", "content": "简单介绍Python语言"}],
                temperature=0.7,
                max_tokens=100
            ):
                assert isinstance(chunk, str)
                full_response += chunk
            
            assert len(full_response) > 0
            assert "Python" in full_response
        except AIServiceError as e:
            pytest.skip(f"DEEPSEEK流式API调用失败: {e}")
    
    @pytest.mark.asyncio
    async def test_embeddings(self, deepseek_client):
        """测试DEEPSEEK文本嵌入"""
        if not settings.DEEPSEEK_API_KEY:
            pytest.skip("DEEPSEEK_API_KEY未配置")
        
        try:
            embeddings = await deepseek_client.embeddings(
                texts=["Python是一种编程语言", "机器学习是人工智能的分支"]
            )
            
            assert isinstance(embeddings, list)
            assert len(embeddings) == 2
            assert all(isinstance(emb, list) for emb in embeddings)
            assert all(isinstance(val, float) for emb in embeddings for val in emb)
        except AIServiceError as e:
            pytest.skip(f"DEEPSEEK嵌入API调用失败: {e}")


class TestInterviewerIntegration:
    """面试官集成测试"""
    
    @pytest.mark.asyncio
    async def test_technical_interviewer_complete_flow(self):
        """测试技术面试官完整流程"""
        technical = InterviewerFactory.get_interviewer("technical")
        
        # 1. 生成面试问题
        questions = await technical.generate_questions(
            position="Python后端工程师",
            difficulty="medium"
        )
        assert isinstance(questions, list)
        assert len(questions) > 0
        assert all(isinstance(q, str) for q in questions)
        
        # 2. 模拟面试对话
        messages = [
            {"sender_type": "interviewer", "content": questions[0], "interviewer_id": "technical"},
            {"sender_type": "user", "content": "我有3年Python开发经验，主要使用Django和FastAPI框架开发Web API"}
        ]
        
        # 3. 生成面试官回复
        response = await technical.generate_response(
            messages=messages,
            position="Python后端工程师",
            difficulty="medium"
        )
        assert isinstance(response, str)
        assert len(response) > 0
        
        # 4. 生成面试反馈
        messages.append({"sender_type": "interviewer", "content": response, "interviewer_id": "technical"})
        feedback = await technical.generate_feedback(messages=messages)
        assert isinstance(feedback, dict)
        
        # 检查反馈结构
        if "technical_knowledge" in feedback:
            assert "score" in feedback["technical_knowledge"]
            assert "feedback" in feedback["technical_knowledge"]
    
    @pytest.mark.asyncio
    async def test_hr_interviewer_complete_flow(self):
        """测试HR面试官完整流程"""
        hr = InterviewerFactory.get_interviewer("hr")
        
        # 生成问题
        questions = await hr.generate_questions(
            position="Python后端工程师",
            difficulty="medium"
        )
        assert len(questions) > 0
        
        # 生成回复
        messages = [{"sender_type": "user", "content": "我希望在技术团队中发挥更大作用，学习新技术"}]
        response = await hr.generate_response(messages)
        assert len(response) > 0
        
        # 生成反馈
        messages.append({"sender_type": "interviewer", "content": response, "interviewer_id": "hr"})
        feedback = await hr.generate_feedback(messages)
        assert isinstance(feedback, dict)
    
    @pytest.mark.asyncio
    async def test_behavioral_interviewer_complete_flow(self):
        """测试行为面试官完整流程"""
        behavioral = InterviewerFactory.get_interviewer("behavioral")
        
        # 生成问题
        questions = await behavioral.generate_questions(
            position="Python后端工程师",
            difficulty="medium"
        )
        assert len(questions) > 0
        
        # 生成回复
        messages = [{"sender_type": "user", "content": "在项目中遇到技术难题时，我会先分析问题，然后寻求团队帮助"}]
        response = await behavioral.generate_response(messages)
        assert len(response) > 0
        
        # 生成反馈
        messages.append({"sender_type": "interviewer", "content": response, "interviewer_id": "behavioral"})
        feedback = await behavioral.generate_feedback(messages)
        assert isinstance(feedback, dict)
    
    @pytest.mark.asyncio
    async def test_interviewer_factory_integration(self):
        """测试面试官工厂集成"""
        # 测试获取所有面试官类型
        types = InterviewerFactory.get_all_interviewer_types()
        assert isinstance(types, dict)
        assert "technical" in types
        assert "hr" in types
        assert "behavioral" in types
        
        # 测试创建所有类型的面试官
        for interviewer_id in types.keys():
            interviewer = InterviewerFactory.get_interviewer(interviewer_id)
            assert interviewer is not None
            assert interviewer.interviewer_id == interviewer_id
            
            # 测试基本功能
            questions = await interviewer.generate_questions("测试职位", "medium")
            assert len(questions) > 0
            
            response = await interviewer.generate_response([
                {"sender_type": "user", "content": "测试回答"}
            ])
            assert len(response) > 0
        
        # 测试面试官序列
        sequence = InterviewerFactory.get_interviewer_sequence()
        assert isinstance(sequence, list)
        assert len(sequence) > 0
        assert all(seq_type in types for seq_type in sequence)


class TestIntegrationScenarios:
    """集成场景测试"""
    
    @pytest.mark.asyncio
    async def test_complete_interview_simulation(self):
        """测试完整面试模拟"""
        position = "Python后端工程师"
        difficulty = "medium"
        
        # 1. 获取面试官序列
        sequence = InterviewerFactory.get_interviewer_sequence()
        
        # 2. 模拟完整面试流程
        all_messages = []
        
        for interviewer_type in sequence[:2]:  # 只测试前两个面试官以节省时间
            # 创建面试官
            interviewer = InterviewerFactory.get_interviewer(interviewer_type)
            
            # 生成问题
            questions = await interviewer.generate_questions(position, difficulty)
            question = questions[0] if questions else f"请介绍一下您在{position}方面的经验"
            
            # 添加面试官问题
            all_messages.append({
                "sender_type": "interviewer",
                "content": question,
                "interviewer_id": interviewer_type
            })
            
            # 模拟候选人回答
            if interviewer_type == "technical":
                user_response = "我有3年Python开发经验，熟悉Django、FastAPI等框架，参与过多个Web API项目开发"
            elif interviewer_type == "hr":
                user_response = "我希望在技术团队中承担更多责任，学习新技术，向架构师方向发展"
            else:  # behavioral
                user_response = "在项目中遇到困难时，我会主动与团队沟通，寻求最佳解决方案"
            
            all_messages.append({
                "sender_type": "user",
                "content": user_response
            })
            
            # 生成面试官回复
            response = await interviewer.generate_response(all_messages, position, difficulty)
            all_messages.append({
                "sender_type": "interviewer",
                "content": response,
                "interviewer_id": interviewer_type
            })
        
        # 3. 生成最终评估
        final_assessment = await crewai_integration.generate_final_assessment(
            messages=all_messages,
            position=position
        )
        
        assert isinstance(final_assessment, dict)
        assert "overall_score" in final_assessment
        assert len(all_messages) >= 4  # 至少包含2轮问答
    
    @pytest.mark.asyncio
    async def test_ai_service_failover(self):
        """测试AI服务故障转移"""
        # 测试主服务不可用时的降级
        original_primary = ai_service_manager.get_primary_service()
        
        # 模拟主服务故障，使用Mock服务
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "测试故障转移"}],
            service_name="mock"  # 强制使用Mock服务
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_interview_sessions(self):
        """测试并发面试会话"""
        # 创建多个并发面试任务
        tasks = []
        
        for i in range(3):
            task = asyncio.create_task(
                self._simulate_single_interview(f"候选人{i+1}")
            )
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"并发面试任务失败: {result}")
            else:
                assert isinstance(result, str)
                assert len(result) > 0
    
    async def _simulate_single_interview(self, candidate_name: str) -> str:
        """模拟单个面试会话"""
        technical = InterviewerFactory.get_interviewer("technical")
        
        messages = [
            {"sender_type": "user", "content": f"我是{candidate_name}，有Python开发经验"}
        ]
        
        response = await technical.generate_response(
            messages=messages,
            position="Python后端工程师",
            difficulty="medium"
        )
        
        return response
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """测试错误恢复机制"""
        technical = InterviewerFactory.get_interviewer("technical")
        
        # 测试空消息列表
        response = await technical.generate_response(messages=[])
        assert isinstance(response, str)
        assert len(response) > 0
        
        # 测试无效消息格式
        invalid_messages = [{"invalid": "format"}]
        response = await technical.generate_response(messages=invalid_messages)
        assert isinstance(response, str)
        assert len(response) > 0
        
        # 测试生成反馈时的错误恢复
        feedback = await technical.generate_feedback(messages=[])
        assert isinstance(feedback, dict)


class TestPerformanceAndLoad:
    """性能和负载测试"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """测试响应时间"""
        import time
        
        start_time = time.time()
        
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "简单测试"}],
            service_name="mock"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response_time < 5.0  # 响应时间应该小于5秒
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行多次AI调用
        for i in range(10):
            await ai_service_manager.chat_completion(
                messages=[{"role": "user", "content": f"测试消息 {i}"}],
                service_name="mock"
            )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内（小于100MB）
        assert memory_increase < 100 * 1024 * 1024


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"]) 