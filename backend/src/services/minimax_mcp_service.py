"""
MiniMax MCP 服务集成
基于官方 MiniMax MCP 工具实现文字转语音功能
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile
import subprocess
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class MinimaxMCPService:
    """MiniMax MCP 服务类"""
    
    def __init__(self):
        self.api_key = os.getenv('MINIMAX_API_KEY')
        self.api_host = os.getenv('MINIMAX_API_HOST', 'https://api.minimax.chat')
        self.base_path = os.getenv('MINIMAX_MCP_BASE_PATH', '~/Desktop')
        self.resource_mode = os.getenv('MINIMAX_API_RESOURCE_MODE', 'url')
        
        # 验证必需的环境变量
        if not self.api_key:
            logger.warning("MINIMAX_API_KEY 未设置，MiniMax MCP 功能将不可用")
            self.available = False
        else:
            self.available = True
            logger.info("MiniMax MCP 服务初始化成功")
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.available
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: str = "female-shaonv",
        model: str = "speech-02-hd",
        speed: float = 1.0,
        vol: float = 1.0,
        pitch: int = 0,
        emotion: str = "happy",
        sample_rate: int = 32000,
        bitrate: int = 128000,
        channel: int = 1,
        format: str = "mp3",
        language_boost: str = "auto",
        output_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用 MiniMax MCP 工具进行文字转语音
        
        Args:
            text: 要转换的文本
            voice_id: 语音ID，默认为 "female-shaonv"
            model: 模型名称，默认为 "speech-02-hd"
            speed: 语速，范围 0.5-2.0，默认 1.0
            vol: 音量，范围 0-10，默认 1.0
            pitch: 音调，范围 -12到12，默认 0
            emotion: 情感，可选值见文档，默认 "happy"
            sample_rate: 采样率，默认 32000
            bitrate: 比特率，默认 128000
            channel: 声道数，默认 1
            format: 音频格式，默认 "mp3"
            language_boost: 语言增强，默认 "auto"
            output_directory: 输出目录，可选
            
        Returns:
            包含音频文件路径或URL的字典
        """
        if not self.available:
            raise Exception("MiniMax MCP 服务不可用，请检查 API 密钥配置")
        
        try:
            # 准备MCP工具调用参数
            mcp_args = {
                "text": text,
                "voice_id": voice_id,
                "model": model,
                "speed": speed,
                "vol": vol,
                "pitch": pitch,
                "emotion": emotion,
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "channel": channel,
                "format": format,
                "language_boost": language_boost
            }
            
            if output_directory:
                mcp_args["output_directory"] = output_directory
            
            # 调用MCP工具
            result = await self._call_mcp_tool("text_to_audio", mcp_args)
            
            if result.get("success"):
                return {
                    "success": True,
                    "audio_url": result.get("audio_url"),
                    "audio_path": result.get("audio_path"),
                    "voice_used": voice_id,
                    "message": result.get("message", "语音合成成功")
                }
            else:
                raise Exception(f"MCP工具调用失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"MiniMax TTS 失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"语音合成失败: {str(e)}"
            }
    
    async def list_voices(self, voice_type: str = "all") -> Dict[str, Any]:
        """
        获取可用的语音列表
        
        Args:
            voice_type: 语音类型，可选 "all", "system", "voice_cloning"
            
        Returns:
            包含语音列表的字典
        """
        if not self.available:
            raise Exception("MiniMax MCP 服务不可用")
        
        try:
            result = await self._call_mcp_tool("list_voices", {"voice_type": voice_type})
            
            if result.get("success"):
                return {
                    "success": True,
                    "voices": result.get("voices", []),
                    "message": "获取语音列表成功"
                }
            else:
                raise Exception(f"获取语音列表失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"获取语音列表失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"获取语音列表失败: {str(e)}"
            }
    
    async def _call_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用 MiniMax MCP 工具
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            
        Returns:
            工具调用结果
        """
        try:
            # 设置环境变量
            env = os.environ.copy()
            env.update({
                'MINIMAX_API_KEY': self.api_key,
                'MINIMAX_API_HOST': self.api_host,
                'MINIMAX_MCP_BASE_PATH': self.base_path,
                'MINIMAX_API_RESOURCE_MODE': self.resource_mode
            })
            
            # 准备MCP调用命令
            # 使用 python -m minimax_mcp 调用MCP服务
            cmd = [
                'python', '-m', 'minimax_mcp',
                '--tool', tool_name,
                '--args', json.dumps(args)
            ]
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # 解析输出
                output = stdout.decode('utf-8').strip()
                
                # 尝试解析JSON输出
                try:
                    result = json.loads(output)
                    return {"success": True, **result}
                except json.JSONDecodeError:
                    # 如果不是JSON，解析文本输出
                    return self._parse_text_output(output, tool_name)
            else:
                error_msg = stderr.decode('utf-8').strip()
                logger.error(f"MCP工具调用失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "return_code": process.returncode
                }
                
        except Exception as e:
            logger.error(f"调用MCP工具时发生异常: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_text_output(self, output: str, tool_name: str) -> Dict[str, Any]:
        """
        解析MCP工具的文本输出
        
        Args:
            output: 工具输出文本
            tool_name: 工具名称
            
        Returns:
            解析后的结果字典
        """
        try:
            if tool_name == "text_to_audio":
                # 解析文字转语音的输出
                if "Success" in output:
                    if "Audio URL:" in output:
                        # URL模式
                        url_start = output.find("Audio URL:") + len("Audio URL:")
                        audio_url = output[url_start:].strip()
                        return {
                            "success": True,
                            "audio_url": audio_url,
                            "message": "语音合成成功（URL模式）"
                        }
                    elif "File saved as:" in output:
                        # 本地文件模式
                        file_start = output.find("File saved as:") + len("File saved as:")
                        voice_start = output.find("Voice used:")
                        
                        if voice_start > 0:
                            audio_path = output[file_start:voice_start].strip().rstrip(".")
                            voice_used = output[voice_start + len("Voice used:"):].strip()
                        else:
                            audio_path = output[file_start:].strip()
                            voice_used = "unknown"
                        
                        return {
                            "success": True,
                            "audio_path": audio_path,
                            "voice_used": voice_used,
                            "message": "语音合成成功（本地文件模式）"
                        }
                else:
                    return {
                        "success": False,
                        "error": output,
                        "message": "语音合成失败"
                    }
            
            elif tool_name == "list_voices":
                # 解析语音列表输出
                if "Success" in output:
                    # 简单解析，实际可能需要更复杂的解析逻辑
                    return {
                        "success": True,
                        "voices": output,
                        "message": "获取语音列表成功"
                    }
                else:
                    return {
                        "success": False,
                        "error": output,
                        "message": "获取语音列表失败"
                    }
            
            else:
                return {
                    "success": True,
                    "output": output,
                    "message": f"{tool_name} 执行成功"
                }
                
        except Exception as e:
            logger.error(f"解析MCP输出时发生错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "raw_output": output
            }

# 创建全局服务实例
minimax_mcp_service = MinimaxMCPService()

# 导出服务实例和类
__all__ = ['MinimaxMCPService', 'minimax_mcp_service'] 