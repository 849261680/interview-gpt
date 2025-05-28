"""
语音处理API端点
提供语音识别(STT)和语音合成(TTS)功能
"""
import base64
import io
import logging
import tempfile
import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field

from ...services.speech_service import speech_service
from ...utils.exceptions import SpeechProcessingError
from ...config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/speech", tags=["语音处理"])


class SpeechToTextRequest(BaseModel):
    """语音转文字请求模型"""
    audio_data: str = Field(..., description="Base64编码的音频数据")
    language: str = Field(default="zh", description="语言代码 (zh/en)")
    format: str = Field(default="webm", description="音频格式")


class SpeechToTextResponse(BaseModel):
    """语音转文字响应模型"""
    text: str = Field(..., description="识别出的文本")
    confidence: float = Field(..., description="置信度 (0-1)")
    language: str = Field(..., description="检测到的语言")
    duration: float = Field(..., description="音频时长(秒)")


class TextToSpeechRequest(BaseModel):
    """文字转语音请求模型"""
    text: str = Field(..., description="要转换的文本", max_length=1000)
    language: str = Field(default="zh-CN", description="语言代码")
    voice: Optional[str] = Field(default=None, description="语音类型")
    speed: float = Field(default=1.0, description="语速 (0.5-2.0)", ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, description="音调 (0.5-2.0)", ge=0.5, le=2.0)
    volume: float = Field(default=1.0, description="音量 (0.1-1.0)", ge=0.1, le=1.0)


class TextToSpeechResponse(BaseModel):
    """文字转语音响应模型"""
    audio_data: str = Field(..., description="Base64编码的音频数据")
    format: str = Field(..., description="音频格式")
    duration: float = Field(..., description="音频时长(秒)")
    text: str = Field(..., description="原始文本")


