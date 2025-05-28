"""
语音API路由
提供语音识别和语音合成的API接口
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import tempfile
import os
import logging
import base64

from ..services.speech_service import speech_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/speech", tags=["speech"])

class TTSRequest(BaseModel):
    """TTS请求模型"""
    text: str
    voice_id: Optional[str] = None
    interviewer_type: str = "technical"

class VoiceCloneRequest(BaseModel):
    """语音克隆请求模型"""
    voice_id: str
    demo_text: str = "这是一个语音克隆测试"

class ASRRequest(BaseModel):
    """ASR请求模型"""
    audio_data: str  # base64编码的音频数据
    language: str = "zh"
    sample_rate: int = 16000
    format: str = "wav"
    enable_punctuation: bool = True
    enable_timestamp: bool = False

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # system, user, assistant
    content: str

class ChatRequest(BaseModel):
    """聊天请求模型"""
    model: str = "abab6.5s-chat"
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    stream: bool = False

class MinimaxResponseMessage(BaseModel):
    content: Optional[str] = None

class MinimaxChoice(BaseModel):
    message: Optional[MinimaxResponseMessage] = None
    finish_reason: Optional[str] = None

class MinimaxUsage(BaseModel):
    prompt_tokens: Optional[int] = 0
    completion_tokens: Optional[int] = 0
    total_tokens: Optional[int] = 0

class MinimaxChatCompletionResponse(BaseModel):
    choices: Optional[List[MinimaxChoice]] = None
    usage: Optional[MinimaxUsage] = None
    # Add other fields if MiniMax provides them and they are useful, e.g.:
    # id: Optional[str] = None
    # object: Optional[str] = None # e.g., "chat.completion"
    # created: Optional[int] = None # Timestamp
    # model: Optional[str] = None # Model used for the completion

@router.get("/status")
async def get_speech_service_status():
    """获取语音服务状态"""
    try:
        status = speech_service.get_service_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"获取语音服务状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = Form("zh")
):
    """
    语音识别API
    将上传的音频文件转换为文本
    """
    try:
        # 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 调用语音识别服务
            text = await speech_service.speech_to_text(temp_file_path, language)
            
            if text is None:
                raise HTTPException(status_code=500, detail="语音识别失败")
            
            return {
                "success": True,
                "data": {
                    "text": text,
                    "language": language
                }
            }
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"语音识别API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """
    语音合成API
    将文本转换为语音文件
    """
    try:
        logger.info(f"收到TTS请求: text='{request.text[:50]}...', voice_id={request.voice_id}, interviewer_type={request.interviewer_type}")
        
        # 调用语音合成服务
        audio_file_path = await speech_service.text_to_speech(
            text=request.text,
            voice_id=request.voice_id,
            interviewer_type=request.interviewer_type
        )
        
        if audio_file_path is None:
            raise HTTPException(status_code=500, detail="语音合成失败")
        
        if not os.path.exists(audio_file_path):
            raise HTTPException(status_code=500, detail="生成的音频文件不存在")
        
        logger.info(f"语音合成成功，文件路径: {audio_file_path}")
        
        # 返回音频文件
        return FileResponse(
            path=audio_file_path,
            media_type="audio/mpeg",
            filename="speech.mp3",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    
    except Exception as e:
        logger.error(f"语音合成API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def get_available_voices():
    """获取可用的语音列表"""
    try:
        voices = await speech_service.get_available_voices()
        return {
            "success": True,
            "data": voices
        }
    except Exception as e:
        logger.error(f"获取语音列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clone-voice")
async def clone_voice(
    request: VoiceCloneRequest,
    audio_file: UploadFile = File(...)
):
    """
    语音克隆API
    使用上传的音频文件克隆语音
    """
    try:
        # 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 调用语音克隆服务
            cloned_voice_id = await speech_service.clone_voice(
                voice_id=request.voice_id,
                audio_file_path=temp_file_path,
                demo_text=request.demo_text
            )
            
            if cloned_voice_id is None:
                raise HTTPException(status_code=500, detail="语音克隆失败")
            
            return {
                "success": True,
                "data": {
                    "voice_id": cloned_voice_id,
                    "demo_text": request.demo_text
                }
            }
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"语音克隆API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/play-audio")
async def play_audio(audio_file: UploadFile = File(...)):
    """
    音频播放API
    播放上传的音频文件
    """
    try:
        # 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 调用音频播放服务
            success = await speech_service.play_audio_file(temp_file_path)
            
            if not success:
                raise HTTPException(status_code=500, detail="音频播放失败")
            
            return {
                "success": True,
                "message": "音频播放成功"
            }
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"音频播放API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MiniMax MCP专用路由
@router.post("/minimax-mcp/speech-to-text", response_model=Dict[str, Any], tags=["minimax_mcp_speech"])
async def minimax_mcp_speech_to_text(request: ASRRequest):
    """
    MiniMax MCP专用语音识别API
    接受base64编码的音频数据
    """
    try:
        logger.info(f"收到MiniMax MCP ASR请求: language={request.language}, format={request.format}")
        
        # 解码base64音频数据
        try:
            audio_data = base64.b64decode(request.audio_data)
            logger.info(f"音频数据解码成功，大小: {len(audio_data)}字节")
        except Exception as e:
            logger.error(f"base64解码失败: {e}")
            raise HTTPException(status_code=400, detail="无效的base64音频数据")
        
        # 调用语音识别服务
        result = await speech_service.speech_to_text(
            audio_data=audio_data,
            language=request.language,
            audio_format=request.format
        )
        
        # 检查结果
        if not result:
            raise HTTPException(status_code=500, detail="语音识别失败")
        
        logger.info(f"MiniMax MCP语音识别成功: {result.get('text', '')[:50]}...")
        
        return {
            "success": True,
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "duration": result.get("duration", 0.0),
            "service": result.get("service", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MiniMax MCP ASR错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/minimax-mcp/text-to-speech")
async def minimax_mcp_text_to_speech(request: TTSRequest):
    """
    MiniMax MCP专用语音合成API
    """
    request_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(request)}" 
    try:
        logger.info(f"[{request_id}] 收到MiniMax MCP TTS请求: {request}")
        
        # 调用语音服务的MiniMax MCP功能
        logger.debug(f"[{request_id}] 开始调用语音服务: text_to_speech(text='{request.text[:30]}...', voice='{request.interviewer_type}')")
        result = await speech_service.text_to_speech(
            text=request.text,
            voice=request.interviewer_type,  # 使用面试官类型作为语音选择
            speed=1.0
        )
        
        # 记录详细结果信息
        result_keys = list(result.keys()) if result else []
        logger.debug(f"[{request_id}] 语音服务返回结果包含键: {result_keys}")        
        
        # 检查结果
        if not result:
            logger.error(f"[{request_id}] TTS服务返回空结果")
            raise HTTPException(status_code=500, detail="语音合成失败")
        
        # 如果有音频文件路径，返回文件
        if "audio_file_path" in result and os.path.exists(result["audio_file_path"]):
            file_size = os.path.getsize(result["audio_file_path"])
            logger.info(f"[{request_id}] MiniMax MCP语音合成成功，文件路径: {result['audio_file_path']}，大小: {file_size} 字节")
            
            # 记录要返回的响应信息
            logger.debug(f"[{request_id}] 返回FileResponse，media_type=audio/mpeg, filename=speech.mp3")
            response = FileResponse(
                path=result["audio_file_path"],
                media_type="audio/mpeg",
                filename="speech.mp3"
            )
            
            # 记录响应头信息
            logger.debug(f"[{request_id}] 响应头: {dict(response.headers)}")
            return response
        
        # 如果有音频数据，保存为临时文件并返回
        elif "audio_data" in result:
            audio_data_size = len(result["audio_data"])
            audio_data_start = result["audio_data"][:20].hex() if isinstance(result["audio_data"], bytes) else "非二进制数据"  
            logger.debug(f"[{request_id}] 收到音频数据，大小: {audio_data_size} 字节，数据开头: {audio_data_start}...")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(result["audio_data"])
                temp_file_path = temp_file.name
            
            file_size = os.path.getsize(temp_file_path)
            logger.info(f"[{request_id}] MiniMax MCP语音合成成功，临时文件: {temp_file_path}，大小: {file_size} 字节")
            
            # 记录要返回的响应信息
            logger.debug(f"[{request_id}] 返回FileResponse，media_type=audio/mpeg, filename=speech.mp3")
            response = FileResponse(
                path=temp_file_path,
                media_type="audio/mpeg",
                filename="speech.mp3"
            )
            
            # 记录响应头信息
            logger.debug(f"[{request_id}] 响应头: {dict(response.headers)}")
            return response
        
        # 如果是直接返回文本或其他格式的数据
        elif "response_text" in result:
            response_text = result["response_text"]
            response_type = result.get("content_type", "text/plain")
            response_length = len(response_text) if response_text else 0
            
            logger.info(f"[{request_id}] MiniMax MCP返回文本数据，长度: {response_length} 字节，Content-Type: {response_type}")
            if response_length > 0:
                logger.debug(f"[{request_id}] 返回内容预览: {response_text[:100]}...")
            
            # 创建带有正确Content-Type的响应
            from fastapi.responses import Response
            response = Response(content=response_text, media_type=response_type)
            
            # 记录响应头信息
            logger.debug(f"[{request_id}] 响应头: {dict(response.headers)}")
            return response
        
        else:
            logger.error(f"[{request_id}] 无法识别的TTS返回结果格式: {result_keys}")  
            raise HTTPException(status_code=500, detail="无法获取音频数据")
        
    except Exception as e:
        logger.error(f"[{request_id}] MiniMax MCP TTS错误: {e}")
        import traceback
        logger.debug(f"[{request_id}] 错误堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.options("/minimax-mcp/chat")
async def options_minimax_mcp_chat():
    """
    处理针对 /minimax-mcp/chat 的 OPTIONS 预检请求
    用于解决 CORS 问题
    """
    return {}  # 返回空响应即可

@router.post("/minimax-mcp/chat", response_model=MinimaxChatCompletionResponse, tags=["minimax_mcp_speech"])
async def minimax_mcp_chat_completion(request: ChatRequest):
    """
    MiniMax MCP专用聊天补全API
    接收聊天消息并返回AI生成的回复
    """
    request_id = request.model + "_" + str(request.messages[-1].content[:10]) # Basic request identifier for logging
    logger.info(f"[{request_id}] Received request for /minimax-mcp/chat")
    logger.debug(f"[{request_id}] Request body: {request.model_dump_json(indent=2)}")

    if request.stream:
        # This endpoint is for non-streaming, the frontend has a separate /chat-stream
        logger.warning(f"[{request_id}] Received stream=True for non-streaming endpoint /minimax-mcp/chat. Forcing stream=False.")
        request.stream = False # Or raise HTTPException for bad request

    try:
        # Delegate to the speech_service to handle the actual call to MiniMax
        # This service method will need to be implemented
        completion_response = await speech_service.minimax_chat_completion(request)
        
        logger.info(f"[{request_id}] Successfully processed chat completion request.")
        logger.debug(f"[{request_id}] Response from service: {completion_response.model_dump_json(indent=2)}")
        
        return completion_response

    except HTTPException as e:
        # Re-raise HTTPExceptions directly
        logger.error(f"[{request_id}] HTTPException during chat completion: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[{request_id}] Unhandled exception in /minimax-mcp/chat: {e}")
        import traceback
        logger.debug(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# TODO: Implement /minimax-mcp/chat-stream endpoint for streaming responses

@router.get("/minimax-mcp/voices")
async def get_minimax_mcp_voices():
    """获取MiniMax MCP可用语音列表"""
    try:
        voices = await speech_service.get_available_voices()
        return {
            "success": True,
            "data": voices.get("minimax_mcp", [])
        }
    except Exception as e:
        logger.error(f"获取MiniMax MCP语音列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/minimax-mcp/health")
async def check_minimax_mcp_health():
    """检查MiniMax MCP服务健康状态"""
    try:
        health = await speech_service.health_check()
        minimax_status = health.get("services", {}).get("minimax_mcp", {})
        
        return {
            "success": True,
            "data": {
                "available": minimax_status.get("available", False),
                "tts": minimax_status.get("tts", False),
                "stt": minimax_status.get("stt", False),
                "error": minimax_status.get("error")
            }
        }
    except Exception as e:
        logger.error(f"MiniMax MCP健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 