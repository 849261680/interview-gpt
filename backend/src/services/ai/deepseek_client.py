"""
DEEPSEEK API客户端
实现与DEEPSEEK AI服务的集成
"""
import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
import logging

from .base_ai_client import BaseAIClient
from ...utils.exceptions import AIServiceError

logger = logging.getLogger(__name__)


class DeepSeekClient(BaseAIClient):
    """
    DEEPSEEK API客户端
    提供与DEEPSEEK AI服务的完整集成
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        **kwargs
    ):
        """
        初始化DEEPSEEK客户端
        
        Args:
            api_key: DEEPSEEK API密钥
            base_url: API基础URL
            model: 默认模型名称
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, **kwargs)
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
        
        self.logger.info(f"初始化DEEPSEEK客户端: {self.base_url}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        DEEPSEEK聊天完成
        
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
            # 准备请求数据
            request_data = {
                "model": model or self.default_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
                **kwargs
            }
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=request_data
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"DEEPSEEK API错误: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise AIServiceError(error_msg, "deepseek")
            
            # 解析响应
            response_data = response.json()
            
            if "choices" not in response_data or not response_data["choices"]:
                raise AIServiceError("DEEPSEEK API返回空响应", "deepseek")
            
            content = response_data["choices"][0]["message"]["content"]
            self.log_response("chat_completion", len(content))
            
            return content
            
        except httpx.RequestError as e:
            error_msg = f"DEEPSEEK API请求失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "deepseek")
        except json.JSONDecodeError as e:
            error_msg = f"DEEPSEEK API响应解析失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "deepseek")
        except Exception as e:
            error_msg = f"DEEPSEEK API未知错误: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "deepseek")
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        DEEPSEEK流式聊天完成
        
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
        
        try:
            # 准备请求数据
            request_data = {
                "model": model or self.default_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }
            
            # 发送流式请求
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json=request_data
            ) as response:
                
                if response.status_code != 200:
                    error_msg = f"DEEPSEEK流式API错误: {response.status_code}"
                    self.logger.error(error_msg)
                    raise AIServiceError(error_msg, "deepseek")
                
                # 处理流式响应
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 移除 "data: " 前缀
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data)
                            if "choices" in chunk_data and chunk_data["choices"]:
                                delta = chunk_data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue  # 跳过无效的JSON行
                            
        except httpx.RequestError as e:
            error_msg = f"DEEPSEEK流式API请求失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "deepseek")
        except Exception as e:
            error_msg = f"DEEPSEEK流式API未知错误: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "deepseek")
    
    async def embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        DEEPSEEK文本嵌入
        
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
                "model": model or "text-embedding-ada-002",  # DEEPSEEK嵌入模型
                "input": texts,
                **kwargs
            }
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/v1/embeddings",
                json=request_data
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"DEEPSEEK嵌入API错误: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise AIServiceError(error_msg, "deepseek")
            
            # 解析响应
            response_data = response.json()
            
            if "data" not in response_data:
                raise AIServiceError("DEEPSEEK嵌入API返回空响应", "deepseek")
            
            # 提取嵌入向量
            embeddings = [item["embedding"] for item in response_data["data"]]
            self.log_response("embeddings", len(embeddings))
            
            return embeddings
            
        except httpx.RequestError as e:
            error_msg = f"DEEPSEEK嵌入API请求失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "deepseek")
        except Exception as e:
            error_msg = f"DEEPSEEK嵌入API未知错误: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, "deepseek")
    
    async def health_check(self) -> bool:
        """
        DEEPSEEK健康检查
        
        Returns:
            bool: 服务是否可用
        """
        try:
            # 发送简单的聊天请求进行健康检查
            test_messages = [{"role": "user", "content": "Hello"}]
            
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.default_model,
                    "messages": test_messages,
                    "max_tokens": 10
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.warning(f"DEEPSEEK健康检查失败: {str(e)}")
            return False
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    def __del__(self):
        """析构函数，确保客户端被正确关闭"""
        try:
            # 检查是否有运行中的事件循环
            try:
                loop = asyncio.get_running_loop()
                # 如果有运行中的循环，创建任务
                loop.create_task(self.close())
            except RuntimeError:
                # 没有运行中的循环，创建新的循环来关闭客户端
                asyncio.run(self.close())
        except Exception:
            pass  # 忽略析构时的错误 