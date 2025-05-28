"""
DeepSeek API 服务
负责与 DeepSeek API 进行通信，获取面试问题的回答
"""
import os
import json
import logging
import aiohttp
from typing import List, Dict, Any, Optional

from ...config.settings import settings

logger = logging.getLogger(__name__)

class DeepSeekService:
    """
    DeepSeek API 服务类
    提供与 DeepSeek 模型交互的方法
    """
    
    def __init__(self):
        """
        初始化 DeepSeek 服务
        """
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY 未设置，DeepSeek 功能将使用模拟模式")
        
        logger.info("DeepSeek 服务初始化完成")
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                             temperature: float = 0.7, 
                             max_tokens: int = 2000) -> Dict[str, Any]:
        """
        获取 DeepSeek 模型的聊天回复
        
        Args:
            messages: 聊天消息列表，每个消息包含 role 和 content
            temperature: 温度参数，控制回答的随机性
            max_tokens: 生成回答的最大 token 数
            
        Returns:
            DeepSeek API 的响应
        """
        logger.info(f"调用 DeepSeek API 生成回答，消息数量: {len(messages)}")
        
        if not self.api_key:
            return await self._mock_chat_completion(messages, temperature, max_tokens)
        
        try:
            # 构建请求体
            request_body = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 发送请求到 DeepSeek API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_body
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"DeepSeek API 调用失败: {response.status}, {error_text}")
                        return {
                            "success": False,
                            "error": f"DeepSeek API 调用失败: {response.status}",
                            "details": error_text
                        }
                    
                    result = await response.json()
                    logger.info("DeepSeek API 调用成功")
                    return {
                        "success": True,
                        "data": result
                    }
        
        except Exception as e:
            logger.error(f"DeepSeek API 调用异常: {str(e)}")
            return {
                "success": False,
                "error": f"DeepSeek API 调用异常: {str(e)}"
            }
    
    async def _mock_chat_completion(self, messages: List[Dict[str, str]], 
                                  temperature: float, 
                                  max_tokens: int) -> Dict[str, Any]:
        """
        模拟 DeepSeek API 调用，用于测试
        
        Args:
            messages: 聊天消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            模拟的 API 响应
        """
        logger.info("使用模拟模式生成 DeepSeek 回答")
        
        # 提取最后一条用户消息
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break
        
        # 根据用户问题生成模拟回答
        response_content = f"这是对问题 '{last_message[:30]}...' 的模拟回答。在实际环境中，这将由 DeepSeek 模型生成。"
        
        # 构造模拟响应
        mock_response = {
            "id": "mock-deepseek-response",
            "object": "chat.completion",
            "created": 1683125326,
            "model": self.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(last_message) // 4,  # 粗略估计
                "completion_tokens": len(response_content) // 4,  # 粗略估计
                "total_tokens": (len(last_message) + len(response_content)) // 4  # 粗略估计
            }
        }
        
        return {
            "success": True,
            "data": mock_response
        }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        return {
            "service": "DeepSeek API",
            "available": bool(self.api_key),
            "model": self.model,
            "api_base": self.api_base
        }

# 创建单例实例
deepseek_service = DeepSeekService()
