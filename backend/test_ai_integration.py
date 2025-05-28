#!/usr/bin/env python3
"""
简化的AI集成测试运行脚本
快速验证AI集成功能是否正常工作
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

async def test_ai_service_manager():
    """测试AI服务管理器"""
    print("🔧 测试AI服务管理器...")
    
    try:
        from src.services.ai.ai_service_manager import ai_service_manager
        
        # 测试获取服务
        primary_service = ai_service_manager.get_primary_service()
        available_services = ai_service_manager.get_available_services()
        
        print(f"  ✓ 主要服务: {primary_service}")
        print(f"  ✓ 可用服务: {available_services}")
        
        # 测试健康检查
        health_status = await ai_service_manager.health_check()
        for service, status in health_status.items():
            status_icon = "✓" if status else "✗"
            print(f"  {status_icon} {service}: {'健康' if status else '异常'}")
        
        # 测试聊天功能
        response = await ai_service_manager.chat_completion(
            messages=[{"role": "user", "content": "你好"}],
            service_name="mock"
        )
        print(f"  ✓ 聊天测试: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False


async def test_crewai_integration():
    """测试CrewAI集成"""
    print("\n🤖 测试CrewAI集成...")
    
    try:
        from src.services.ai.crewai_integration import crewai_integration
        
        # 测试可用性
        is_available = crewai_integration.is_crewai_available()
        print(f"  ✓ CrewAI可用: {is_available}")
        
        # 测试面试官列表
        interviewers = crewai_integration.get_available_interviewers()
        print(f"  ✓ 可用面试官: {interviewers}")
        
        # 测试面试轮次
        test_messages = [
            {"sender_type": "user", "content": "我有3年Python开发经验"}
        ]
        
        response = await crewai_integration.conduct_interview_round(
            interviewer_type="technical",
            messages=test_messages,
            position="Python工程师",
            difficulty="medium"
        )
        print(f"  ✓ 面试轮次测试: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False


async def test_interviewer_factory():
    """测试面试官工厂"""
    print("\n👥 测试面试官工厂...")
    
    try:
        from src.agents.interviewer_factory import InterviewerFactory
        
        # 测试获取面试官类型
        types = InterviewerFactory.get_all_interviewer_types()
        print(f"  ✓ 面试官类型: {list(types.keys())}")
        
        # 测试创建面试官
        for interviewer_id in ["technical", "hr", "behavioral"]:
            interviewer = InterviewerFactory.get_interviewer(interviewer_id)
            print(f"  ✓ {interviewer_id}: {interviewer.name} - {interviewer.role}")
            
            # 测试生成问题
            questions = await interviewer.generate_questions("测试职位", "medium")
            print(f"    - 生成问题数量: {len(questions)}")
            
            # 测试生成回复
            response = await interviewer.generate_response([
                {"sender_type": "user", "content": "测试消息"}
            ])
            print(f"    - 回复长度: {len(response)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False


async def test_deepseek_api():
    """测试DEEPSEEK API"""
    print("\n🧠 测试DEEPSEEK API...")
    
    try:
        from src.config.settings import settings
        
        if not settings.DEEPSEEK_API_KEY:
            print("  ⚠ DEEPSEEK_API_KEY未配置，跳过API测试")
            return True
        
        from src.services.ai.deepseek_client import DeepSeekClient
        
        client = DeepSeekClient(
            api_key=settings.DEEPSEEK_API_KEY,
            model="deepseek-chat"
        )
        
        # 测试健康检查
        is_healthy = await client.health_check()
        print(f"  ✓ 健康检查: {'通过' if is_healthy else '失败'}")
        
        if is_healthy:
            # 测试聊天完成
            response = await client.chat_completion(
                messages=[{"role": "user", "content": "什么是Python？"}],
                max_tokens=100
            )
            print(f"  ✓ 聊天完成: {response[:50]}...")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False


async def test_complete_interview_flow():
    """测试完整面试流程"""
    print("\n🎯 测试完整面试流程...")
    
    try:
        from src.agents.interviewer_factory import InterviewerFactory
        from src.services.ai.crewai_integration import crewai_integration
        
        # 1. 创建技术面试官
        technical = InterviewerFactory.get_interviewer("technical")
        print(f"  ✓ 创建面试官: {technical.name}")
        
        # 2. 生成面试问题
        questions = await technical.generate_questions("Python工程师", "medium")
        print(f"  ✓ 生成问题: {len(questions)}个")
        
        # 3. 模拟面试对话
        messages = [
            {"sender_type": "interviewer", "content": questions[0], "interviewer_id": "technical"},
            {"sender_type": "user", "content": "我有3年Python开发经验，熟悉Django和FastAPI"}
        ]
        
        # 4. 生成面试官回复
        response = await technical.generate_response(messages)
        print(f"  ✓ 面试官回复: {len(response)}字符")
        
        # 5. 生成面试反馈
        messages.append({"sender_type": "interviewer", "content": response, "interviewer_id": "technical"})
        feedback = await technical.generate_feedback(messages)
        print(f"  ✓ 生成反馈: {type(feedback).__name__}")
        
        # 6. 生成最终评估
        assessment = await crewai_integration.generate_final_assessment(
            messages=messages,
            position="Python工程师"
        )
        print(f"  ✓ 最终评估: 总分 {assessment.get('overall_score', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始AI集成测试")
    print("=" * 50)
    
    # 检查环境
    print("📋 环境检查:")
    print(f"  Python版本: {sys.version}")
    print(f"  工作目录: {os.getcwd()}")
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        print(f"  DEEPSEEK_API_KEY: 已配置")
    else:
        print(f"  DEEPSEEK_API_KEY: 未配置（将使用Mock服务）")
    
    # 运行测试
    tests = [
        ("AI服务管理器", test_ai_service_manager),
        ("CrewAI集成", test_crewai_integration),
        ("面试官工厂", test_interviewer_factory),
        ("DEEPSEEK API", test_deepseek_api),
        ("完整面试流程", test_complete_interview_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有AI集成测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查配置和实现")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 测试运行异常: {e}")
        sys.exit(1) 