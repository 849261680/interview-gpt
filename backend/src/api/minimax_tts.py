"""
MiniMax TTS API端点
提供基于MiniMax MCP的文字转语音服务
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from ..services.audio_service import audio_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/minimax-tts", tags=["MiniMax TTS"])

class TTSRequest(BaseModel):
    """TTS请求模型"""
    text: str = Field(..., description="要转换的文本", min_length=1, max_length=1000)
    voice_id: str = Field("female-tianmei", description="语音ID")
    model: str = Field("speech-02-hd", description="模型名称")
    speed: float = Field(1.0, description="语速", ge=0.5, le=2.0)
    vol: float = Field(1.0, description="音量", ge=0.0, le=10.0)
    pitch: int = Field(0, description="音调", ge=-12, le=12)
    emotion: str = Field("happy", description="情感")
    sample_rate: int = Field(32000, description="采样率")
    bitrate: int = Field(128000, description="比特率")
    channel: int = Field(1, description="声道数", ge=1, le=2)
    format: str = Field("mp3", description="音频格式")
    language_boost: str = Field("auto", description="语言增强")
    service: str = Field("auto", description="指定服务 (auto, minimax, openai)")

class TTSResponse(BaseModel):
    """TTS响应模型"""
    success: bool
    message: str
    audio_url: Optional[str] = None
    audio_path: Optional[str] = None
    voice_used: Optional[str] = None
    service: Optional[str] = None
    error: Optional[str] = None

class VoicesResponse(BaseModel):
    """语音列表响应模型"""
    success: bool
    message: str
    voices: Any
    service: Optional[str] = None
    error: Optional[str] = None

class ServiceStatusResponse(BaseModel):
    """服务状态响应模型"""
    minimax: Dict[str, Any]
    openai: Dict[str, Any]

@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    文字转语音
    
    使用MiniMax MCP或其他TTS服务将文本转换为语音
    """
    try:
        logger.info(f"收到TTS请求: {request.text[:50]}... (service: {request.service})")
        
        # 调用音频服务
        result = await audio_service.text_to_speech(
            text=request.text,
            voice_id=request.voice_id,
            service=request.service
        )
        
        return TTSResponse(**result)
        
    except Exception as e:
        logger.error(f"TTS API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"语音合成失败: {str(e)}"
        )

@router.get("/voices", response_model=VoicesResponse)
async def get_voices(service: str = "auto"):
    """
    获取可用的语音列表
    
    Args:
        service: 指定服务 (auto, minimax, openai)
    """
    try:
        logger.info(f"获取语音列表 (service: {service})")
        
        result = await audio_service.get_available_voices(service=service)
        
        return VoicesResponse(**result)
        
    except Exception as e:
        logger.error(f"获取语音列表API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取语音列表失败: {str(e)}"
        )

@router.get("/status", response_model=ServiceStatusResponse)
async def get_service_status():
    """
    获取TTS服务状态
    """
    try:
        status = audio_service.get_service_status()
        return ServiceStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"获取服务状态API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取服务状态失败: {str(e)}"
        )

@router.post("/test")
async def test_minimax_tts():
    """
    测试MiniMax TTS功能
    """
    try:
        test_text = "你好，这是MiniMax TTS测试。欢迎使用AI面试系统！"
        
        result = await audio_service.text_to_speech(
            text=test_text,
            voice_id="female-tianmei",
            service="minimax"
        )
        
        return {
            "test_text": test_text,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"测试MiniMax TTS失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"测试失败: {str(e)}"
        ) 