@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(request: SpeechToTextRequest):
    """
    语音转文字
    
    将音频数据转换为文本
    
    Args:
        request: 语音转文字请求
        
    Returns:
        SpeechToTextResponse: 识别结果
        
    Raises:
        HTTPException: 处理失败时抛出
    """
    try:
        logger.info(f"开始语音识别，语言: {request.language}, 格式: {request.format}")
        
        # 验证音频数据
        if not request.audio_data:
            raise HTTPException(status_code=400, detail="音频数据不能为空")
        
        # 解码Base64音频数据
        try:
            audio_bytes = base64.b64decode(request.audio_data)
        except Exception as e:
            logger.error(f"Base64解码失败: {e}")
            raise HTTPException(status_code=400, detail="无效的音频数据格式")
        
        # 验证音频大小
        if len(audio_bytes) > settings.MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"音频文件过大，最大支持 {settings.MAX_AUDIO_SIZE // 1024 // 1024}MB"
            )
        
        # 调用语音识别服务
        result = await speech_service.speech_to_text(
            audio_data=audio_bytes,
            language=request.language,
            audio_format=request.format
        )
        
        logger.info(f"语音识别完成，文本长度: {len(result['text'])}")
        
        return SpeechToTextResponse(
            text=result["text"],
            confidence=result["confidence"],
            language=result["language"],
            duration=result["duration"]
        )
        
    except SpeechProcessingError as e:
        logger.error(f"语音识别失败: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"语音识别异常: {e}")
        raise HTTPException(status_code=500, detail="语音识别服务暂时不可用")


@router.post("/speech-to-text/file", response_model=SpeechToTextResponse)
async def speech_to_text_file(
    file: UploadFile = File(..., description="音频文件"),
    language: str = "zh"
):
    """
    文件上传语音转文字
    
    通过文件上传的方式进行语音识别
    
    Args:
        file: 上传的音频文件
        language: 语言代码
        
    Returns:
        SpeechToTextResponse: 识别结果
    """
    try:
        logger.info(f"开始处理上传的音频文件: {file.filename}")
        
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="请上传音频文件")
        
        # 读取文件内容
        audio_data = await file.read()
        
        # 验证文件大小
        if len(audio_data) > settings.MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"文件过大，最大支持 {settings.MAX_AUDIO_SIZE // 1024 // 1024}MB"
            )
        
        # 获取文件格式
        audio_format = file.content_type.split('/')[-1]
        
        # 调用语音识别服务
        result = await speech_service.speech_to_text(
            audio_data=audio_data,
            language=language,
            audio_format=audio_format
        )
        
        logger.info(f"文件语音识别完成: {file.filename}")
        
        return SpeechToTextResponse(
            text=result["text"],
            confidence=result["confidence"],
            language=result["language"],
            duration=result["duration"]
        )
        
    except SpeechProcessingError as e:
        logger.error(f"文件语音识别失败: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"文件语音识别异常: {e}")
        raise HTTPException(status_code=500, detail="语音识别服务暂时不可用")


@router.post("/text-to-speech", response_model=TextToSpeechResponse)
async def text_to_speech(request: TextToSpeechRequest):
    """
    文字转语音
    
    将文本转换为语音音频
    
    Args:
        request: 文字转语音请求
        
    Returns:
        TextToSpeechResponse: 语音合成结果
        
    Raises:
        HTTPException: 处理失败时抛出
    """
    try:
        logger.info(f"开始语音合成，文本长度: {len(request.text)}")
        
        # 验证文本内容
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="文本内容不能为空")
        
        if len(request.text) > 1000:
            raise HTTPException(status_code=400, detail="文本长度不能超过1000字符")
        
        # 调用语音合成服务
        result = await speech_service.text_to_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed,
            pitch=request.pitch,
            volume=request.volume
        )
        
        # 将音频数据编码为Base64
        audio_base64 = base64.b64encode(result["audio_data"]).decode('utf-8')
        
        logger.info(f"语音合成完成，音频大小: {len(result['audio_data'])} bytes")
        
        return TextToSpeechResponse(
            audio_data=audio_base64,
            format=result["format"],
            duration=result["duration"],
            text=request.text
        )
        
    except SpeechProcessingError as e:
        logger.error(f"语音合成失败: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"语音合成异常: {e}")
        raise HTTPException(status_code=500, detail="语音合成服务暂时不可用")


@router.get("/voices")
async def get_available_voices():
    """
    获取可用的语音列表
    
    Returns:
        Dict: 可用语音列表
    """
    try:
        voices = await speech_service.get_available_voices()
        return {
            "voices": voices,
            "total": len(voices)
        }
    except Exception as e:
        logger.error(f"获取语音列表失败: {e}")
        raise HTTPException(status_code=500, detail="无法获取语音列表")


@router.get("/languages")
async def get_supported_languages():
    """
    获取支持的语言列表
    
    Returns:
        Dict: 支持的语言列表
    """
    try:
        languages = await speech_service.get_supported_languages()
        return {
            "languages": languages,
            "total": len(languages)
        }
    except Exception as e:
        logger.error(f"获取语言列表失败: {e}")
        raise HTTPException(status_code=500, detail="无法获取语言列表")


@router.get("/health")
async def speech_health_check():
    """
    语音服务健康检查
    
    Returns:
        Dict: 服务状态信息
    """
    try:
        status = await speech_service.health_check()
        return {
            "status": "healthy" if status["available"] else "unhealthy",
            "services": status["services"],
            "timestamp": status["timestamp"]
        }
    except Exception as e:
        logger.error(f"语音服务健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": None
        }


@router.post("/test/echo")
async def test_speech_echo(request: SpeechToTextRequest):
    """
    语音回声测试
    
    将语音转换为文字，再转换回语音，用于测试完整流程
    
    Args:
        request: 语音数据
        
    Returns:
        Dict: 包含原始文本和回声音频的结果
    """
    try:
        logger.info("开始语音回声测试")
        
        # 解码音频数据
        audio_bytes = base64.b64decode(request.audio_data)
        
        # 语音转文字
        stt_result = await speech_service.speech_to_text(
            audio_data=audio_bytes,
            language=request.language,
            audio_format=request.format
        )
        
        # 文字转语音
        tts_result = await speech_service.text_to_speech(
            text=stt_result["text"],
            language=f"{request.language}-CN" if request.language == "zh" else "en-US"
        )
        
        # 编码回声音频
        echo_audio_base64 = base64.b64encode(tts_result["audio_data"]).decode('utf-8')
        
        logger.info("语音回声测试完成")
        
        return {
            "original_text": stt_result["text"],
            "confidence": stt_result["confidence"],
            "echo_audio": echo_audio_base64,
            "echo_format": tts_result["format"],
            "echo_duration": tts_result["duration"]
        }
        
    except Exception as e:
        logger.error(f"语音回声测试失败: {e}")
        raise HTTPException(status_code=500, detail="语音回声测试失败")


# 添加路由到主应用
def include_speech_routes(app):
    """将语音路由添加到主应用"""
    app.include_router(router) 