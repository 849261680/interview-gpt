"""
AI服务管理API端点
提供AI服务状态检查、配置管理等功能
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from ...services.ai.ai_service_manager import ai_service_manager
from ...services.ai.crewai_integration import crewai_integration
from ...db.database import get_db
from ...utils.exceptions import AIServiceError

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def check_ai_services_health():
    """
    检查所有AI服务的健康状态
    
    Returns:
        Dict[str, Any]: 各AI服务的健康状态
    """
    try:
        logger.info("检查AI服务健康状态")
        
        # 获取所有AI服务的健康状态
        health_status = await ai_service_manager.health_check()
        
        # 计算整体健康状态
        total_services = len(health_status)
        healthy_services = sum(1 for status in health_status.values() if status)
        overall_health = healthy_services / total_services if total_services > 0 else 0
        
        return {
            "success": True,
            "data": {
                "overall_health": overall_health,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "services": health_status,
                "primary_service": ai_service_manager.get_primary_service(),
                "available_services": ai_service_manager.get_available_services()
            }
        }
        
    except Exception as e:
        logger.error(f"AI服务健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.get("/services", response_model=Dict[str, Any])
async def get_available_services():
    """
    获取可用的AI服务列表
    
    Returns:
        Dict[str, Any]: 可用的AI服务信息
    """
    try:
        logger.info("获取可用AI服务列表")
        
        available_services = ai_service_manager.get_available_services()
        primary_service = ai_service_manager.get_primary_service()
        
        # 获取每个服务的详细信息
        services_info = {}
        for service_name in available_services:
            try:
                client = ai_service_manager.get_client(service_name)
                services_info[service_name] = {
                    "name": service_name,
                    "type": client.get_service_name(),
                    "is_primary": service_name == primary_service,
                    "status": "available"
                }
            except Exception as e:
                services_info[service_name] = {
                    "name": service_name,
                    "type": "unknown",
                    "is_primary": service_name == primary_service,
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "success": True,
            "data": {
                "primary_service": primary_service,
                "available_services": available_services,
                "services_info": services_info,
                "total_services": len(available_services)
            }
        }
        
    except Exception as e:
        logger.error(f"获取AI服务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取服务列表失败: {str(e)}")


@router.get("/interviewers", response_model=Dict[str, Any])
async def get_available_interviewers():
    """
    获取可用的面试官类型
    
    Returns:
        Dict[str, Any]: 可用的面试官信息
    """
    try:
        logger.info("获取可用面试官类型")
        
        # 从CrewAI集成获取面试官信息
        interviewer_types = crewai_integration.get_available_interviewers()
        
        # 获取面试官详细信息
        interviewers_info = {}
        for interviewer_type in interviewer_types:
            if interviewer_type in crewai_integration.agents:
                agent = crewai_integration.agents[interviewer_type]
                interviewers_info[interviewer_type] = {
                    "type": interviewer_type,
                    "role": agent.role,
                    "goal": agent.goal,
                    "backstory": agent.backstory[:200] + "..." if len(agent.backstory) > 200 else agent.backstory
                }
        
        return {
            "success": True,
            "data": {
                "available_interviewers": interviewer_types,
                "interviewers_info": interviewers_info,
                "total_interviewers": len(interviewer_types)
            }
        }
        
    except Exception as e:
        logger.error(f"获取面试官列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取面试官列表失败: {str(e)}")


@router.post("/test-chat", response_model=Dict[str, Any])
async def test_ai_chat(
    request_data: Dict[str, Any]
):
    """
    测试AI聊天功能
    
    Args:
        request_data: 包含测试消息的请求数据
        
    Returns:
        Dict[str, Any]: AI回复结果
    """
    try:
        logger.info("测试AI聊天功能")
        
        # 提取请求参数
        message = request_data.get("message", "Hello, this is a test message.")
        service_name = request_data.get("service_name")
        
        # 构建测试消息
        messages = [{"role": "user", "content": message}]
        
        # 调用AI服务
        response = await ai_service_manager.chat_completion(
            messages=messages,
            service_name=service_name,
            temperature=0.7,
            max_tokens=200
        )
        
        return {
            "success": True,
            "data": {
                "request_message": message,
                "ai_response": response,
                "service_used": service_name or ai_service_manager.get_primary_service()
            }
        }
        
    except AIServiceError as e:
        logger.error(f"AI聊天测试失败: {str(e)}")
        raise HTTPException(status_code=503, detail=f"AI服务不可用: {str(e)}")
    except Exception as e:
        logger.error(f"AI聊天测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.post("/test-interview", response_model=Dict[str, Any])
async def test_interview_round(
    request_data: Dict[str, Any]
):
    """
    测试面试轮次功能
    
    Args:
        request_data: 包含面试测试数据的请求
        
    Returns:
        Dict[str, Any]: 面试回复结果
    """
    try:
        logger.info("测试面试轮次功能")
        
        # 提取请求参数
        interviewer_type = request_data.get("interviewer_type", "technical")
        message = request_data.get("message", "我有3年的Python开发经验。")
        position = request_data.get("position", "AI应用工程师")
        difficulty = request_data.get("difficulty", "medium")
        
        # 构建测试消息历史
        messages = [
            {"sender_type": "system", "content": "面试开始"},
            {"sender_type": "user", "content": message}
        ]
        
        # 调用CrewAI进行面试
        response = await crewai_integration.conduct_interview_round(
            interviewer_type=interviewer_type,
            messages=messages,
            position=position,
            difficulty=difficulty
        )
        
        return {
            "success": True,
            "data": {
                "interviewer_type": interviewer_type,
                "position": position,
                "difficulty": difficulty,
                "user_message": message,
                "interviewer_response": response
            }
        }
        
    except AIServiceError as e:
        logger.error(f"面试测试失败: {str(e)}")
        raise HTTPException(status_code=503, detail=f"面试服务不可用: {str(e)}")
    except Exception as e:
        logger.error(f"面试测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.get("/config", response_model=Dict[str, Any])
async def get_ai_config():
    """
    获取AI服务配置信息（不包含敏感信息）
    
    Returns:
        Dict[str, Any]: AI服务配置信息
    """
    try:
        logger.info("获取AI服务配置")
        
        from ...config.settings import settings
        
        # 返回非敏感的配置信息
        config_info = {
            "primary_service": settings.PRIMARY_AI_SERVICE,
            "available_services": settings.AVAILABLE_AI_SERVICES,
            "crewai_verbose": settings.CREWAI_VERBOSE,
            "crewai_max_iterations": settings.CREWAI_MAX_ITERATIONS,
            "crewai_max_rpm": settings.CREWAI_MAX_RPM,
            "vector_db_type": settings.VECTOR_DB_TYPE,
            "services_configured": {
                "deepseek": bool(settings.DEEPSEEK_API_KEY),
                "minimax": bool(settings.MINIMAX_API_KEY and settings.MINIMAX_GROUP_ID),
                "openai": bool(settings.OPENAI_API_KEY)
            }
        }
        
        return {
            "success": True,
            "data": config_info
        }
        
    except Exception as e:
        logger.error(f"获取AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}") 