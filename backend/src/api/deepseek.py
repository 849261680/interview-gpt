"""
DeepSeek API u8defu7531
u63d0u4f9bu4e0e DeepSeek u6a21u578bu4ea4u4e92u7684 API u63a5u53e3
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ..services.ai.deepseek_service import deepseek_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["deepseek"])

class ChatMessage(BaseModel):
    """u804au5929u6d88u606fu6a21u578b"""
    role: str  # system, user, assistant
    content: str

class ChatRequest(BaseModel):
    """u804au5929u8bf7u6c42u6a21u578b"""
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2000

class ChatResponse(BaseModel):
    """u804au5929u54cdu5e94u6a21u578b"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest) -> ChatResponse:
    """
    DeepSeek u804au5929u5b8cu6210 API
    u63a5u6536u804au5929u6d88u606fu5e76u8fd4u56de DeepSeek u6a21u578bu751fu6210u7684u56deu590d
    """
    try:
        # u8f6cu6362u8bf7u6c42u683cu5f0f
        messages = [{
            "role": msg.role,
            "content": msg.content
        } for msg in request.messages]
        
        # u8c03u7528 DeepSeek u670du52a1
        result = await deepseek_service.chat_completion(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if not result.get("success", False):
            error_detail = result.get("error", "Unknown error from DeepSeek service")
            logger.error(f"DeepSeek u804au5929u5b8cu6210u5931u8d25: {error_detail}")
            return ChatResponse(success=False, error=error_detail)
        
        return ChatResponse(success=True, data=result.get("data", {}))
    
    except Exception as e:
        logger.error(f"DeepSeek u804au5929 API u5f02u5e38: {str(e)}")
        return ChatResponse(success=False, error=f"An unexpected error occurred: {str(e)}")

@router.options("/chat")
async def options_chat():
    """
    u5904u7406u9488u5bf9 /deepseek/chat u7684 OPTIONS u9884u68c0u8bf7u6c42
    u7528u4e8eu89e3u51b3 CORS u95eeu9898
    """
    return {}

@router.get("/status")
async def get_service_status():
    """u83b7u53d6 DeepSeek u670du52a1u72b6u6001"""
    try:
        status = await deepseek_service.get_service_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"u83b7u53d6 DeepSeek u670du52a1u72b6u6001u5931u8d25: {e}")
        return {
            "success": False,
            "error": str(e)
        }
