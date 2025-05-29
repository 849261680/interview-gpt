"""
音频处理服务
集成多种TTS和ASR服务，包括MiniMax MCP、OpenAI、Google Speech等
"""

import os
import logging
import tempfile
import asyncio
from typing import Optional, Dict, Any, Union
from pathlib import Path
import aiofiles
import httpx
from dotenv import load_dotenv

# 导入MCP工具函数
try:
    from mcp_tools import (
        mcp_MiniMax_text_to_audio,
        mcp_MiniMax_list_voices,
        mcp_MiniMax_play_audio
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP工具不可用，将使用备用TTS服务")

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class AudioService:
    """音频处理服务类"""
    
    def __init__(self):
        # MiniMax配置
        self.minimax_api_key = os.getenv('MINIMAX_API_KEY')
        self.minimax_available = MCP_AVAILABLE and bool(self.minimax_api_key)
        
        # OpenAI配置
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_available = bool(self.openai_api_key)
        
        # 音频文件存储目录
        self.audio_dir = Path(__file__).parent.parent.parent / "static" / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"音频服务初始化完成 - MiniMax: {self.minimax_available}, OpenAI: {self.openai_available}")
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: str = "female-tianmei",
        service: str = "auto"
    ) -> Dict[str, Any]:
        """
        文字转语音
        
        Args:
            text: 要转换的文本
            voice_id: 语音ID
            service: 指定服务 ("minimax", "openai", "auto")
            
        Returns:
            包含音频URL或文件路径的结果字典
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "文本内容不能为空",
                "message": "请提供有效的文本内容"
            }
        
        # 自动选择服务
        if service == "auto":
            if self.minimax_available:
                service = "minimax"
            elif self.openai_available:
                service = "openai"
            else:
                return {
                    "success": False,
                    "error": "没有可用的TTS服务",
                    "message": "请配置MiniMax或OpenAI API密钥"
                }
        
        try:
            if service == "minimax" and self.minimax_available:
                return await self._minimax_tts(text, voice_id)
            elif service == "openai" and self.openai_available:
                return await self._openai_tts(text, voice_id)
            else:
                return {
                    "success": False,
                    "error": f"服务 {service} 不可用",
                    "message": f"请检查 {service} 的配置"
                }
                
        except Exception as e:
            logger.error(f"TTS服务调用失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"语音合成失败: {str(e)}"
            }
    
    async def _minimax_tts(self, text: str, voice_id: str) -> Dict[str, Any]:
        """使用MiniMax MCP进行文字转语音"""
        try:
            logger.info(f"使用MiniMax MCP进行TTS: {text[:50]}...")
            
            # 调用MiniMax MCP工具
            result = mcp_MiniMax_text_to_audio(
                text=text,
                voice_id=voice_id,
                model="speech-02-hd",
                speed=1.0,
                vol=1.0,
                pitch=0,
                emotion="happy",
                sample_rate=32000,
                bitrate=128000,
                channel=1,
                format="mp3",
                language_boost="auto",
                output_directory=str(self.audio_dir)
            )
            
            # 解析MCP工具返回结果
            if hasattr(result, 'content') and result.content:
                content = result.content
                
                if "Success" in content:
                    if "Audio URL:" in content:
                        # URL模式
                        url_start = content.find("Audio URL:") + len("Audio URL:")
                        audio_url = content[url_start:].strip()
                        
                        logger.info(f"MiniMax TTS成功，音频URL: {audio_url}")
                        
                        return {
                            "success": True,
                            "audio_url": audio_url,
                            "voice_used": voice_id,
                            "service": "minimax",
                            "message": "MiniMax语音合成成功"
                        }
                    
                    elif "File saved as:" in content:
                        # 本地文件模式
                        file_start = content.find("File saved as:") + len("File saved as:")
                        voice_start = content.find("Voice used:")
                        
                        if voice_start > 0:
                            audio_path = content[file_start:voice_start].strip().rstrip(".")
                        else:
                            audio_path = content[file_start:].strip()
                        
                        logger.info(f"MiniMax TTS成功，音频文件: {audio_path}")
                        
                        return {
                            "success": True,
                            "audio_path": audio_path,
                            "voice_used": voice_id,
                            "service": "minimax",
                            "message": "MiniMax语音合成成功"
                        }
                
                # 如果包含错误信息
                logger.error(f"MiniMax TTS失败: {content}")
                return {
                    "success": False,
                    "error": content,
                    "service": "minimax",
                    "message": "MiniMax语音合成失败"
                }
            
            else:
                logger.error("MiniMax MCP工具返回空结果")
                return {
                    "success": False,
                    "error": "MCP工具返回空结果",
                    "service": "minimax",
                    "message": "MiniMax语音合成失败"
                }
                
        except Exception as e:
            logger.error(f"MiniMax TTS异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "service": "minimax",
                "message": f"MiniMax语音合成异常: {str(e)}"
            }
    
    async def _openai_tts(self, text: str, voice_id: str = "alloy") -> Dict[str, Any]:
        """使用OpenAI进行文字转语音"""
        try:
            logger.info(f"使用OpenAI TTS: {text[:50]}...")
            
            # OpenAI语音映射
            openai_voices = {
                "female-tianmei": "nova",
                "female-shaonv": "shimmer", 
                "male-qn-qingse": "onyx",
                "male-chunhou": "fable",
                "default": "alloy"
            }
            
            openai_voice = openai_voices.get(voice_id, "alloy")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "tts-1",
                        "input": text,
                        "voice": openai_voice,
                        "response_format": "mp3"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    # 保存音频文件
                    audio_filename = f"openai_tts_{hash(text) % 10000}.mp3"
                    audio_path = self.audio_dir / audio_filename
                    
                    async with aiofiles.open(audio_path, 'wb') as f:
                        await f.write(response.content)
                    
                    logger.info(f"OpenAI TTS成功，音频文件: {audio_path}")
                    
                    return {
                        "success": True,
                        "audio_path": str(audio_path),
                        "voice_used": openai_voice,
                        "service": "openai",
                        "message": "OpenAI语音合成成功"
                    }
                else:
                    error_msg = f"OpenAI API错误: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "service": "openai",
                        "message": "OpenAI语音合成失败"
                    }
                    
        except Exception as e:
            logger.error(f"OpenAI TTS异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "service": "openai",
                "message": f"OpenAI语音合成异常: {str(e)}"
            }
    
    async def get_available_voices(self, service: str = "auto") -> Dict[str, Any]:
        """获取可用的语音列表"""
        try:
            if service == "auto":
                if self.minimax_available:
                    service = "minimax"
                elif self.openai_available:
                    service = "openai"
                else:
                    return {
                        "success": False,
                        "error": "没有可用的TTS服务",
                        "voices": []
                    }
            
            if service == "minimax" and self.minimax_available:
                return await self._get_minimax_voices()
            elif service == "openai":
                return await self._get_openai_voices()
            else:
                return {
                    "success": False,
                    "error": f"服务 {service} 不可用",
                    "voices": []
                }
                
        except Exception as e:
            logger.error(f"获取语音列表失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "voices": []
            }
    
    async def _get_minimax_voices(self) -> Dict[str, Any]:
        """获取MiniMax可用语音"""
        try:
            result = mcp_MiniMax_list_voices(voice_type="all")
            
            if hasattr(result, 'content') and result.content:
                content = result.content
                
                if "Success" in content:
                    return {
                        "success": True,
                        "voices": content,
                        "service": "minimax",
                        "message": "获取MiniMax语音列表成功"
                    }
                else:
                    return {
                        "success": False,
                        "error": content,
                        "voices": [],
                        "service": "minimax"
                    }
            else:
                return {
                    "success": False,
                    "error": "MCP工具返回空结果",
                    "voices": [],
                    "service": "minimax"
                }
                
        except Exception as e:
            logger.error(f"获取MiniMax语音列表异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "voices": [],
                "service": "minimax"
            }
    
    async def _get_openai_voices(self) -> Dict[str, Any]:
        """获取OpenAI可用语音"""
        openai_voices = [
            {"name": "Alloy", "id": "alloy"},
            {"name": "Echo", "id": "echo"},
            {"name": "Fable", "id": "fable"},
            {"name": "Onyx", "id": "onyx"},
            {"name": "Nova", "id": "nova"},
            {"name": "Shimmer", "id": "shimmer"}
        ]
        
        return {
            "success": True,
            "voices": openai_voices,
            "service": "openai",
            "message": "获取OpenAI语音列表成功"
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "minimax": {
                "available": self.minimax_available,
                "api_key_configured": bool(self.minimax_api_key),
                "mcp_tools_available": MCP_AVAILABLE
            },
            "openai": {
                "available": self.openai_available,
                "api_key_configured": bool(self.openai_api_key)
            }
        }

# 创建全局服务实例
audio_service = AudioService()

# 导出
__all__ = ['AudioService', 'audio_service'] 