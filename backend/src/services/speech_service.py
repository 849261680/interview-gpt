"""
语音服务模块
集成多种语音识别和语音合成服务
支持OpenAI Whisper、Azure Speech、Google Speech等
"""
import asyncio
import io
import logging
import tempfile
import os
import wave
import json
import subprocess
import base64
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
from datetime import datetime
import aiohttp
import aiofiles

from ..config.settings import settings
from ..utils.exceptions import SpeechProcessingError
from .ai.ai_service_manager import ai_service_manager
# 导入新的 minimax_chat_service 模块
from .speech.minimax_chat_service import minimax_chat_service

# Import Pydantic models from the API layer for type hinting
if TYPE_CHECKING:
    from ..api.speech import ChatRequest, MinimaxChatCompletionResponse, MinimaxChoice, MinimaxResponseMessage, MinimaxUsage

# MCP imports - u6682u65f6u6ce8u91cau6389uff0cu53eau5b9eu73b0u6587u5b57u529fu80fd
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# u4f7fu7528u6a21u62dfu5b9eu73b0u66ffu4ee3

logger = logging.getLogger(__name__)


class SpeechService:
    """
    语音服务类
    提供语音识别和语音合成功能
    """
    
    def __init__(self):
        """初始化语音服务"""
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['wav', 'mp3', 'webm', 'ogg', 'm4a', 'flac']
        self.supported_languages = {
            'zh': 'zh-CN',
            'zh-CN': 'zh-CN', 
            'en': 'en-US',
            'en-US': 'en-US',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'es': 'es-ES'
        }
        
        # 初始化各种语音服务
        self._init_services()
    
    def _init_services(self):
        """初始化语音服务"""
        self.services = {
            'openai': {
                'available': bool(settings.OPENAI_API_KEY),
                'stt': True,
                'tts': True
            },
            'azure': {
                'available': bool(getattr(settings, 'AZURE_SPEECH_KEY', None)),
                'stt': True,
                'tts': True
            },
            'google': {
                'available': bool(settings.GOOGLE_APPLICATION_CREDENTIALS or settings.GOOGLE_SPEECH_CREDENTIALS_PATH),
                'stt': True,
                'tts': True
            },
            'minimax_mcp': {
                'available': bool(settings.MINIMAX_API_KEY and settings.MINIMAX_GROUP_ID),
                'stt': True,
                'tts': True
            },
            'browser': {
                'available': True,  # 浏览器原生支持
                'stt': False,  # 浏览器STT在前端处理
                'tts': True   # 可以生成SSML给浏览器
            }
        }
        
        self.logger.info(f"语音服务初始化完成: {self.services}")
        
        # 初始化可用的语音列表
        self.available_voices = {}
        # 暂时不在初始化时加载语音列表，因为需要异步调用
        # self._load_available_voices()
    
    def _validate_config(self):
        """验证配置"""
        if not self.services['minimax_mcp']['available']:
            logger.warning("MINIMAX_API_KEY 未设置，MiniMax MCP功能将不可用")
            self.services['minimax_mcp']['stt'] = False
        
        if not self.services['minimax_mcp']['available']:
            logger.warning("MINIMAX_GROUP_ID 未设置，MiniMax MCP功能将不可用")
            self.services['minimax_mcp']['stt'] = False
    
    async def _call_minimax_mcp_async(self, tool_name: str, arguments: dict) -> dict:
        """异步调用MiniMax MCP工具 - 处理语音相关功能"""
        # 此方法只处理文本到语音和语音到文本的功能
        # 聊天功能已经移至 minimax_chat_service 模块
        try:
            self.logger.info(f"模拟调用MiniMax MCP工具: {tool_name}, 参数: {arguments}")
            
            # 文字转语音功能，返回模拟数据
            if tool_name == "text_to_audio":
                # 创建临时音频文件
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file_path = temp_file.name
                temp_file.close()
                
                # 生成模拟音频URL
                audio_url = f"file://{temp_file_path}"
                
                return {
                    "success": True,
                    "result": f"Audio URL: {audio_url}"
                }
                
            elif tool_name == "list_voices":
                return {
                    "success": True,
                    "result": "可用语音: female-zhiyu, male-qingsong, female-shaonv"
                }

            # 其他工具的模拟响应
            return {
                "success": True,
                "result": "模拟响应：工具调用成功"
            }
        
        except Exception as e:
            self.logger.error(f"模拟MCP调用失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'minimax_mcp': {
                'enabled': self.services['minimax_mcp']['available'],
                'api_configured': bool(settings.MINIMAX_API_KEY),
                'available_voices': len(self.available_voices.get('minimax_mcp', [])) if 'minimax_mcp' in self.available_voices else 0
            }
        }
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "zh",
        audio_format: str = "webm"
    ) -> Dict[str, Any]:
        """
        语音转文字
        
        Args:
            audio_data: 音频数据
            language: 语言代码
            audio_format: 音频格式
            
        Returns:
            Dict: 识别结果
            
        Raises:
            SpeechProcessingError: 处理失败时抛出
        """
        try:
            self.logger.info(f"开始语音识别，格式: {audio_format}, 语言: {language}")
            
            # 验证输入
            if not audio_data:
                raise SpeechProcessingError("音频数据为空")
            
            if audio_format not in self.supported_formats:
                raise SpeechProcessingError(f"不支持的音频格式: {audio_format}")
            
            # 标准化语言代码
            normalized_language = self.supported_languages.get(language, language)
            
            # 尝试不同的语音识别服务
            result = None
            errors = []
            
            # 优先使用MiniMax MCP（如果可用）
            if self.services['minimax_mcp']['available'] and self.services['minimax_mcp']['stt']:
                try:
                    result = await self._minimax_mcp_speech_to_text(audio_data, normalized_language, audio_format)
                    self.logger.info("MiniMax MCP识别成功")
                except Exception as e:
                    error_msg = f"MiniMax MCP识别失败: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            # 如果MiniMax MCP失败，尝试OpenAI Whisper
            if not result and self.services['openai']['available'] and self.services['openai']['stt']:
                try:
                    result = await self._openai_speech_to_text(audio_data, normalized_language, audio_format)
                    self.logger.info("OpenAI Whisper识别成功")
                except Exception as e:
                    error_msg = f"OpenAI Whisper识别失败: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            # 如果OpenAI失败，尝试Google Speech
            if not result and self.services['google']['available'] and self.services['google']['stt']:
                try:
                    result = await self._google_speech_to_text(audio_data, normalized_language, audio_format)
                    self.logger.info("Google Speech识别成功")
                except Exception as e:
                    error_msg = f"Google Speech识别失败: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            # 如果Google Speech失败，尝试Azure
            if not result and self.services['azure']['available'] and self.services['azure']['stt']:
                try:
                    result = await self._azure_speech_to_text(audio_data, normalized_language, audio_format)
                    self.logger.info("Azure Speech识别成功")
                except Exception as e:
                    error_msg = f"Azure Speech识别失败: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            # 如果都失败，使用本地模拟识别
            if not result:
                self.logger.warning("所有语音识别服务都失败，使用模拟识别")
                result = await self._fallback_speech_to_text(audio_data, normalized_language)
            
            # 添加元数据
            result.update({
                "timestamp": datetime.now().isoformat(),
                "service_errors": errors if errors else None
            })
            
            return result
            
        except Exception as e:
            error_msg = f"语音识别失败: {str(e)}"
            self.logger.error(error_msg)
            raise SpeechProcessingError(error_msg)
    
    async def _minimax_mcp_speech_to_text(
        self,
        audio_data: bytes,
        language: str,
        audio_format: str
    ) -> Dict[str, Any]:
        """使用MiniMax MCP进行语音识别"""
        try:
            # 注意：MiniMax MCP目前主要支持TTS，ASR功能可能有限
            # 这里我们先实现一个基础版本
            
            # 将音频数据编码为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 调用MiniMax MCP
            arguments = {
                "audio_data": audio_base64,
                "format": audio_format,
                "language": language
            }
            
            result = await self._call_minimax_mcp_async("speech_to_text", arguments)
            
            # 计算音频时长
            duration = self._estimate_audio_duration(audio_data, audio_format)
            
            return {
                "text": result.get("result", ""),
                "confidence": 0.8,
                "language": language,
                "duration": duration,
                "service": "minimax_mcp"
            }
                        
        except Exception as e:
            raise SpeechProcessingError(f"MiniMax MCP识别失败: {e}")
    
    async def _openai_speech_to_text(
        self,
        audio_data: bytes,
        language: str,
        audio_format: str
    ) -> Dict[str, Any]:
        """使用OpenAI Whisper进行语音识别"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # 使用AI服务管理器调用OpenAI
                # 这里需要特殊处理，因为Whisper API需要文件上传
                import openai
                
                client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                
                with open(temp_file_path, 'rb') as audio_file:
                    transcript = await client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language.split('-')[0],  # whisper只需要语言代码，不需要地区
                        response_format="verbose_json"
                    )
                
                # 计算音频时长
                duration = self._estimate_audio_duration(audio_data, audio_format)
                
                return {
                    "text": transcript.text,
                    "confidence": 0.9,  # Whisper不提供置信度，使用默认值
                    "language": language,
                    "duration": duration,
                    "service": "openai_whisper"
                }
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise SpeechProcessingError(f"OpenAI Whisper识别失败: {e}")
    
    async def _google_speech_to_text(
        self,
        audio_data: bytes,
        language: str,
        audio_format: str
    ) -> Dict[str, Any]:
        """使用Google Speech进行语音识别"""
        try:
            from google.cloud import speech
            import asyncio
            import tempfile
            import os
            
            # 设置认证
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
            elif settings.GOOGLE_SPEECH_CREDENTIALS_PATH:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_SPEECH_CREDENTIALS_PATH
            
            # 创建客户端
            client = speech.SpeechClient()
            
            # 音频格式映射
            format_mapping = {
                'wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
                'webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                'mp3': speech.RecognitionConfig.AudioEncoding.MP3,
                'flac': speech.RecognitionConfig.AudioEncoding.FLAC,
                'ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                'm4a': speech.RecognitionConfig.AudioEncoding.MP3  # 近似处理
            }
            
            # 语言代码映射
            language_mapping = {
                'zh-CN': 'zh-CN',
                'zh': 'zh-CN',
                'en-US': 'en-US', 
                'en': 'en-US',
                'ja-JP': 'ja-JP',
                'ja': 'ja-JP',
                'ko-KR': 'ko-KR',
                'ko': 'ko-KR',
                'fr-FR': 'fr-FR',
                'fr': 'fr-FR',
                'de-DE': 'de-DE',
                'de': 'de-DE',
                'es-ES': 'es-ES',
                'es': 'es-ES'
            }
            
            # 获取音频编码格式
            encoding = format_mapping.get(audio_format, speech.RecognitionConfig.AudioEncoding.LINEAR16)
            
            # 获取语言代码
            google_language = language_mapping.get(language, 'zh-CN')
            
            # 配置识别参数
            config = speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=16000,  # 默认采样率
                language_code=google_language,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
                model='latest_long'  # 使用最新的长音频模型
            )
            
            # 创建音频对象
            audio = speech.RecognitionAudio(content=audio_data)
            
            # 执行识别（在线程池中运行同步代码）
            def recognize_sync():
                return client.recognize(config=config, audio=audio)
            
            # 异步执行
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, recognize_sync)
            
            # 处理结果
            if response.results:
                # 获取最佳识别结果
                result = response.results[0]
                alternative = result.alternatives[0]
                
                # 计算音频时长
                duration = self._estimate_audio_duration(audio_data, audio_format)
                
                return {
                    "text": alternative.transcript,
                    "confidence": alternative.confidence if hasattr(alternative, 'confidence') else 0.9,
                    "language": google_language,
                    "duration": duration,
                    "service": "google_speech",
                    "alternatives": [
                        {
                            "transcript": alt.transcript,
                            "confidence": alt.confidence if hasattr(alt, 'confidence') else 0.0
                        }
                        for alt in result.alternatives[:3]  # 返回前3个候选结果
                    ]
                }
            else:
                # 没有识别结果
                self.logger.warning("Google Speech没有返回识别结果")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": google_language,
                    "duration": self._estimate_audio_duration(audio_data, audio_format),
                    "service": "google_speech",
                    "error": "no_results"
                }
                
        except ImportError:
            raise SpeechProcessingError("Google Cloud Speech库未安装，请运行: pip install google-cloud-speech")
        except Exception as e:
            self.logger.error(f"Google Speech API调用失败: {e}")
            raise SpeechProcessingError(f"Google Speech识别失败: {e}")
    
    async def _azure_speech_to_text(
        self,
        audio_data: bytes,
        language: str,
        audio_format: str
    ) -> Dict[str, Any]:
        """使用Azure Speech进行语音识别"""
        try:
            # Azure Speech API实现
            # 这里是示例实现，实际需要Azure Speech SDK
            
            # 模拟Azure识别结果
            duration = self._estimate_audio_duration(audio_data, audio_format)
            
            return {
                "text": "这是Azure Speech识别的模拟结果",
                "confidence": 0.85,
                "language": language,
                "duration": duration,
                "service": "azure_speech"
            }
            
        except Exception as e:
            raise SpeechProcessingError(f"Azure Speech识别失败: {e}")
    
    async def _fallback_speech_to_text(
        self,
        audio_data: bytes,
        language: str
    ) -> Dict[str, Any]:
        """降级语音识别实现"""
        try:
            # 计算音频时长
            duration = self._estimate_audio_duration(audio_data, "webm")
            
            # 根据语言返回不同的模拟文本
            if language.startswith('zh'):
                text = "这是语音识别的模拟结果，实际项目中请配置真实的语音识别服务。"
            else:
                text = "This is a simulated speech recognition result. Please configure real speech recognition service in production."
            
            return {
                "text": text,
                "confidence": 0.7,
                "language": language,
                "duration": duration,
                "service": "fallback"
            }
            
        except Exception as e:
            raise SpeechProcessingError(f"降级语音识别失败: {e}")
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "zh-CN",
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0
    ) -> Dict[str, Any]:
        """
        文字转语音
        
        Args:
            text: 要转换的文本
            language: 语言代码
            voice: 语音类型
            speed: 语速
            pitch: 音调
            volume: 音量
            
        Returns:
            Dict: 语音合成结果
            
        Raises:
            SpeechProcessingError: 处理失败时抛出
        """
        try:
            self.logger.info(f"开始语音合成，文本长度: {len(text)}")
            
            # 验证输入
            if not text.strip():
                raise SpeechProcessingError("文本内容为空")
            
            # 标准化语言代码
            normalized_language = self.supported_languages.get(language, language)
            
            # 尝试不同的语音合成服务
            result = None
            errors = []
            
            # 优先使用MiniMax MCP（如果可用）
            if self.services['minimax_mcp']['available'] and self.services['minimax_mcp']['tts']:
                try:
                    result = await self._minimax_mcp_text_to_speech(text, normalized_language, voice, speed)
                    self.logger.info("MiniMax MCP合成成功")
                except Exception as e:
                    error_msg = f"MiniMax MCP合成失败: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            # 如果MiniMax MCP失败，尝试OpenAI TTS
            if not result and self.services['openai']['available'] and self.services['openai']['tts']:
                try:
                    result = await self._openai_text_to_speech(text, normalized_language, voice, speed)
                    self.logger.info("OpenAI TTS合成成功")
                except Exception as e:
                    error_msg = f"OpenAI TTS合成失败: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            # 如果OpenAI失败，尝试Azure
            if not result and self.services['azure']['available'] and self.services['azure']['tts']:
                try:
                    result = await self._azure_text_to_speech(text, normalized_language, voice, speed, pitch, volume)
                    self.logger.info("Azure Speech合成成功")
                except Exception as e:
                    error_msg = f"Azure Speech合成失败: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            # 如果都失败，生成SSML给浏览器处理
            if not result:
                self.logger.warning("所有语音合成服务都失败，生成SSML")
                result = await self._generate_ssml_for_browser(text, normalized_language, voice, speed, pitch, volume)
            
            # 添加元数据
            result.update({
                "timestamp": datetime.now().isoformat(),
                "service_errors": errors if errors else None
            })
            
            return result
            
        except Exception as e:
            error_msg = f"语音合成失败: {str(e)}"
            self.logger.error(error_msg)
            raise SpeechProcessingError(error_msg)
    
    async def _minimax_mcp_text_to_speech(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float
    ) -> Dict[str, Any]:
        """使用MiniMax MCP进行语音合成"""
        # 创建唯一请求ID，帮助跟踪日志
        request_id = f"mcp_tts_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(text)[:8]}"
        
        try:
            self.logger.info(f"[{request_id}] 开始 MiniMax MCP 语音合成, 文本长度: {len(text)}, 语音: {voice}, 语言: {language}")
            self.logger.debug(f"[{request_id}] 合成文本内容预览: '{text[:50]}...'")
            
            # 根据语言和面试官类型选择语音
            voice_mapping = {
                "technical": "male-qn-qingse",
                "hr": "female-shaonv", 
                "product": "audiobook_female_1",
                "general": "Charming_Lady",
                "system": "female-tianmei"
            }
            
            # 如果没有指定语音，使用默认语音
            original_voice = voice
            if not voice:
                voice = "female-shaonv"
                self.logger.debug(f"[{request_id}] 未指定语音，使用默认语音: {voice}")
            elif voice in voice_mapping:
                voice = voice_mapping[voice]
                self.logger.debug(f"[{request_id}] 将面试官类型 '{original_voice}' 映射到语音ID: {voice}")
            
            # 创建临时输出目录
            output_dir = tempfile.mkdtemp()
            self.logger.debug(f"[{request_id}] 创建临时输出目录: {output_dir}")
            
            # 调用MiniMax MCP
            arguments = {
                "text": text,
                "voice_id": voice,
                "model": "speech-02-hd",
                "speed": speed,
                "vol": 1.0,
                "pitch": 0,
                "emotion": "happy",
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "output_directory": output_dir
            }
            
            self.logger.info(f"[{request_id}] 调用 MiniMax MCP text_to_audio API，参数: {arguments}")
            
            # 捕获调用时间和异常
            start_time = datetime.now()
            try:
                result = await self._call_minimax_mcp_async("text_to_audio", arguments)
                api_duration = (datetime.now() - start_time).total_seconds()
                self.logger.debug(f"[{request_id}] MCP API调用时间: {api_duration:.2f}秒")
            except Exception as mcp_error:
                api_duration = (datetime.now() - start_time).total_seconds()
                self.logger.error(f"[{request_id}] MCP API调用失败: {mcp_error}, 耗时: {api_duration:.2f}秒")
                raise mcp_error  # 重新抛出异常以触发外层处理
            
            # 记录API响应详情
            self.logger.debug(f"[{request_id}] MCP API响应: {result}")
            
            if result.get("success"):
                result_text = result.get("result", "")
                self.logger.debug(f"[{request_id}] 成功响应文本: {result_text[:200]}...")
                
                # 检查是否返回了XML/SSML格式数据
                if result_text.strip().startswith("<speak") or "<speak version" in result_text:
                    self.logger.warning(f"[{request_id}] MCP返回了SSML格式数据，这可能导致前端处理错误")
                    self.logger.debug(f"[{request_id}] SSML数据: {result_text[:500]}...")
                    
                    # 返回原始响应文本，并标记其内容类型
                    return {
                        "response_text": result_text,
                        "content_type": "application/xml",  # 正确标记XML/SSML类型
                        "format": "xml",
                        "duration": 0,
                        "service": "minimax_mcp",
                        "voice_name": voice,
                        "method": "mcp_client"
                    }
                
                # 解析音频URL
                if "Audio URL:" in result_text:
                    audio_url = result_text.split("Audio URL:")[-1].strip()
                    self.logger.info(f"[{request_id}] 提取到音频URL: {audio_url}")
                    
                    # 下载音频文件
                    download_start = datetime.now()
                    self.logger.debug(f"[{request_id}] 开始下载音频文件...")
                    
                    audio_file_path = await self._download_audio_from_url(audio_url, output_dir)
                    download_duration = (datetime.now() - download_start).total_seconds()
                    
                    # 检查文件大小和类型
                    if os.path.exists(audio_file_path):
                        file_size = os.path.getsize(audio_file_path)
                        file_type = "未知"
                        
                        # 试图读取文件头部信息识别文件类型
                        try:
                            with open(audio_file_path, 'rb') as f:
                                header = f.read(12)  # 读取前12个字节
                                header_hex = header.hex()
                                if header_hex.startswith('494433') or header_hex.startswith('fffb'): 
                                    file_type = 'MP3'
                                elif header_hex.startswith('52494646'): 
                                    file_type = 'WAV'
                                elif header_hex.startswith('4f676753'): 
                                    file_type = 'OGG'
                        except Exception as e:
                            self.logger.debug(f"[{request_id}] 无法识别文件类型: {e}")
                        
                        self.logger.info(f"[{request_id}] 下载完成，文件路径: {audio_file_path}, 大小: {file_size}字节, 类型: {file_type}, 耗时: {download_duration:.2f}秒")
                    else:
                        self.logger.error(f"[{request_id}] 下载失败，文件不存在: {audio_file_path}")
                    
                    # 估算时长
                    duration = len(text) / 10 / speed  # 粗略估算
                    
                    # 构造返回结果
                    response_data = {
                        "audio_file_path": audio_file_path,
                        "audio_url": audio_url,
                        "format": "mp3",
                        "duration": duration,
                        "service": "minimax_mcp",
                        "voice_name": voice,
                        "method": "mcp_client"
                    }
                    
                    self.logger.debug(f"[{request_id}] 返回结果: {response_data}")
                    return response_data
                else:
                    error_msg = f"无法从 MCP结果中提取音频URL: {result_text}"
                    self.logger.error(f"[{request_id}] {error_msg}")
                    raise Exception(error_msg)
            else:
                error_msg = f"MCP调用失败: {result.get('error', '未知错误')}"
                self.logger.error(f"[{request_id}] {error_msg}")
                raise Exception(error_msg)
                        
        except Exception as e:
            self.logger.error(f"[{request_id}] MiniMax MCP合成失败: {e}")
            import traceback
            self.logger.debug(f"[{request_id}] 错误堆栈: {traceback.format_exc()}")
            raise SpeechProcessingError(f"MiniMax MCP合成失败: {e}")
    
    async def _download_audio_from_url(self, audio_url: str, output_dir: str) -> str:
        """从URL下载音频文件"""
        try:
            import aiohttp
            import os
            
            # 生成本地文件名
            file_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            file_path = os.path.join(output_dir, file_name)
            
            # 下载文件
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        self.logger.info(f"音频文件下载成功: {file_path}")
                        return file_path
                    else:
                        raise Exception(f"下载失败，状态码: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"下载音频文件失败: {e}")
            raise
    
    async def _openai_text_to_speech(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float
    ) -> Dict[str, Any]:
        """使用OpenAI TTS进行语音合成"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # 选择合适的语音
            if not voice:
                voice = "alloy" if language.startswith('en') else "nova"
            
            # 调用OpenAI TTS API
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            
            # 获取音频数据
            audio_data = response.content
            
            # 估算时长
            duration = len(text) / 10 / speed  # 粗略估算
            
            return {
                "audio_data": audio_data,
                "format": "mp3",
                "duration": duration,
                "service": "openai_tts"
            }
            
        except Exception as e:
            raise SpeechProcessingError(f"OpenAI TTS合成失败: {e}")
    
    async def _azure_text_to_speech(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float,
        pitch: float,
        volume: float
    ) -> Dict[str, Any]:
        """使用Azure Speech进行语音合成"""
        try:
            # Azure Speech API实现
            # 这里是示例实现，实际需要Azure Speech SDK
            
            # 生成模拟音频数据
            duration = len(text) / 10 / speed
            audio_data = self._generate_mock_audio(duration)
            
            return {
                "audio_data": audio_data,
                "format": "wav",
                "duration": duration,
                "service": "azure_speech"
            }
            
        except Exception as e:
            raise SpeechProcessingError(f"Azure Speech合成失败: {e}")
    
    async def _generate_ssml_for_browser(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float,
        pitch: float,
        volume: float
    ) -> Dict[str, Any]:
        """生成SSML给浏览器处理"""
        try:
            # 生成SSML标记
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
                <prosody rate="{speed}" pitch="{pitch}" volume="{volume}">
                    {text}
                </prosody>
            </speak>
            """
            
            # 估算时长
            duration = len(text) / 10 / speed
            
            # 返回SSML数据（编码为字节）
            return {
                "audio_data": ssml.encode('utf-8'),
                "format": "ssml",
                "duration": duration,
                "service": "browser_ssml"
            }
            
        except Exception as e:
            raise SpeechProcessingError(f"SSML生成失败: {e}")
    
    def _generate_mock_audio(self, duration: float) -> bytes:
        """生成模拟音频数据"""
        try:
            # 生成简单的WAV文件头和静音数据
            sample_rate = 44100
            samples = int(sample_rate * duration)
            
            # 创建WAV文件
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16位
                wav_file.setframerate(sample_rate)
                
                # 写入静音数据
                silence = b'\x00\x00' * samples
                wav_file.writeframes(silence)
            
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"生成模拟音频失败: {e}")
            return b''
    
    def _estimate_audio_duration(self, audio_data: bytes, audio_format: str) -> float:
        """估算音频时长"""
        try:
            # 简单的时长估算，基于文件大小
            # 实际项目中应该使用音频库来获取准确时长
            
            if audio_format in ['mp3', 'webm', 'ogg']:
                # 压缩格式，估算比特率
                estimated_bitrate = 128000  # 128 kbps
                duration = (len(audio_data) * 8) / estimated_bitrate
            else:
                # 未压缩格式，假设44.1kHz 16bit 单声道
                sample_rate = 44100
                bytes_per_sample = 2
                duration = len(audio_data) / (sample_rate * bytes_per_sample)
            
            return max(duration, 0.1)  # 最少0.1秒
            
        except Exception:
            return 1.0  # 默认1秒
    
    async def get_available_voices(self) -> Dict[str, List[str]]:
        """
        获取可用的语音列表
        
        Returns:
            按服务分组的语音列表
        """
        return self.available_voices
    
    async def get_supported_languages(self) -> List[Dict[str, Any]]:
        """获取支持的语言列表"""
        try:
            languages = [
                {"code": "zh-CN", "name": "中文（简体）", "native_name": "中文"},
                {"code": "en-US", "name": "English (US)", "native_name": "English"},
                {"code": "ja-JP", "name": "Japanese", "native_name": "日本語"},
                {"code": "ko-KR", "name": "Korean", "native_name": "한국어"},
                {"code": "fr-FR", "name": "French", "native_name": "Français"},
                {"code": "de-DE", "name": "German", "native_name": "Deutsch"},
                {"code": "es-ES", "name": "Spanish", "native_name": "Español"}
            ]
            
            return languages
            
        except Exception as e:
            self.logger.error(f"获取语言列表失败: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """语音服务健康检查"""
        try:
            service_status = {}
            
            # 检查各个服务的可用性
            for service_name, service_info in self.services.items():
                try:
                    if service_name == 'openai' and service_info['available']:
                        # 检查OpenAI API
                        status = await self._check_openai_health()
                    elif service_name == 'azure' and service_info['available']:
                        # 检查Azure Speech
                        status = await self._check_azure_health()
                    elif service_name == 'google' and service_info['available']:
                        # 检查Google Speech
                        status = await self._check_google_health()
                    elif service_name == 'minimax_mcp' and service_info['available']:
                        # 检查MiniMax MCP
                        status = await self._check_minimax_mcp_health()
                    elif service_name == 'browser':
                        # 浏览器服务总是可用
                        status = True
                    else:
                        status = service_info['available']
                    
                    service_status[service_name] = {
                        "available": status,
                        "stt": service_info['stt'] and status,
                        "tts": service_info['tts'] and status
                    }
                    
                except Exception as e:
                    self.logger.warning(f"检查{service_name}服务健康状态失败: {e}")
                    service_status[service_name] = {
                        "available": False,
                        "stt": False,
                        "tts": False,
                        "error": str(e)
                    }
            
            # 判断整体可用性
            any_available = any(s.get('available', False) for s in service_status.values())
            
            return {
                "available": any_available,
                "services": service_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"语音服务健康检查失败: {e}")
            return {
                "available": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_openai_health(self) -> bool:
        """检查OpenAI服务健康状态"""
        try:
            # 简单的API可用性检查
            if not settings.OPENAI_API_KEY:
                return False
            
            # 这里可以添加实际的API调用测试
            return True
            
        except Exception:
            return False
    
    async def _check_azure_health(self) -> bool:
        """检查Azure Speech服务健康状态"""
        try:
            # 检查Azure Speech配置
            azure_key = getattr(settings, 'AZURE_SPEECH_KEY', None)
            azure_region = getattr(settings, 'AZURE_SPEECH_REGION', None)
            
            return bool(azure_key and azure_region)
            
        except Exception:
            return False
    
    async def _check_google_health(self) -> bool:
        """检查Google Speech服务健康状态"""
        try:
            # 检查Google Speech配置
            google_credentials = settings.GOOGLE_APPLICATION_CREDENTIALS or settings.GOOGLE_SPEECH_CREDENTIALS_PATH
            return bool(google_credentials)
            
        except Exception:
            return False
    
    async def _check_minimax_mcp_health(self) -> bool:
        """检查MiniMax MCP服务健康状态"""
        try:
            # 检查环境变量
            if not (settings.MINIMAX_API_KEY and settings.MINIMAX_GROUP_ID):
                return False
            
            # 尝试调用list_voices来测试连接
            result = await self._call_minimax_mcp_async("list_voices", {})
            return result.get("success", False)
            
        except Exception as e:
            self.logger.warning(f"MiniMax MCP健康检查失败: {e}")
            return False

    async def minimax_chat_completion(self, request: 'ChatRequest') -> 'MinimaxChatCompletionResponse':
        """
        Handles chat completion using MiniMax MCP.
        This method will call the MiniMax service (via minimax_chat_service)
        and format the response.
        """
        self.logger.info(f"SpeechService: minimax_chat_completion called with model {request.model}")
        self.logger.debug(f"SpeechService: Full request: {request.model_dump_json(indent=2)}")

        # 委托给专门的 minimax_chat_service 模块处理
        return await minimax_chat_service.chat_completion(request)


# 创建全局语音服务实例
speech_service = SpeechService() 