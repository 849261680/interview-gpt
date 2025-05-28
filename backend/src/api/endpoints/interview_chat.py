"""
面试聊天API端点
提供文字面试的API接口
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import traceback

from ...config.settings import settings
from ...db.database import get_db
from ...services.ai.ai_service_manager import ai_service_manager
from ...services.ai.crewai_integration import crewai_integration
from ...utils.exceptions import AIServiceError

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()


@router.post("/chat", response_model=Dict[str, Any])
async def chat(request_data: Dict[str, Any]):
    """
    处理面试聊天请求
    
    Args:
        request_data: 包含聊天消息和面试官类型的请求数据
        
    Returns:
        Dict[str, Any]: AI面试官的回复
    """
    try:
        logger.info(f"收到面试聊天请求: {request_data}")
        
        # 提取请求参数
        messages = request_data.get("messages", [])
        interviewer_type = request_data.get("interviewer_type", "technical")
        
        if not messages:
            raise HTTPException(status_code=400, detail="消息不能为空")
        
        # 获取系统消息和用户消息
        system_message = next((msg for msg in messages if msg.get("role") == "system"), None)
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        if not user_messages:
            raise HTTPException(status_code=400, detail="请提供用户消息")
        
        # 获取最新的用户消息
        latest_user_message = user_messages[-1].get("content", "")
        
        # 转换消息格式为CrewAI可用格式
        crewai_messages = [
            {"sender_type": msg.get("role"), "content": msg.get("content")}
            for msg in messages
            if msg.get("role") in ["user", "assistant", "system"]
        ]
        
        # 获取职位和难度级别（这里使用默认值，实际应从面试会话中获取）
        position = request_data.get("position", "AI应用工程师")
        difficulty = request_data.get("difficulty", "medium")
        
        logger.debug(f"调用CrewAI面试: 面试官类型={interviewer_type}, 职位={position}, 难度={difficulty}")
        logger.debug(f"面试消息历史: {crewai_messages}")
        
        # 调用CrewAI进行面试
        response = await crewai_integration.conduct_interview_round(
            interviewer_type=interviewer_type,
            messages=crewai_messages,
            position=position,
            difficulty=difficulty
        )
        
        logger.info(f"AI面试官({interviewer_type})回复: {response[:100]}...")
        
        return {
            "success": True,
            "content": response,
            "interviewer_type": interviewer_type
        }
        
    except AIServiceError as e:
        logger.error(f"面试聊天失败: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=503, detail=f"AI服务不可用: {str(e)}")
    except Exception as e:
        logger.error(f"面试聊天处理失败: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
