"""
AI客户端基础类
定义所有AI服务客户端的通用接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class BaseAIClient(ABC):
    """
    AI客户端基础抽象类
    定义所有AI服务必须实现的接口
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化AI客户端
        
        Args:
            api_key: API密钥
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.config = kwargs
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            str: AI回复内容
        """
        pass
    
    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天完成接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Yields:
            str: 流式回复内容片段
        """
        pass
    
    @abstractmethod
    async def embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        文本嵌入接口
        
        Args:
            texts: 文本列表
            model: 嵌入模型名称
            **kwargs: 其他参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康检查接口
        
        Returns:
            bool: 服务是否可用
        """
        pass
    
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        格式化消息为标准格式
        
        Args:
            messages: 原始消息列表
            
        Returns:
            List[Dict[str, str]]: 格式化后的消息列表
        """
        formatted_messages = []
        
        for msg in messages:
            # 提取角色和内容
            role = msg.get("sender_type", "user")
            content = msg.get("content", "")
            
            # 转换角色名称
            if role == "user":
                formatted_role = "user"
            elif role == "interviewer":
                formatted_role = "assistant"
            elif role == "system":
                formatted_role = "system"
            else:
                formatted_role = "user"  # 默认为用户
            
            formatted_messages.append({
                "role": formatted_role,
                "content": content
            })
        
        return formatted_messages
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return self.__class__.__name__.replace("Client", "").lower()
    
    def log_request(self, method: str, **kwargs):
        """记录请求日志"""
        self.logger.info(f"调用 {method} 方法", extra={"params": kwargs})
    
    def log_response(self, method: str, response_length: int):
        """记录响应日志"""
        self.logger.info(f"{method} 方法响应完成", extra={"response_length": response_length}) 