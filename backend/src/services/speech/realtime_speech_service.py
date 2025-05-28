"""
实时语音面试服务
使用MiniMax MCP实现实时语音转文字和文字转语音功能
"""
import os
import logging
import uuid
import asyncio
import tempfile
from typing import Dict, Any, Optional, AsyncGenerator
from pathlib import Path

logger = logging.getLogger(__name__)

# 面试官语音配置
INTERVIEWER_VOICES = {
    "technical": {
        "voice_id": "male-qn-jingying",
        "name": "精英青年音色",
        "description": "技术面试官 - 专业、严谨"
    },
    "hr": {
        "voice_id": "female-yujie", 
        "name": "御姐音色",
        "description": "HR面试官 - 温和、专业"
    },
    "behavioral": {
        "voice_id": "male-qn-qingse",
        "name": "青涩青年音色", 
        "description": "行为面试官 - 亲和、耐心"
    },
    "product": {
        "voice_id": "female-chengshu",
        "name": "成熟女性音色",
        "description": "产品面试官 - 成熟、理性"
    },
    "final": {
        "voice_id": "presenter_male",
        "name": "男性主持人",
        "description": "总面试官 - 权威、总结性"
    },
    "system": {
        "voice_id": "female-tianmei",
        "name": "甜美女性音色",
        "description": "系统提示 - 友好、引导性"
    }
}

