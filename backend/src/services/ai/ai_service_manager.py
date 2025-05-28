"""
AI服务管理器
统一管理和调度所有AI服务客户端
"""
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
import logging

from .base_ai_client import BaseAIClient
from .deepseek_client import DeepSeekClient
from .minimax_client import MinimaxClient
from .mock_client import MockAIClient
from ...config.settings import settings
from ...utils.exceptions import AIServiceError, ConfigurationError

logger = logging.getLogger(__name__)


class AIServiceManager:
    """
    AI服务管理器
    负责管理多个AI服务客户端，提供统一的接口和故障转移机制
    """
    
    def __init__(self):
        """初始化AI服务管理器"""
        self.clients: Dict[str, BaseAIClient] = {}
        self.primary_service = settings.PRIMARY_AI_SERVICE
        self.available_services = settings.AVAILABLE_AI_SERVICES
        self.logger = logging.getLogger(__name__)
        
        # 初始化所有可用的AI服务客户端
        self._initialize_clients()
        
        self.logger.info(f"AI服务管理器初始化完成，主要服务: {self.primary_service}")
        self.logger.info(f"可用服务: {', '.join(self.available_services)}")
    
    def _initialize_clients(self):
        """初始化所有AI服务客户端"""
        
        # 初始化DEEPSEEK客户端
        if settings.DEEPSEEK_API_KEY:
            try:
                self.clients["deepseek"] = DeepSeekClient(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=settings.DEEPSEEK_BASE_URL,
                    model=settings.DEEPSEEK_MODEL
                )
                self.logger.info("DEEPSEEK客户端初始化成功")
            except Exception as e:
                self.logger.error(f"DEEPSEEK客户端初始化失败: {str(e)}")
        
        # 初始化MiniMax客户端
        if settings.MINIMAX_API_KEY and settings.MINIMAX_GROUP_ID:
            try:
                self.clients["minimax"] = MinimaxClient(
                    api_key=settings.MINIMAX_API_KEY,
                    group_id=settings.MINIMAX_GROUP_ID
                )
                self.logger.info("MiniMax客户端初始化成功")
            except Exception as e:
                self.logger.error(f"MiniMax客户端初始化失败: {str(e)}")
        
        # 初始化OpenAI客户端（如果需要）
        if settings.OPENAI_API_KEY:
            try:
                # 这里可以添加OpenAI客户端的初始化
                # self.clients["openai"] = OpenAIClient(api_key=settings.OPENAI_API_KEY)
                self.logger.info("OpenAI客户端配置可用（未实现）")
            except Exception as e:
                self.logger.error(f"OpenAI客户端初始化失败: {str(e)}")
        
        # 不再使用模拟客户端作为备用
        # self.clients["mock"] = MockAIClient()
        self.logger.info("跳过模拟AI客户端初始化，将使用真实服务")
        
        # 检查是否有可用的真实服务
        if not any(service in self.clients for service in ["deepseek", "minimax", "openai"]):
            self.logger.error("没有可用的真实AI服务，请配置正确的API密钥")
            raise ConfigurationError("没有可用的AI服务，请检查API密钥配置")
    
    def get_client(self, service_name: Optional[str] = None) -> BaseAIClient:
        """
        获取AI服务客户端
        
        Args:
            service_name: 服务名称，如果为None则使用主要服务
            
        Returns:
            BaseAIClient: AI服务客户端
            
        Raises:
            AIServiceError: 服务不可用时抛出异常
        """
        target_service = service_name or self.primary_service
        
        if target_service not in self.clients:
            raise AIServiceError(f"AI服务 '{target_service}' 不可用", target_service)
        
        return self.clients[target_service]
    
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        service_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        聊天完成接口，支持故障转移
        
        Args:
            messages: 消息列表
            service_name: 指定的服务名称
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            str: AI回复内容
        """
        # 格式化消息
        formatted_messages = self._format_messages(messages)
        
        # 确定要尝试的服务列表
        services_to_try = [service_name] if service_name else self.available_services
        
        last_error = None
        for service in services_to_try:
            if service not in self.clients:
                continue
                
            try:
                client = self.clients[service]
                self.logger.info(f"尝试使用 {service} 服务进行聊天完成")
                
                result = await client.chat_completion(
                    formatted_messages, model, temperature, max_tokens, **kwargs
                )
                
                self.logger.info(f"使用 {service} 服务成功完成聊天")
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"{service} 服务失败: {str(e)}")
                continue
        
        # 所有服务都失败了
        error_msg = f"所有AI服务都不可用，最后错误: {str(last_error)}"
        self.logger.error(error_msg)
        raise AIServiceError(error_msg, "all")
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        service_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天完成接口
        
        Args:
            messages: 消息列表
            service_name: 指定的服务名称
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Yields:
            str: 流式回复内容片段
        """
        # 格式化消息
        formatted_messages = self._format_messages(messages)
        
        # 确定要使用的服务
        target_service = service_name or self.primary_service
        
        if target_service not in self.clients:
            raise AIServiceError(f"AI服务 '{target_service}' 不可用", target_service)
        
        client = self.clients[target_service]
        self.logger.info(f"使用 {target_service} 服务进行流式聊天")
        
        try:
            async for chunk in client.stream_chat_completion(
                formatted_messages, model, temperature, max_tokens, **kwargs
            ):
                yield chunk
        except Exception as e:
            error_msg = f"{target_service} 流式服务失败: {str(e)}"
            self.logger.error(error_msg)
            raise AIServiceError(error_msg, target_service)
    
    async def embeddings(
        self,
        texts: List[str],
        service_name: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        文本嵌入接口，支持故障转移
        
        Args:
            texts: 文本列表
            service_name: 指定的服务名称
            model: 嵌入模型名称
            **kwargs: 其他参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        # 确定要尝试的服务列表
        services_to_try = [service_name] if service_name else self.available_services
        
        last_error = None
        for service in services_to_try:
            if service not in self.clients:
                continue
                
            try:
                client = self.clients[service]
                self.logger.info(f"尝试使用 {service} 服务进行文本嵌入")
                
                result = await client.embeddings(texts, model, **kwargs)
                
                self.logger.info(f"使用 {service} 服务成功完成文本嵌入")
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"{service} 嵌入服务失败: {str(e)}")
                continue
        
        # 所有服务都失败了
        error_msg = f"所有AI嵌入服务都不可用，最后错误: {str(last_error)}"
        self.logger.error(error_msg)
        raise AIServiceError(error_msg, "all")
    
    async def health_check(self) -> Dict[str, bool]:
        """
        检查所有AI服务的健康状态
        
        Returns:
            Dict[str, bool]: 各服务的健康状态
        """
        health_status = {}
        
        for service_name, client in self.clients.items():
            try:
                is_healthy = await client.health_check()
                health_status[service_name] = is_healthy
                self.logger.info(f"{service_name} 服务健康检查: {'正常' if is_healthy else '异常'}")
            except Exception as e:
                health_status[service_name] = False
                self.logger.error(f"{service_name} 服务健康检查失败: {str(e)}")
        
        return health_status
    
    def _format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        格式化消息为标准格式
        
        Args:
            messages: 原始消息列表
            
        Returns:
            List[Dict[str, str]]: 格式化后的消息列表
        """
        if not messages:
            return []
        
        # 使用第一个可用客户端的格式化方法
        if self.clients:
            first_client = next(iter(self.clients.values()))
            return first_client.format_messages(messages)
        
        # 如果没有客户端，使用默认格式化
        formatted_messages = []
        for msg in messages:
            role = msg.get("sender_type", "user")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_role = "user"
            elif role == "interviewer":
                formatted_role = "assistant"
            elif role == "system":
                formatted_role = "system"
            else:
                formatted_role = "user"
            
            formatted_messages.append({
                "role": formatted_role,
                "content": content
            })
        
        return formatted_messages
    
    def get_available_services(self) -> List[str]:
        """获取可用的AI服务列表"""
        return list(self.clients.keys())
    
    def get_primary_service(self) -> str:
        """获取主要AI服务名称"""
        return self.primary_service
    
    async def close_all(self):
        """关闭所有AI服务客户端"""
        for service_name, client in self.clients.items():
            try:
                await client.close()
                self.logger.info(f"关闭 {service_name} 客户端")
            except Exception as e:
                self.logger.error(f"关闭 {service_name} 客户端失败: {str(e)}")


# 创建全局AI服务管理器实例
ai_service_manager = AIServiceManager() 