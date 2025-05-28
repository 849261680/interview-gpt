#!/usr/bin/env python3
"""
使用MCP客户端库测试MiniMax MCP
"""
import asyncio
import os
import tempfile
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_minimax_mcp_client():
    print('=== MiniMax MCP 客户端测试 ===')
    
    # 检查环境变量
    api_key = os.getenv("MINIMAX_API_KEY", "")
    group_id = os.getenv("MINIMAX_GROUP_ID", "")
    
    if not api_key or not group_id:
        print("❌ 环境变量未正确设置")
        return False
    
    print("✅ 环境变量已正确设置")
    
    try:
        # 创建MCP客户端
        server_params = StdioServerParameters(
            command="minimax-mcp",
            args=[],
            env=os.environ.copy()
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化
                await session.initialize()
                
                # 列出可用工具
                print("\n获取可用工具...")
                tools = await session.list_tools()
                print(f"可用工具: {[tool.name for tool in tools.tools]}")
                
                # 测试text_to_audio工具
                if any(tool.name == "text_to_audio" for tool in tools.tools):
                    print("\n测试 text_to_audio 工具...")
                    
                    # 创建临时输出目录
                    output_dir = tempfile.mkdtemp()
                    print(f"输出目录: {output_dir}")
                    
                    # 调用text_to_audio
                    result = await session.call_tool(
                        "text_to_audio",
                        {
                            "text": "你好，欢迎参加面试！",
                            "voice_id": "female-shaonv",
                            "model": "speech-02-hd",
                            "speed": 1.0,
                            "vol": 1.0,
                            "pitch": 0,
                            "emotion": "happy",
                            "sample_rate": 32000,
                            "bitrate": 128000,
                            "format": "mp3",
                            "output_directory": output_dir
                        }
                    )
                    
                    print(f"TTS结果: {result}")
                    
                    # 检查输出目录
                    files = os.listdir(output_dir)
                    print(f"生成的文件: {files}")
                    
                    if files:
                        print("✅ text_to_audio 测试成功")
                        return True
                    else:
                        print("❌ 没有生成音频文件")
                        return False
                else:
                    print("❌ text_to_audio 工具不可用")
                    return False
                    
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_minimax_mcp_client()) 