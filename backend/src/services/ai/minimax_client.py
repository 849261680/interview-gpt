"""
MiniMax API客户端
实现与MiniMax AI服务的集成
"""
import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
import logging

from .base_ai_client import BaseAIClient
from ...utils.exceptions import AIServiceError

logger = logging.getLogger(__name__)


class MinimaxClient(BaseAIClient):
    """
    MiniMax API客户端
    提供与MiniMax AI服务的完整集成
    """
    
    def __init__(
        self,
        api_key: str,
        group_id: str,
        base_url: str = "https://api.minimax.chat",
        model: str = "abab5.5-chat",
        **kwargs
    ):
        """
        初始化MiniMax客户端
        
        Args:
            api_key: MiniMax API密钥
            group_id: MiniMax Group ID
            base_url: API基础URL
            model: 默认模型名称
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, **kwargs)
        self.group_id = group_id
        self.base_url = base_url.rstrip("/")
        self.default_model = model
        self.timeout = kwargs.get("timeout", 30)
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        self.logger.info(f"初始化MiniMax客户端: {self.base_url}")
    
    def _format_messages_for_minimax(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        将标准消息格式转换为MiniMax格式
        
        Args:
            messages: 标准格式消息列表
            
        Returns:
            List[Dict[str, str]]: MiniMax格式消息列表
        """
        minimax_messages = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # MiniMax使用不同的角色名称
            if role == "user":
                sender_type = "USER"
            elif role == "assistant":
                sender_type = "BOT"
            elif role == "system":
                sender_type = "USER"  # MiniMax将系统消息作为用户消息处理
                content = f"[系统提示] {content}"
            else:
                sender_type = "USER"
            
            minimax_messages.append({
                "sender_type": sender_type,
                "text": content
            })
        
        return minimax_messages
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        MiniMax聊天完成
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            str: AI回复内容
        """
        self.log_request("chat_completion", model=model, temperature=temperature)
        
        try:
            # 转换消息格式
            minimax_messages = self._format_messages_for_minimax(messages)
            
            # 准备请求数据
            request_data = {
                "model": model or self.default_model,
                "messages": minimax_messages,
                "temperature": temperature,
                "tokens_to_generate": max_tokens,
                "top_p": kwargs.get("top_p", 0.95),
                **{k: v for k, v in kwargs.items() if k not in ["top_p"]}
            }
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/v1/text/chatcompletion?GroupId={self.group_id}",
                json=request_data
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"MiniMax API错误: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise AIServiceError(error_msg, "minimax")
            
            # 解析响应
            response_data = response.json()
            
            # 检查MiniMax特定的错误格式
            if "base_resp" in response_data:
                base_resp = response_data["base_resp"]
                if base_resp.get("status_code", 0) != 0:
                    error_msg = f"MiniMax API错误: {base_resp.get('status_msg', '未知错误')}"
                    self.logger.error(error_msg)
                    raise AIServiceError(error_msg, "minimax")
            
            # 提取回复内容
            if "reply" not in response_data:
                raise AIServiceError("MiniMax API返回空响应", "minimax")
            
            content = response_data["reply"]
            self.log_response("chat_completion", len(content))
            
            return content
            
        except httpx.RequestError as e:
            error_msg = f"MiniMax API请求失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "minimax")
        except json.JSONDecodeError as e:
            error_msg = f"MiniMax API响应解析失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "minimax")
        except Exception as e:
            error_msg = f"MiniMax API未知错误: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "minimax")
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        MiniMax流式聊天完成
        注意：MiniMax可能不支持流式响应，这里提供兼容实现
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Yields:
            str: 流式回复内容片段
        """
        self.log_request("stream_chat_completion", model=model, temperature=temperature)
        
        # MiniMax不支持流式响应，使用普通响应模拟流式
        try:
            content = await self.chat_completion(
                messages, model, temperature, max_tokens, **kwargs
            )
            
            # 将完整响应分块返回，模拟流式效果
            chunk_size = 10  # 每次返回10个字符
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield chunk
                # 添加小延迟模拟流式效果
                await asyncio.sleep(0.05)
                
        except Exception as e:
            error_msg = f"MiniMax流式API错误: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "minimax")
    
    async def embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        MiniMax文本嵌入
        
        Args:
            texts: 文本列表
            model: 嵌入模型名称
            **kwargs: 其他参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        self.log_request("embeddings", model=model, texts_count=len(texts))
        
        try:
            # 准备请求数据
            request_data = {
                "model": model or "embo-01",  # MiniMax嵌入模型
                "texts": texts,
                "type": kwargs.get("type", "db"),  # db 或 query
                **{k: v for k, v in kwargs.items() if k not in ["type"]}
            }
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/v1/embeddings?GroupId={self.group_id}",
                json=request_data
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"MiniMax嵌入API错误: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise AIServiceError(error_msg, "minimax")
            
            # 解析响应
            response_data = response.json()
            
            # 检查MiniMax特定的错误格式
            if "base_resp" in response_data:
                base_resp = response_data["base_resp"]
                if base_resp.get("status_code", 0) != 0:
                    error_msg = f"MiniMax嵌入API错误: {base_resp.get('status_msg', '未知错误')}"
                    self.logger.error(error_msg)
                    raise AIServiceError(error_msg, "minimax")
            
            # 提取嵌入向量
            if "vectors" not in response_data:
                raise AIServiceError("MiniMax嵌入API返回空响应", "minimax")
            
            embeddings = response_data["vectors"]
            self.log_response("embeddings", len(embeddings))
            
            return embeddings
            
        except httpx.RequestError as e:
            error_msg = f"MiniMax嵌入API请求失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "minimax")
        except Exception as e:
            error_msg = f"MiniMax嵌入API未知错误: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "minimax")
    
    async def health_check(self) -> bool:
        """
        MiniMax健康检查
        
        Returns:
            bool: 服务是否可用
        """
        try:
            # 发送简单的聊天请求进行健康检查
            test_messages = [{"role": "user", "content": "Hello"}]
            minimax_messages = self._format_messages_for_minimax(test_messages)
            
            response = await self.client.post(
                f"{self.base_url}/v1/text/chatcompletion?GroupId={self.group_id}",
                json={
                    "model": self.default_model,
                    "messages": minimax_messages,
                    "tokens_to_generate": 10
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # 检查MiniMax特定的成功响应
                if "base_resp" in response_data:
                    return response_data["base_resp"].get("status_code", 1) == 0
                return "reply" in response_data
            
            return False
            
        except Exception as e:
            self.logger.warning(f"MiniMax健康检查失败: {str(e)}")
            return False
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    def __del__(self):
        """析构函数，确保客户端被正确关闭"""
        try:
            asyncio.create_task(self.close())
        except Exception:
            pass  # 忽略析构时的错误 