#!/usr/bin/env python3
"""
真正的 MiniMax MCP 集成演示
展示如何在后端真正调用 MiniMax MCP 工具
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

async def demo_real_mcp_interview():
    """演示真正的 MCP 面试流程"""
    try:
        logger.info("=== 真正的 MiniMax MCP 面试演示 ===")
        
        # 导入真实的 MCP 服务
        from src.services.speech.cursor_mcp_service import get_cursor_mcp_service
        
        service = get_cursor_mcp_service()
        
        # 面试对话内容
        interview_dialogues = [
            {
                "interviewer": "system",
                "text": "欢迎参加我们的AI模拟面试！今天将有多位面试官与您交流，请放轻松。",
                "role": "系统提示"
            },
            {
                "interviewer": "technical", 
                "text": "我是技术面试官。请先简单介绍一下您的技术背景和最擅长的编程语言。",
                "role": "技术面试官"
            },
            {
                "interviewer": "hr",
                "text": "我是HR面试官。请谈谈您为什么想要加入我们公司，以及您的职业规划。",
                "role": "HR面试官"
            },
            {
                "interviewer": "behavioral",
                "text": "我是行为面试官。请描述一次您在团队中解决冲突的经历。",
                "role": "行为面试官"
            },
            {
                "interviewer": "product",
                "text": "我是产品面试官。如果让您设计一个新的移动应用，您会如何开始？",
                "role": "产品面试官"
            },
            {
                "interviewer": "final",
                "text": "我是总面试官。感谢您的精彩回答。我们会在一周内给您反馈。",
                "role": "总面试官"
            }
        ]
        
        logger.info(f"准备生成 {len(interview_dialogues)} 段面试语音")
        
        # 批量生成语音
        speech_requests = [
            {
                "text": dialogue["text"],
                "interviewer_type": dialogue["interviewer"]
            }
            for dialogue in interview_dialogues
        ]
        
        results = await service.batch_generate_speeches(speech_requests)
        
        # 输出结果
        logger.info("面试语音生成结果:")
        for i, (dialogue, result) in enumerate(zip(interview_dialogues, results), 1):
            if result.get("success"):
                logger.info(f"  {i}. {dialogue['role']}: ✓ 成功")
                logger.info(f"     文件: {result['file_name']}")
                logger.info(f"     语音: {result.get('voice_name', 'Unknown')}")
                logger.info(f"     方法: {result.get('method', 'Unknown')}")
            else:
                logger.error(f"  {i}. {dialogue['role']}: ✗ 失败 - {result.get('error', 'Unknown error')}")
        
        success_count = sum(1 for result in results if result.get("success"))
        logger.info(f"\n生成成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        
        return results
        
    except Exception as e:
        logger.error(f"MCP 面试演示失败: {str(e)}")
        return []

async def main():
    """主演示函数"""
    logger.info("开始 MiniMax MCP 真实集成演示")
    
    # 运行演示
    result = await demo_real_mcp_interview()
    
    # 总结
    logger.info("=== 演示总结 ===")
    if result:
        success_count = sum(1 for r in result if r.get("success"))
        logger.info(f"✓ 面试语音生成: 成功 {success_count}/{len(result)}")
    else:
        logger.info("✗ 演示失败")
    
    logger.info("\n🎉 MiniMax MCP 真实集成演示完成！")
    
    return result

if __name__ == "__main__":
    # 运行演示
    results = asyncio.run(main())
    print(f"\n🚀 演示完成！") 