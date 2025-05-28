#!/usr/bin/env python3
"""
Google Speech API 测试脚本
测试语音识别功能
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.speech_service import speech_service
from src.config.settings import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_google_speech():
    """测试Google Speech语音识别"""
    try:
        print("🎤 Google Speech API 测试")
        print("=" * 50)
        
        # 检查配置
        print("📋 检查配置...")
        google_credentials = settings.GOOGLE_APPLICATION_CREDENTIALS or settings.GOOGLE_SPEECH_CREDENTIALS_PATH
        if not google_credentials:
            print("❌ Google Speech配置未设置")
            print("请设置以下环境变量之一:")
            print("- GOOGLE_APPLICATION_CREDENTIALS")
            print("- GOOGLE_SPEECH_CREDENTIALS_PATH")
            return
        
        print(f"✅ Google Speech配置已设置: {google_credentials}")
        
        # 检查服务状态
        print("\n🔍 检查服务状态...")
        health = await speech_service.health_check()
        google_status = health.get("services", {}).get("google", {})
        
        if not google_status.get("available", False):
            print("❌ Google Speech服务不可用")
            if "error" in google_status:
                print(f"错误: {google_status['error']}")
            return
        
        print("✅ Google Speech服务可用")
        
        # 测试音频文件
        test_audio_file = "test_audio.mp3"
        if not os.path.exists(test_audio_file):
            print(f"❌ 测试音频文件不存在: {test_audio_file}")
            print("请提供一个测试音频文件")
            return
        
        # 读取音频数据
        print(f"\n📁 读取测试音频文件: {test_audio_file}")
        with open(test_audio_file, 'rb') as f:
            audio_data = f.read()
        
        print(f"✅ 音频文件大小: {len(audio_data)} 字节")
        
        # 执行语音识别
        print("\n🎯 执行Google Speech语音识别...")
        result = await speech_service._google_speech_to_text(
            audio_data=audio_data,
            language="zh-CN",
            audio_format="mp3"
        )
        
        # 显示结果
        print("\n📊 识别结果:")
        print(f"文本: {result.get('text', '')}")
        print(f"置信度: {result.get('confidence', 0):.2f}")
        print(f"语言: {result.get('language', '')}")
        print(f"时长: {result.get('duration', 0):.2f}秒")
        print(f"服务: {result.get('service', '')}")
        
        # 显示候选结果
        if 'alternatives' in result:
            print("\n🔄 候选结果:")
            for i, alt in enumerate(result['alternatives'][:3]):
                print(f"  {i+1}. {alt.get('transcript', '')} (置信度: {alt.get('confidence', 0):.2f})")
        
        print("\n✅ Google Speech测试完成!")
        
    except Exception as e:
        logger.error(f"Google Speech测试失败: {e}")
        print(f"❌ 测试失败: {e}")

async def test_speech_service_integration():
    """测试语音服务集成"""
    try:
        print("\n🔧 测试语音服务集成...")
        
        # 测试音频文件
        test_audio_file = "test_audio.mp3"
        if not os.path.exists(test_audio_file):
            print(f"❌ 测试音频文件不存在: {test_audio_file}")
            return
        
        # 读取音频数据
        with open(test_audio_file, 'rb') as f:
            audio_data = f.read()
        
        # 通过语音服务调用
        print("🎯 通过语音服务调用...")
        result = await speech_service.speech_to_text(
            audio_data=audio_data,
            language="zh-CN",
            audio_format="mp3"
        )
        
        # 显示结果
        print("\n📊 集成测试结果:")
        print(f"文本: {result.get('text', '')}")
        print(f"置信度: {result.get('confidence', 0):.2f}")
        print(f"服务: {result.get('service', '')}")
        
        print("\n✅ 语音服务集成测试完成!")
        
    except Exception as e:
        logger.error(f"语音服务集成测试失败: {e}")
        print(f"❌ 集成测试失败: {e}")

if __name__ == "__main__":
    print("🚀 启动Google Speech测试...")
    
    # 运行测试
    asyncio.run(test_google_speech())
    asyncio.run(test_speech_service_integration())
    
    print("\n🎉 所有测试完成!") 