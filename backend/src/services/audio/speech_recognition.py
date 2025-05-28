"""
语音识别服务
使用MiniMax ASR API将语音转换为文本
"""
import base64
import logging
import aiohttp
import os
from typing import Dict, Any, Optional
import json

# 设置日志
logger = logging.getLogger(__name__)

# MiniMax API配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_ASR_URL = "https://api.minimax.chat/v1/audio/speech_recognition"


async def recognize_speech(audio_data: str, language: str = "zh") -> Dict[str, Any]:
    """
    将语音转换为文本
    
    Args:
        audio_data: Base64编码的音频数据
        language: 语言代码 (默认zh)
        
    Returns:
        Dict[str, Any]: 包含识别文本和置信度的结果
    """
    try:
        logger.info("开始语音识别")
        
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
            "audio": audio_data,
            "language": language,
            "type": "general"  # 通用识别模式
        }
        
        # 发送请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                MINIMAX_ASR_URL,
                headers=headers,
                json=payload
            ) as response:
                # 检查响应状态
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"语音识别请求失败: {response.status}, {error_text}")
                    return {
                        "text": "",
                        "confidence": 0.0,
                        "error": f"API请求失败: {response.status}"
                    }
                
                # 解析响应
                result = await response.json()
                
                # 提取文本和置信度
                text = result.get("text", "")
                confidence = result.get("confidence", 0.0)
                
                logger.info(f"语音识别成功, 置信度: {confidence}")
                
                return {
                    "text": text,
                    "confidence": confidence
                }
                
    except Exception as e:
        logger.error(f"语音识别出错: {str(e)}")
        return {
            "text": "",
            "confidence": 0.0,
            "error": f"语音识别服务错误: {str(e)}"
        }


async def process_audio_file(file_path: str, language: str = "zh") -> Dict[str, Any]:
    """
    处理音频文件并进行语音识别
    
    Args:
        file_path: 音频文件路径
        language: 语言代码 (默认zh)
        
    Returns:
        Dict[str, Any]: 包含识别文本和置信度的结果
    """
    try:
        logger.info(f"处理音频文件: {file_path}")
        
        # 读取文件
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        
        # 转换为Base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        # 调用语音识别
        result = await recognize_speech(audio_base64, language)
        
        return result
        
    except Exception as e:
        logger.error(f"处理音频文件出错: {str(e)}")
        return {
            "text": "",
            "confidence": 0.0,
            "error": f"处理音频文件错误: {str(e)}"
        }
