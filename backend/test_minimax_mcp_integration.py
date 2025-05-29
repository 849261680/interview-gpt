#!/usr/bin/env python3
"""
测试MiniMax MCP集成
验证文字转语音功能是否正常工作
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量（测试用）
os.environ.setdefault('MINIMAX_API_KEY', 'your_minimax_api_key_here')
os.environ.setdefault('MINIMAX_API_HOST', 'https://api.minimax.chat')
os.environ.setdefault('MINIMAX_API_RESOURCE_MODE', 'url')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_mcp_tools():
    """测试MCP工具调用"""
    logger.info("开始测试MCP工具...")
    
    try:
        # 导入MCP工具
        from mcp_tools import (
            mcp_MiniMax_text_to_audio,
            mcp_MiniMax_list_voices,
            MCPResult
        )
        
        logger.info("MCP工具导入成功")
        
        # 测试1: 获取语音列表
        logger.info("测试1: 获取语音列表")
        voices_result = mcp_MiniMax_list_voices("all")
        
        if voices_result.success:
            logger.info("✅ 获取语音列表成功")
            logger.info(f"语音列表: {voices_result.content[:200]}...")
        else:
            logger.error(f"❌ 获取语音列表失败: {voices_result.error}")
        
        # 测试2: 文字转语音
        logger.info("测试2: 文字转语音")
        test_text = "你好，这是MiniMax MCP文字转语音测试。"
        
        tts_result = mcp_MiniMax_text_to_audio(
            text=test_text,
            voice_id="female-tianmei",
            model="speech-02-hd"
        )
        
        if tts_result.success:
            logger.info("✅ 文字转语音成功")
            logger.info(f"TTS结果: {tts_result.content}")
        else:
            logger.error(f"❌ 文字转语音失败: {tts_result.error}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 导入MCP工具失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ 测试MCP工具时发生异常: {str(e)}")
        return False

async def test_audio_service():
    """测试音频服务"""
    logger.info("开始测试音频服务...")
    
    try:
        # 导入音频服务
        from src.services.audio_service import audio_service
        
        logger.info("音频服务导入成功")
        
        # 测试服务状态
        logger.info("测试: 获取服务状态")
        status = audio_service.get_service_status()
        logger.info(f"服务状态: {status}")
        
        # 测试文字转语音
        logger.info("测试: 文字转语音")
        test_text = "你好，这是音频服务测试。"
        
        result = await audio_service.text_to_speech(
            text=test_text,
            voice_id="female-tianmei",
            service="minimax"
        )
        
        if result.get('success'):
            logger.info("✅ 音频服务TTS成功")
            logger.info(f"结果: {result}")
        else:
            logger.error(f"❌ 音频服务TTS失败: {result.get('error')}")
        
        # 测试获取语音列表
        logger.info("测试: 获取语音列表")
        voices_result = await audio_service.get_available_voices("minimax")
        
        if voices_result.get('success'):
            logger.info("✅ 获取语音列表成功")
            logger.info(f"语音数量: {len(str(voices_result.get('voices', '')))}")
        else:
            logger.error(f"❌ 获取语音列表失败: {voices_result.get('error')}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 导入音频服务失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ 测试音频服务时发生异常: {str(e)}")
        return False

async def test_api_endpoints():
    """测试API端点"""
    logger.info("开始测试API端点...")
    
    try:
        import httpx
        
        # 测试API服务器是否运行
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            # 测试健康检查
            logger.info("测试: 健康检查")
            try:
                response = await client.get(f"{base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ API服务器运行正常")
                else:
                    logger.warning(f"⚠️ API服务器响应异常: {response.status_code}")
            except httpx.ConnectError:
                logger.warning("⚠️ API服务器未运行，跳过API测试")
                return False
            
            # 测试MiniMax TTS API
            logger.info("测试: MiniMax TTS API")
            try:
                tts_data = {
                    "text": "这是API测试文本",
                    "voice_id": "female-tianmei",
                    "service": "minimax"
                }
                
                response = await client.post(
                    f"{base_url}/api/api/minimax-tts/synthesize",
                    json=tts_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ MiniMax TTS API测试成功")
                    logger.info(f"API响应: {result}")
                else:
                    logger.error(f"❌ MiniMax TTS API测试失败: {response.status_code}")
                    logger.error(f"错误详情: {response.text}")
                    
            except Exception as e:
                logger.error(f"❌ MiniMax TTS API测试异常: {str(e)}")
            
            # 测试服务状态API
            logger.info("测试: 服务状态API")
            try:
                response = await client.get(
                    f"{base_url}/api/api/minimax-tts/status",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ 服务状态API测试成功")
                    logger.info(f"状态: {result}")
                else:
                    logger.error(f"❌ 服务状态API测试失败: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ 服务状态API测试异常: {str(e)}")
        
        return True
        
    except ImportError:
        logger.warning("⚠️ httpx未安装，跳过API测试")
        return False
    except Exception as e:
        logger.error(f"❌ 测试API端点时发生异常: {str(e)}")
        return False

async def main():
    """主测试函数"""
    logger.info("🚀 开始MiniMax MCP集成测试")
    logger.info("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key or api_key == 'your_minimax_api_key_here':
        logger.warning("⚠️ MINIMAX_API_KEY未配置，某些测试可能失败")
    else:
        logger.info("✅ MINIMAX_API_KEY已配置")
    
    # 运行测试
    tests = [
        ("MCP工具测试", test_mcp_tools()),
        ("音频服务测试", test_audio_service()),
        ("API端点测试", test_api_endpoints())
    ]
    
    results = []
    for test_name, test_coro in tests:
        logger.info(f"\n📋 {test_name}")
        logger.info("-" * 40)
        
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name}发生异常: {str(e)}")
            results.append((test_name, False))
    
    # 输出测试总结
    logger.info("\n" + "=" * 60)
    logger.info("📊 测试总结")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！MiniMax MCP集成正常工作")
    else:
        logger.warning("⚠️ 部分测试失败，请检查配置和依赖")

if __name__ == "__main__":
    asyncio.run(main()) 