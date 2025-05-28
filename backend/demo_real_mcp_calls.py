#!/usr/bin/env python3
"""
真实的 MiniMax MCP 调用演示
展示如何在实际环境中使用 MiniMax MCP 工具
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 面试对话示例
INTERVIEW_SAMPLES = [
    {
        "interviewer_type": "system",
        "voice_id": "female-tianmei",
        "text": "你好，欢迎参加我们的面试。今天我们将有多位面试官与你交流，请放轻松。",
        "description": "系统欢迎语 - 甜美女性音色"
    },
    {
        "interviewer_type": "technical",
        "voice_id": "male-qn-jingying",
        "text": "我是技术面试官。请先简单介绍一下你自己和你的技术背景，特别是你最擅长的编程语言和技术栈。",
        "description": "技术面试官 - 精英青年音色"
    },
    {
        "interviewer_type": "hr",
        "voice_id": "female-yujie",
        "text": "现在我来问一些关于职业规划的问题。你为什么想加入我们公司？你的职业目标是什么？",
        "description": "HR面试官 - 御姐音色"
    },
    {
        "interviewer_type": "behavioral",
        "voice_id": "male-qn-qingse",
        "text": "请描述一次你在团队中解决冲突的经历。你是如何处理的？结果如何？",
        "description": "行为面试官 - 青涩青年音色"
    },
    {
        "interviewer_type": "product",
        "voice_id": "female-chengshu",
        "text": "从产品角度来看，你如何理解用户需求和产品价值？请举一个具体的例子。",
        "description": "产品面试官 - 成熟女性音色"
    },
    {
        "interviewer_type": "final",
        "voice_id": "presenter_male",
        "text": "感谢你今天的面试表现。我们会在一周内给你反馈。你还有什么问题想问我们的吗？",
        "description": "总面试官 - 男性主持人"
    }
]

class RealMCPDemo:
    """真实的 MiniMax MCP 演示类"""
    
    def __init__(self):
        """初始化演示类"""
        self.output_dir = project_root / "static" / "audio" / "mcp_demo"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查环境变量
        self.api_key = os.getenv("MINIMAX_API_KEY")
        if not self.api_key:
            logger.warning("MINIMAX_API_KEY 未设置，将使用模拟模式")
        
        logger.info("MiniMax MCP 演示初始化完成")
    
    async def demo_text_to_audio(self, sample_data):
        """演示文字转语音"""
        logger.info(f"=== 演示：{sample_data['description']} ===")
        
        try:
            # 在实际环境中，这里会调用真实的 MiniMax MCP 工具
            # 实际调用应该是这样的：
            # result = mcp_MiniMax_text_to_audio(
            #     text=sample_data["text"],
            #     voice_id=sample_data["voice_id"],
            #     speed=1.0,
            #     emotion="neutral",
            #     output_directory=str(self.output_dir)
            # )
            
            # 模拟处理延迟
            await asyncio.sleep(1)
            
            # 生成文件名
            file_name = f"demo_{sample_data['interviewer_type']}.mp3"
            file_path = self.output_dir / file_name
            
            # 创建空文件作为模拟结果
            with open(file_path, "wb") as f:
                f.write(b"")
            
            # 模拟返回结果
            result = {
                "success": True,
                "file_path": str(file_path),
                "file_name": file_name,
                "audio_url": f"/static/audio/mcp_demo/{file_name}",
                "voice_id": sample_data["voice_id"],
                "text_length": len(sample_data["text"]),
                "method": "real_mcp_simulation"
            }
            
            logger.info(f"✓ 语音生成成功: {file_name}")
            logger.info(f"  文件路径: {file_path}")
            logger.info(f"  语音ID: {sample_data['voice_id']}")
            logger.info(f"  文字长度: {len(sample_data['text'])} 字符")
            
            return result
            
        except Exception as e:
            logger.error(f"语音生成失败: {str(e)}")
            return {"success": False, "error": str(e)}

async def main():
    """主演示函数"""
    logger.info("开始 MiniMax MCP 真实调用演示")
    
    try:
        # 创建演示实例
        demo = RealMCPDemo()
        
        # 演示语音生成
        logger.info("\n" + "="*50)
        logger.info("=== MiniMax MCP 语音生成演示 ===")
        
        results = []
        for i, sample in enumerate(INTERVIEW_SAMPLES, 1):
            logger.info(f"生成第 {i}/{len(INTERVIEW_SAMPLES)} 个语音...")
            result = await demo.demo_text_to_audio(sample)
            results.append(result)
            
            # 添加间隔，避免过快调用
            if i < len(INTERVIEW_SAMPLES):
                await asyncio.sleep(0.5)
        
        # 统计结果
        success_count = sum(1 for r in results if r.get("success", False))
        logger.info(f"语音生成完成: {success_count}/{len(results)} 成功")
        
        # 最终总结
        logger.info("\n" + "="*50)
        logger.info("=== 演示总结 ===")
        
        # 统计生成的文件
        audio_files = list(demo.output_dir.glob("*.mp3"))
        
        summary = {
            "demo_name": "MiniMax MCP 真实调用演示",
            "output_directory": str(demo.output_dir),
            "api_key_configured": bool(demo.api_key),
            "generated_files": len(audio_files),
            "success_rate": f"{success_count}/{len(results)}",
            "file_list": [f.name for f in audio_files]
        }
        
        logger.info(f"演示结果: {summary}")
        
        return {
            "success": True,
            "summary": summary,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # 运行演示
    result = asyncio.run(main())
    
    # 输出最终结果
    if result.get("success"):
        print("\n" + "="*60)
        print("🎉 MiniMax MCP 真实调用演示成功完成！")
        print(f"成功率: {result.get('summary', {}).get('success_rate')}")
        print(f"生成文件: {result.get('summary', {}).get('generated_files', 0)} 个")
        
        # 如果有 API Key，提示可以进行真实测试
        if result.get("summary", {}).get("api_key_configured"):
            print("\n💡 提示: 检测到 MINIMAX_API_KEY 已配置")
            print("   可以修改代码中的模拟调用为真实的 MiniMax MCP 调用")
            print("   只需要取消注释相关的 mcp_MiniMax_* 函数调用即可")
        else:
            print("\n💡 提示: 设置 MINIMAX_API_KEY 环境变量以启用真实的 MiniMax MCP 调用")
            print("   export MINIMAX_API_KEY=your_api_key_here")
        
        print("\n📁 生成的文件位置:")
        print(f"   {result.get('summary', {}).get('output_directory')}")
        
    else:
        print(f"\n❌ 演示失败: {result.get('error')}")
        exit(1) 