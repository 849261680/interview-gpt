#!/usr/bin/env python3
"""
测试真实的 MiniMax MCP 服务
验证各种 MCP 服务实现的功能
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_cursor_mcp_service():
    """测试 Cursor MCP 服务"""
    try:
        logger.info("=== 测试 Cursor MCP 服务 ===")
        
        from src.services.speech.cursor_mcp_service import get_cursor_mcp_service
        
        service = get_cursor_mcp_service()
        
        # 获取服务状态
        status = await service.get_service_status()
        logger.info(f"服务状态: {status}")
        
        # 测试 TTS
        tts_result = await service.text_to_speech_real(
            text="这是 Cursor MCP 服务的测试语音",
            interviewer_type="technical"
        )
        logger.info(f"TTS 测试结果: {tts_result}")
        
        # 测试批量生成
        batch_requests = [
            {"text": "技术面试官测试", "interviewer_type": "technical"},
            {"text": "HR面试官测试", "interviewer_type": "hr"},
            {"text": "系统提示测试", "interviewer_type": "system"}
        ]
        
        batch_results = await service.batch_generate_speeches(batch_requests)
        logger.info(f"批量生成测试: 成功 {sum(1 for r in batch_results if r.get('success'))} / {len(batch_results)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Cursor MCP 服务测试失败: {str(e)}")
        return False

async def test_real_mcp_caller():
    """测试真实 MCP 调用器"""
    try:
        logger.info("=== 测试真实 MCP 调用器 ===")
        
        from src.services.speech.real_mcp_caller import get_real_mcp_caller
        
        caller = get_real_mcp_caller()
        
        # 获取服务状态
        status = await caller.get_service_status()
        logger.info(f"调用器状态: {status}")
        
        # 测试 TTS
        tts_result = await caller.text_to_speech_real(
            text="这是真实 MCP 调用器的测试语音",
            interviewer_type="hr"
        )
        logger.info(f"TTS 测试结果: {tts_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"真实 MCP 调用器测试失败: {str(e)}")
        return False

async def test_mcp_bridge():
    """测试 MCP 桥接"""
    try:
        logger.info("=== 测试 MCP 桥接 ===")
        
        from src.services.speech.mcp_bridge import get_mcp_bridge
        
        bridge = get_mcp_bridge()
        
        # 测试连接
        connection_test = await bridge.test_mcp_connection()
        logger.info(f"连接测试: {connection_test}")
        
        # 测试 TTS
        tts_result = await bridge.call_mcp_text_to_audio(
            text="这是 MCP 桥接的测试语音",
            voice_id="female-tianmei",
            speed=1.0,
            emotion="happy"
        )
        logger.info(f"TTS 测试结果: {tts_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"MCP 桥接测试失败: {str(e)}")
        return False

async def test_real_mcp_speech_service():
    """测试真实 MCP 语音服务"""
    try:
        logger.info("=== 测试真实 MCP 语音服务 ===")
        
        from src.services.speech.real_mcp_speech_service import RealMCPSpeechService
        
        service = RealMCPSpeechService()
        
        # 获取服务状态
        status = await service.get_service_status()
        logger.info(f"服务状态: {status}")
        
        # 测试 TTS
        tts_result = await service.text_to_speech_real(
            text="这是真实 MCP 语音服务的测试语音",
            interviewer_type="product"
        )
        logger.info(f"TTS 测试结果: {tts_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"真实 MCP 语音服务测试失败: {str(e)}")
        return False

async def compare_services():
    """比较不同服务的性能"""
    try:
        logger.info("=== 服务性能比较 ===")
        
        test_text = "这是一个性能测试语音，用于比较不同服务的响应时间和质量。"
        
        # 导入所有服务
        from src.services.speech.cursor_mcp_service import get_cursor_mcp_service
        from src.services.speech.real_mcp_caller import get_real_mcp_caller
        from src.services.speech.mcp_bridge import get_mcp_bridge
        from src.services.speech.real_mcp_speech_service import RealMCPSpeechService
        
        services = [
            ("Cursor MCP", get_cursor_mcp_service()),
            ("Real MCP Caller", get_real_mcp_caller()),
            ("Real MCP Speech", RealMCPSpeechService())
        ]
        
        results = {}
        
        for service_name, service in services:
            try:
                import time
                start_time = time.time()
                
                if hasattr(service, 'text_to_speech_real'):
                    result = await service.text_to_speech_real(test_text, "system")
                else:
                    continue
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[service_name] = {
                    "success": result.get("success", False),
                    "duration": duration,
                    "method": result.get("method", "unknown"),
                    "file_size": len(test_text)
                }
                
                logger.info(f"{service_name}: {duration:.2f}s - {'成功' if result.get('success') else '失败'}")
                
            except Exception as e:
                logger.error(f"{service_name} 测试失败: {str(e)}")
                results[service_name] = {"error": str(e)}
        
        # 输出比较结果
        logger.info("性能比较结果:")
        for service_name, result in results.items():
            if "error" not in result:
                logger.info(f"  {service_name}: {result['duration']:.2f}s ({result['method']})")
            else:
                logger.info(f"  {service_name}: 错误 - {result['error']}")
        
        return results
        
    except Exception as e:
        logger.error(f"服务比较失败: {str(e)}")
        return {}

async def main():
    """主测试函数"""
    logger.info("开始测试真实的 MiniMax MCP 服务")
    
    test_results = {}
    
    # 测试各个服务
    test_functions = [
        ("Cursor MCP 服务", test_cursor_mcp_service),
        ("真实 MCP 调用器", test_real_mcp_caller),
        ("MCP 桥接", test_mcp_bridge),
        ("真实 MCP 语音服务", test_real_mcp_speech_service)
    ]
    
    for test_name, test_func in test_functions:
        try:
            logger.info(f"\n{'='*50}")
            result = await test_func()
            test_results[test_name] = result
            logger.info(f"{test_name}: {'✓ 成功' if result else '✗ 失败'}")
        except Exception as e:
            logger.error(f"{test_name} 测试异常: {str(e)}")
            test_results[test_name] = False
    
    # 性能比较
    logger.info(f"\n{'='*50}")
    comparison_results = await compare_services()
    
    # 总结
    logger.info(f"\n{'='*50}")
    logger.info("=== 测试总结 ===")
    
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    
    logger.info(f"测试通过: {success_count}/{total_count}")
    
    for test_name, result in test_results.items():
        status = "✓ 成功" if result else "✗ 失败"
        logger.info(f"  {test_name}: {status}")
    
    if comparison_results:
        logger.info("\n性能排名:")
        sorted_results = sorted(
            [(name, data) for name, data in comparison_results.items() if "error" not in data],
            key=lambda x: x[1].get("duration", float('inf'))
        )
        
        for i, (name, data) in enumerate(sorted_results, 1):
            logger.info(f"  {i}. {name}: {data['duration']:.2f}s")
    
    logger.info("\n测试完成！")
    
    return test_results

if __name__ == "__main__":
    # 运行测试
    results = asyncio.run(main())
    
    # 退出码
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\n🎉 所有测试通过！({success_count}/{total_count})")
        sys.exit(0)
    else:
        print(f"\n⚠️  部分测试失败 ({success_count}/{total_count})")
        sys.exit(1) 