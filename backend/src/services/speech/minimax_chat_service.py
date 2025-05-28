"""
MiniMax 聊天服务
提供与 MiniMax 聊天模型交互的功能
"""
import logging
import json
import os
from typing import Dict, Any, Optional, TYPE_CHECKING

from ...config.settings import settings
from ...utils.exceptions import SpeechProcessingError

if TYPE_CHECKING:
    from ...api.speech import ChatRequest, MinimaxChatCompletionResponse

logger = logging.getLogger(__name__)

class MinimaxChatService:
    """
    MiniMax 聊天服务
    提供与 MiniMax 聊天模型交互的功能
    """
    
    def __init__(self):
        """
        初始化 MiniMax 聊天服务
        """
        self.api_key = os.getenv("MINIMAX_API_KEY", "")
        self.group_id = os.getenv("MINIMAX_GROUP_ID", "")
        
        if not self.api_key or not self.group_id:
            logger.warning("MINIMAX_API_KEY 或 MINIMAX_GROUP_ID 未设置，MiniMax 聊天功能将使用模拟模式")
        
        logger.info("MiniMax 聊天服务初始化完成")
    
    async def chat_completion(self, request: 'ChatRequest') -> 'MinimaxChatCompletionResponse':
        """
        处理聊天完成请求
        
        Args:
            request: 聊天请求对象
            
        Returns:
            聊天完成响应
        """
        logger.info(f"[MinimaxChatService] 收到聊天完成请求，模型: {request.model}")
        logger.debug(f"[MinimaxChatService] 完整请求: {request.model_dump_json(indent=2)}")

        # 准备请求参数
        mcp_arguments = {
            "model": request.model,
            "messages": [{ "role": msg.role, "content": msg.content } for msg in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "stream": request.stream,
        }

        try:
            # 调用 MiniMax API
            raw_response = await self._call_minimax_chat_api(mcp_arguments)
            logger.info("[MinimaxChatService] 已收到 MiniMax API 响应")
            logger.debug(f"[MinimaxChatService] 原始响应数据: {json.dumps(raw_response, indent=2)}")

            if not raw_response.get("success", False) or not raw_response.get("data"):
                error_detail = raw_response.get("error", "MiniMax 服务未知错误")
                logger.error(f"[MinimaxChatService] MiniMax 聊天完成失败: {error_detail}")
                raise SpeechProcessingError(f"MiniMax 聊天完成失败: {error_detail}")

            data = raw_response.get("data", {})
            
            if not isinstance(data, dict):
                logger.error(f"[MinimaxChatService] 数据格式错误: {data}")
                raise SpeechProcessingError("MiniMax 服务返回的数据格式无效")

            from ...api.speech import MinimaxChatCompletionResponse 
            try:
                response_obj = MinimaxChatCompletionResponse(**data)
            except Exception as pydantic_error:
                logger.error(f"[MinimaxChatService] 解析数据到 MinimaxChatCompletionResponse 失败: {pydantic_error}")
                logger.error(f"[MinimaxChatService] 收到的数据: {data}")
                raise SpeechProcessingError(f"解析 MiniMax 响应失败: {pydantic_error}")
                
            logger.info("[MinimaxChatService] 成功解析聊天完成响应")
            return response_obj

        except SpeechProcessingError:
            raise
        except Exception as e:
            logger.error(f"[MinimaxChatService] 处理聊天完成请求出错: {e}")
            import traceback
            logger.debug(f"[MinimaxChatService] 堆栈跟踪: {traceback.format_exc()}")
            raise SpeechProcessingError(f"处理 MiniMax 聊天完成请求失败: {str(e)}")
    
    async def _call_minimax_chat_api(self, arguments: dict) -> Dict[str, Any]:
        """
        调用 MiniMax 聊天 API
        
        Args:
            arguments: 请求参数
            
        Returns:
            API 响应
        """
        try:
            logger.info(f"[MinimaxChatService] 调用 MiniMax 聊天 API")
            
            # 如果配置了 API 密钥和 GROUP_ID，则调用真实 API
            if self.api_key and self.group_id:
                # TODO: 实现真实的 MiniMax API 调用
                # 此处应使用 aiohttp 或其他 HTTP 客户端调用 MiniMax API
                # 例如: 
                # async with aiohttp.ClientSession() as session:
                #     async with session.post(
                #         "https://api.minimax.chat/v1/text/chat_completions",
                #         headers={"Authorization": f"Bearer {self.api_key}"},
                #         json={
                #             "model": arguments.get("model", "minimax-text"),
                #             "messages": arguments.get("messages", []),
                #             "temperature": arguments.get("temperature", 0.7),
                #             "max_tokens": arguments.get("max_tokens", 2000),
                #             "top_p": arguments.get("top_p", 0.9),
                #             "stream": arguments.get("stream", False),
                #             "group_id": self.group_id
                #         }
                #     ) as response:
                #         result = await response.json()
                #         return {"success": True, "data": result}
                pass
            
            # 目前使用模拟实现
            # 从用户消息中提取内容，生成更有针对性的模拟回复
            last_user_message = "未知问题"
            if arguments.get('messages'):
                user_messages = [m.get('content', '') for m in arguments['messages'] if m.get('role') == 'user']
                if user_messages:
                    last_user_message = user_messages[-1][:30] # 截取前30个字符作为摘要

            mock_chat_response_data = {
                "choices": [
                    {
                        "message": {
                            "content": f"这是对'{last_user_message}...'的模拟AI回复。这条回复来自 MiniMax 模拟服务。"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(last_user_message),
                    "completion_tokens": 40,
                    "total_tokens": len(last_user_message) + 40
                }
            }
            
            return {
                "success": True,
                "data": mock_chat_response_data
            }
            
        except Exception as e:
            logger.error(f"[MinimaxChatService] MiniMax API 调用失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        return {
            "service_name": "MiniMax 聊天服务",
            "api_key_configured": bool(self.api_key),
            "group_id_configured": bool(self.group_id),
            "models_supported": ["abab5.5-chat", "abab5-chat", "abab5.5s-chat"],
            "status": "active"
        }

# 创建单例实例
minimax_chat_service = MinimaxChatService()