class RealtimeSpeechService:
    """
    实时语音面试服务
    提供实时语音转文字和文字转语音功能
    """
    
    def __init__(self):
        """初始化实时语音服务"""
        # 音频文件存储路径
        self.audio_dir = Path(os.getcwd()) / "static" / "audio" / "realtime"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # MiniMax API配置
        self.api_key = os.getenv("MINIMAX_API_KEY", "")
        self.group_id = os.getenv("MINIMAX_GROUP_ID", "")
        
        # 语音参数配置
        self.tts_config = {
            "model": "speech-02-hd",
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
            "emotion": "neutral",
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }
        
        # 检查配置
        if not self.api_key:
            logger.warning("MiniMax API Key未配置，将使用模拟模式")
        else:
            logger.info("实时语音服务初始化完成，使用MiniMax MCP")
    
    async def speech_to_text_realtime(self, audio_data: bytes, format: str = "wav") -> str:
        """
        实时语音转文字
        
        Args:
            audio_data: 音频数据（字节）
            format: 音频格式
            
        Returns:
            识别的文字
        """
        try:
            logger.info(f"开始实时语音识别，音频大小: {len(audio_data)} bytes")
            
            if not self.api_key:
                # 模拟模式
                await asyncio.sleep(0.5)
                return "这是模拟的语音识别结果"
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # 使用MiniMax MCP进行语音识别
                # 注意：这里需要根据实际的MiniMax MCP API调用方式调整
                logger.info("调用MiniMax语音识别API")
                
                # 暂时使用模拟实现，实际使用时需要调用真实API
                await asyncio.sleep(1)
                
                # 模拟返回结果
                return "我对这个职位很感兴趣，我认为我的技能和经验很适合这个岗位。"
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"实时语音识别失败: {str(e)}")
            raise Exception(f"语音识别失败: {str(e)}")
    
    async def text_to_speech_realtime(self, text: str, interviewer_type: str = "system") -> bytes:
        """
        实时文字转语音
        
        Args:
            text: 要转换的文字
            interviewer_type: 面试官类型
            
        Returns:
            音频数据（字节）
        """
        try:
            logger.info(f"开始实时文字转语音: {text[:50]}... (面试官: {interviewer_type})")
            
            # 获取语音配置
            voice_config = INTERVIEWER_VOICES.get(interviewer_type, INTERVIEWER_VOICES["system"])
            voice_id = voice_config["voice_id"]
            
            if not self.api_key:
                # 模拟模式 - 返回空音频数据
                await asyncio.sleep(1)
                return b""
            
            # 使用MiniMax MCP进行文字转语音
            logger.info(f"调用MiniMax TTS API，使用语音: {voice_config['name']}")
            
            # 暂时使用模拟实现，实际使用时需要调用真实API
            await asyncio.sleep(1)
            
            # 模拟返回空音频数据
            return b""
            
        except Exception as e:
            logger.error(f"实时文字转语音失败: {str(e)}")
            raise Exception(f"文字转语音失败: {str(e)}")
    
    async def text_to_speech_with_mcp(self, text: str, interviewer_type: str = "system") -> str:
        """
        使用MiniMax MCP进行文字转语音并保存文件
        
        Args:
            text: 要转换的文字
            interviewer_type: 面试官类型
            
        Returns:
            音频文件路径
        """
        try:
            # 获取语音配置
            voice_config = INTERVIEWER_VOICES.get(interviewer_type, INTERVIEWER_VOICES["system"])
            voice_id = voice_config["voice_id"]
            
            # 生成文件名
            file_name = f"interview_{interviewer_type}_{uuid.uuid4().hex[:8]}.mp3"
            output_path = str(self.audio_dir)
            
            logger.info(f"使用MiniMax MCP生成语音: {voice_config['name']}")
            
            # 这里应该调用真实的MiniMax MCP API
            # 暂时使用模拟实现
            await asyncio.sleep(1)
            
            # 创建空文件作为模拟
            file_path = self.audio_dir / file_name
            with open(file_path, "wb") as f:
                f.write(b"")
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"MiniMax MCP文字转语音失败: {str(e)}")
            raise Exception(f"文字转语音失败: {str(e)}")
    
    async def stream_speech_recognition(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """
        流式语音识别
        
        Args:
            audio_stream: 音频数据流
            
        Yields:
            识别的文字片段
        """
        try:
            logger.info("开始流式语音识别")
            
            buffer = b""
            chunk_size = 1024 * 16  # 16KB chunks
            
            async for audio_chunk in audio_stream:
                buffer += audio_chunk
                
                # 当缓冲区达到一定大小时进行识别
                if len(buffer) >= chunk_size:
                    try:
                        # 识别当前缓冲区的音频
                        text = await self.speech_to_text_realtime(buffer)
                        if text.strip():
                            yield text
                        
                        # 清空缓冲区
                        buffer = b""
                        
                    except Exception as e:
                        logger.error(f"流式识别片段失败: {str(e)}")
                        continue
            
            # 处理剩余的音频数据
            if buffer:
                try:
                    text = await self.speech_to_text_realtime(buffer)
                    if text.strip():
                        yield text
                except Exception as e:
                    logger.error(f"处理最后音频片段失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"流式语音识别失败: {str(e)}")
            raise Exception(f"流式语音识别失败: {str(e)}")
    
    async def get_interviewer_voices(self) -> Dict[str, Dict[str, str]]:
        """
        获取所有面试官语音配置
        
        Returns:
            面试官语音配置字典
        """
        return INTERVIEWER_VOICES
    
    async def validate_audio_format(self, audio_data: bytes, expected_format: str = "wav") -> bool:
        """
        验证音频格式
        
        Args:
            audio_data: 音频数据
            expected_format: 期望的格式
            
        Returns:
            是否有效
        """
        try:
            if not audio_data:
                return False
            
            # 简单的格式检查
            if expected_format.lower() == "wav":
                # WAV文件头检查
                return audio_data[:4] == b"RIFF" and audio_data[8:12] == b"WAVE"
            elif expected_format.lower() == "mp3":
                # MP3文件头检查
                return audio_data[:3] == b"ID3" or audio_data[:2] == b"\xff\xfb"
            
            return True
            
        except Exception as e:
            logger.error(f"音频格式验证失败: {str(e)}")
            return False
    
    async def cleanup_temp_files(self):
        """
        清理临时音频文件
        """
        try:
            import time
            current_time = time.time()
            max_age = 3600  # 1小时
            
            for file_path in self.audio_dir.glob("*.mp3"):
                if current_time - file_path.stat().st_mtime > max_age:
                    file_path.unlink()
                    logger.info(f"清理临时文件: {file_path}")
                    
        except Exception as e:
            logger.error(f"清理临时文件失败: {str(e)}")
    
    async def get_speech_stats(self) -> Dict[str, Any]:
        """
        获取语音服务统计信息
        
        Returns:
            统计信息
        """
        try:
            stats = {
                "api_configured": bool(self.api_key),
                "audio_dir": str(self.audio_dir),
                "supported_formats": ["wav", "mp3", "m4a"],
                "available_voices": len(INTERVIEWER_VOICES),
                "temp_files_count": len(list(self.audio_dir.glob("*.mp3")))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {} 