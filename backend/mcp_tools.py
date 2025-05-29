"""
MCP工具包装模块
提供对MiniMax MCP工具的真实调用接口
"""

import os
import logging
import asyncio
import subprocess
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MCPResult:
    """MCP工具调用结果"""
    content: str
    success: bool = True
    error: Optional[str] = None

def _call_minimax_mcp_sync(tool_name: str, **kwargs) -> MCPResult:
    """
    同步调用MiniMax MCP工具
    
    Args:
        tool_name: 工具名称
        **kwargs: 工具参数
        
    Returns:
        MCP调用结果
    """
    try:
        # 检查环境变量
        api_key = os.getenv('MINIMAX_API_KEY')
        api_host = os.getenv('MINIMAX_API_HOST', 'https://api.minimax.chat')
        
        if not api_key:
            return MCPResult(
                content=f"Failed to call {tool_name}: MINIMAX_API_KEY not configured",
                success=False,
                error="API密钥未配置"
            )
        
        # 设置环境变量
        env = os.environ.copy()
        env.update({
            'MINIMAX_API_KEY': api_key,
            'MINIMAX_API_HOST': api_host,
            'MINIMAX_API_RESOURCE_MODE': 'url'  # 使用URL模式
        })
        
        # 构建Python代码来调用MiniMax MCP
        python_code = f"""
import os
import sys
sys.path.insert(0, '/Users/psx849261680/Desktop/Interview-GPT/venv311/lib/python3.11/site-packages')

from minimax_mcp.server import {tool_name}
from mcp.types import TextContent

try:
    # 调用MCP工具
    result = {tool_name}({', '.join([f'{k}={repr(v)}' for k, v in kwargs.items()])})
    
    if isinstance(result, TextContent):
        print(result.text)
    else:
        print(str(result))
        
except Exception as e:
    print(f"Error: {{str(e)}}")
    sys.exit(1)
"""
        
        # 执行Python代码
        process = subprocess.run(
            ['python', '-c', python_code],
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if process.returncode == 0:
            output = process.stdout.strip()
            logger.info(f"MiniMax MCP {tool_name} 调用成功")
            
            return MCPResult(
                content=output,
                success=True
            )
        else:
            error_msg = process.stderr.strip() or process.stdout.strip()
            logger.error(f"MiniMax MCP {tool_name} 调用失败: {error_msg}")
            
            return MCPResult(
                content=f"Failed to call {tool_name}: {error_msg}",
                success=False,
                error=error_msg
            )
            
    except subprocess.TimeoutExpired:
        logger.error(f"MiniMax MCP {tool_name} 调用超时")
        return MCPResult(
            content=f"Failed to call {tool_name}: Timeout",
            success=False,
            error="调用超时"
        )
    except Exception as e:
        logger.error(f"MiniMax MCP {tool_name} 调用异常: {str(e)}")
        return MCPResult(
            content=f"Failed to call {tool_name}: {str(e)}",
            success=False,
            error=str(e)
        )

def mcp_MiniMax_text_to_audio(
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
) -> MCPResult:
    """
    MiniMax文字转语音工具
    """
    try:
        logger.info(f"调用MiniMax TTS: {text[:50]}...")
        
        # 准备参数
        params = {
            'text': text,
            'voice_id': voice_id,
            'model': model,
            'speed': speed,
            'vol': vol,
            'pitch': pitch,
            'emotion': emotion,
            'sample_rate': sample_rate,
            'bitrate': bitrate,
            'channel': channel,
            'format': format,
            'language_boost': language_boost
        }
        
        if output_directory:
            params['output_directory'] = output_directory
        
        # 调用MCP工具
        return _call_minimax_mcp_sync('text_to_audio', **params)
        
    except Exception as e:
        logger.error(f"MiniMax TTS调用失败: {str(e)}")
        return MCPResult(
            content=f"Failed to generate audio: {str(e)}",
            success=False,
            error=str(e)
        )

def mcp_MiniMax_list_voices(voice_type: str = "all") -> MCPResult:
    """
    获取MiniMax可用语音列表
    """
    try:
        logger.info("获取MiniMax语音列表...")
        
        # 调用MCP工具
        return _call_minimax_mcp_sync('list_voices', voice_type=voice_type)
        
    except Exception as e:
        logger.error(f"获取MiniMax语音列表失败: {str(e)}")
        return MCPResult(
            content=f"Failed to list voices: {str(e)}",
            success=False,
            error=str(e)
        )

def mcp_MiniMax_play_audio(input_file_path: str, is_url: bool = False) -> MCPResult:
    """
    播放音频文件
    """
    try:
        logger.info(f"播放音频: {input_file_path}")
        
        # 调用MCP工具
        return _call_minimax_mcp_sync('play_audio', input_file_path=input_file_path, is_url=is_url)
        
    except Exception as e:
        logger.error(f"播放音频失败: {str(e)}")
        return MCPResult(
            content=f"Failed to play audio: {str(e)}",
            success=False,
            error=str(e)
        )

# 导出函数
__all__ = [
    'mcp_MiniMax_text_to_audio',
    'mcp_MiniMax_list_voices', 
    'mcp_MiniMax_play_audio',
    'MCPResult'
] 