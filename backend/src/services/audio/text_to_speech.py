"""
文本转语音服务
使用MiniMax TTS API将文本转换为语音
"""
import base64
import logging
import aiohttp
import os
from typing import Dict, Any, Optional
import json
import uuid

# 设置日志
logger = logging.getLogger(__name__)

# MiniMax API配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_TTS_URL = "https://api.minimax.chat/v1/audio/text_to_speech"


async def text_to_speech(
    text: str, 
    voice_id: str = "male-qn-qingse",
    language: str = "zh"
) -> Dict[str, Any]:
    """
    将文本转换为语音
    
    Args:
        text: 要转换的文本
        voice_id: 语音ID，可选值：
                 - male-qn-qingse: 男声-轻色
                 - female-shaibei: 女声-筛贝
                 - female-zhichu: 女声-织楚
        language: 语言代码 (默认zh)
        
    Returns:
        Dict[str, Any]: 包含Base64编码的音频数据和元信息
    """
    try:
        logger.info(f"开始文本转语音: {text[:30]}...")
        
        # 验证API密钥
        if not MINIMAX_API_KEY:
            logger.error("缺少MiniMax API密钥")
            raise ValueError("缺少MiniMax API密钥")
        
        # 准备请求头
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 准备请求体
        payload = {
            "text": text,
            "model": "speech-v2",
            "voice_id": voice_id,
            "speed": 1.0,         # 语速，范围0.5-2.0
            "vol": 1.0,           # 音量，范围0.1-1.0
            "pitch": 0,           # 音调，范围-12到12
            "config": {
                "audio_type": "mp3"  # 返回音频格式，可选mp3或wav
            }
        }
        
        # 发送请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                MINIMAX_TTS_URL,
                headers=headers,
                json=payload
            ) as response:
                # 检查响应状态
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"文本转语音请求失败: {response.status}, {error_text}")
                    return {
                        "audio_data": "",
                        "error": f"API请求失败: {response.status}"
                    }
                
                # 解析响应
                result = await response.json()
                
                # 提取音频数据
                audio_data = result.get("audio", "")
                
                logger.info("文本转语音成功")
                
                return {
                    "audio_data": audio_data,
                    "audio_type": "mp3",
                    "voice_id": voice_id
                }
                
    except Exception as e:
        logger.error(f"文本转语音出错: {str(e)}")
        return {
            "audio_data": "",
            "error": f"文本转语音服务错误: {str(e)}"
        }


async def save_audio_file(audio_data: str, output_dir: str = "uploads/audio") -> Dict[str, Any]:
    """
    保存Base64编码的音频数据到文件
    
    Args:
        audio_data: Base64编码的音频数据
        output_dir: 输出目录
        
    Returns:
        Dict[str, Any]: 包含文件路径和URL的结果
    """
    try:
        logger.info("开始保存音频文件")
        
        # 创建输出目录（如果不存在）
        os.makedirs(output_dir, exist_ok=True)
        
        # 解码Base64数据
        audio_bytes = base64.b64decode(audio_data)
        
        # 生成唯一文件名
        file_name = f"{uuid.uuid4()}.mp3"
        file_path = os.path.join(output_dir, file_name)
        
        # 写入文件
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        
        logger.info(f"音频文件已保存: {file_path}")
        
        # 构建URL
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        file_url = f"{base_url}/audio/{file_name}"
        
        return {
            "file_path": file_path,
            "file_url": file_url
        }
        
    except Exception as e:
        logger.error(f"保存音频文件出错: {str(e)}")
        return {
            "file_path": "",
            "file_url": "",
            "error": f"保存音频文件错误: {str(e)}"
        }


async def get_interviewer_voice(interviewer_id: str) -> str:
    """
    根据面试官ID获取对应的语音ID
    
    Args:
        interviewer_id: 面试官ID
        
    Returns:
        str: 语音ID
    """
    # 面试官语音映射
    voice_mapping = {
        "technical": "male-qn-qingse",   # 技术面试官使用男声
        "hr": "female-shaibei",          # HR面试官使用女声
        "behavioral": "male-qn-qingse"   # 行为面试官使用男声
    }
    
    # 返回对应的语音ID，默认使用男声
    return voice_mapping.get(interviewer_id, "male-qn-qingse")
