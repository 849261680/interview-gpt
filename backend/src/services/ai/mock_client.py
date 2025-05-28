"""
模拟AI客户端
用于测试和开发环境，提供模拟的AI响应
"""
import asyncio
import random
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging

from .base_ai_client import BaseAIClient

logger = logging.getLogger(__name__)


class MockAIClient(BaseAIClient):
    """
    模拟AI客户端
    用于测试和开发环境，不需要真实的API密钥
    """
    
    def __init__(self, api_key: str = "mock_key", **kwargs):
        """
        初始化模拟AI客户端
        
        Args:
            api_key: 模拟API密钥（可以是任意值）
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, **kwargs)
        self.response_delay = kwargs.get("response_delay", 1.0)  # 模拟响应延迟
        self.logger.info("初始化模拟AI客户端")
        
        # 预定义的模拟响应
        self.mock_responses = {
            "technical": [
                "请详细介绍一下您在Python开发方面的经验，包括使用过的框架和项目实例。",
                "能否描述一下您对面向对象编程的理解？请举例说明封装、继承和多态的概念。",
                "您在项目中是如何处理异常和错误的？请分享一些最佳实践。",
                "请解释一下数据库索引的作用，以及在什么情况下应该创建索引。",
                "您对微服务架构有什么了解？它相比单体架构有哪些优势和挑战？"
            ],
            "hr": [
                "请简单介绍一下您自己，包括您的教育背景和工作经历。",
                "您为什么想要加入我们公司？对这个职位有什么期待？",
                "请描述一下您理想的工作环境和团队氛围。",
                "您的职业规划是什么？未来3-5年希望在哪些方面有所发展？",
                "您在之前的工作中遇到过什么挑战？是如何解决的？"
            ],
            "behavioral": [
                "请描述一次您在团队中解决冲突的经历。",
                "能否分享一个您在压力下成功完成任务的例子？",
                "请举例说明您是如何学习新技能或适应新环境的。",
                "描述一次您主动承担额外责任的情况。",
                "请分享一个您从失败中学到重要经验的例子。"
            ],
            "general": [
                "感谢您的回答。能否进一步详细说明一下？",
                "这个例子很有趣。您在这个过程中学到了什么？",
                "您提到的这个方法很好。还有其他的解决方案吗？",
                "基于您的经验，您认为这个领域未来的发展趋势是什么？",
                "非常好的回答。接下来我想了解一下您在其他方面的经验。"
            ]
        }
    
    def _get_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """
        根据对话历史生成模拟响应
        
        Args:
            messages: 消息历史
            
        Returns:
            str: 模拟响应
        """
        # 分析最后几条消息，判断面试类型
        recent_content = " ".join([msg.get("content", "") for msg in messages[-3:]])
        
        # 根据关键词判断面试类型
        if any(keyword in recent_content.lower() for keyword in ["python", "代码", "技术", "算法", "数据库", "框架"]):
            response_type = "technical"
        elif any(keyword in recent_content.lower() for keyword in ["公司", "职业", "规划", "期待", "背景"]):
            response_type = "hr"
        elif any(keyword in recent_content.lower() for keyword in ["团队", "冲突", "压力", "挑战", "经历"]):
            response_type = "behavioral"
        else:
            response_type = "general"
        
        # 随机选择一个响应
        responses = self.mock_responses.get(response_type, self.mock_responses["general"])
        return random.choice(responses)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        模拟聊天完成
        
        Args:
            messages: 消息列表
            model: 模型名称（忽略）
            temperature: 温度参数（忽略）
            max_tokens: 最大token数（忽略）
            **kwargs: 其他参数（忽略）
            
        Returns:
            str: 模拟AI回复内容
        """
        self.log_request("chat_completion", model=model, temperature=temperature)
        
        # 模拟API延迟
        await asyncio.sleep(self.response_delay)
        
        # 生成模拟响应
        response = self._get_mock_response(messages)
        
        # 添加一些随机性
        if random.random() < 0.3:  # 30%的概率添加额外内容
            additional_content = [
                "另外，我还想了解一下您对这个问题的看法。",
                "顺便问一下，您在这方面还有其他经验吗？",
                "这让我想到了另一个相关的问题。",
                "基于您刚才的回答，我想深入了解一下。"
            ]
            response += " " + random.choice(additional_content)
        
        self.log_response("chat_completion", len(response))
        return response
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        模拟流式聊天完成
        
        Args:
            messages: 消息列表
            model: 模型名称（忽略）
            temperature: 温度参数（忽略）
            max_tokens: 最大token数（忽略）
            **kwargs: 其他参数（忽略）
            
        Yields:
            str: 流式回复内容片段
        """
        self.log_request("stream_chat_completion", model=model, temperature=temperature)
        
        # 获取完整响应
        full_response = await self.chat_completion(messages, model, temperature, max_tokens, **kwargs)
        
        # 模拟流式输出
        chunk_size = random.randint(5, 15)  # 随机块大小
        for i in range(0, len(full_response), chunk_size):
            chunk = full_response[i:i + chunk_size]
            yield chunk
            # 模拟流式延迟
            await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        模拟文本嵌入
        
        Args:
            texts: 文本列表
            model: 嵌入模型名称（忽略）
            **kwargs: 其他参数（忽略）
            
        Returns:
            List[List[float]]: 模拟嵌入向量列表
        """
        self.log_request("embeddings", model=model, texts_count=len(texts))
        
        # 模拟API延迟
        await asyncio.sleep(self.response_delay * 0.5)
        
        # 生成模拟嵌入向量（1536维，类似OpenAI的嵌入）
        embeddings = []
        for text in texts:
            # 基于文本内容生成伪随机向量
            random.seed(hash(text) % (2**32))
            embedding = [random.uniform(-1, 1) for _ in range(1536)]
            embeddings.append(embedding)
        
        self.log_response("embeddings", len(embeddings))
        return embeddings
    
    async def health_check(self) -> bool:
        """
        模拟健康检查
        
        Returns:
            bool: 始终返回True（模拟服务总是可用）
        """
        # 模拟检查延迟
        await asyncio.sleep(0.1)
        return True
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "mock"
    
    async def close(self):
        """关闭客户端（模拟实现，无需实际操作）"""
        self.logger.info("关闭模拟AI客户端")
        pass 