"""
基础面试官类
所有面试官类型的基类，定义共同接口和功能
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

from ..services.ai.ai_service_manager import ai_service_manager
from ..services.ai.crewai_integration import crewai_integration

# 设置日志
logger = logging.getLogger(__name__)


class BaseInterviewer(ABC):
    """
    面试官基类
    定义所有面试官必须实现的接口和共有功能
    """
    
    def __init__(self, name: str, role: str, description: str, interviewer_id: str):
        """
        初始化面试官
        
        Args:
            name: 面试官姓名
            role: 面试官角色
            description: 面试官描述
            interviewer_id: 面试官ID（用于CrewAI集成）
        """
        self.name = name
        self.role = role
        self.description = description
        self.interviewer_id = interviewer_id
        self.ai_manager = ai_service_manager
        self.crewai = crewai_integration
        
        logger.info(f"初始化面试官: {self.name} ({self.role})")
    
    async def generate_response(self, messages: List[Dict[str, Any]], position: str = "通用职位", difficulty: str = "medium") -> str:
        """
        生成面试官回复（使用CrewAI）
        
        Args:
            messages: 面试消息历史
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            str: 面试官的回复内容
        """
        logger.info(f"生成{self.role}回复")
        
        try:
            # 使用CrewAI进行面试回复生成
            response = await self.crewai.conduct_interview_round(
                interviewer_type=self.interviewer_id,
                messages=messages,
                position=position,
                difficulty=difficulty
            )
            
            return response
            
        except Exception as e:
            logger.error(f"生成{self.role}回复失败: {str(e)}")
            # 降级到直接AI服务调用
            return await self._fallback_generate_response(messages)
    
    async def _fallback_generate_response(self, messages: List[Dict[str, Any]]) -> str:
        """
        降级回复生成（直接使用AI服务）
        
        Args:
            messages: 面试消息历史
            
        Returns:
            str: 面试官的回复内容
        """
        try:
            # 构建系统提示
            system_prompt = f"""你是一位{self.role}，名字是{self.name}。{self.description}
            
请根据对话历史，以专业、友好的方式回复候选人。你的回复应该：
1. 符合你的角色特点
2. 基于候选人的回答提出合适的后续问题
3. 保持面试的专业性和连贯性
4. 适当给予鼓励和指导"""
            
            # 构建消息列表
            formatted_messages = [{"role": "system", "content": system_prompt}]
            
            # 添加对话历史
            for msg in messages[-10:]:  # 只取最近10条消息
                if msg.get("sender_type") == "user":
                    formatted_messages.append({
                        "role": "user", 
                        "content": msg.get("content", "")
                    })
                elif msg.get("sender_type") == "interviewer":
                    formatted_messages.append({
                        "role": "assistant", 
                        "content": msg.get("content", "")
                    })
            
            # 调用AI服务
            response = await self.ai_manager.chat_completion(
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response
            
        except Exception as e:
            logger.error(f"降级回复生成失败: {str(e)}")
            return self._get_default_response()
    
    async def generate_questions(self, position: str, difficulty: str, resume_text: str = None) -> List[str]:
        """
        生成面试问题
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            resume_text: 简历文本内容（可选）
            
        Returns:
            List[str]: 面试问题列表
        """
        logger.info(f"生成{self.role}面试问题: 职位={position}, 难度={difficulty}")
        
        try:
            # 构建问题生成提示
            prompt = f"""作为{self.role}，请为{position}职位生成5个{difficulty}难度的面试问题。

角色描述：{self.description}

要求：
1. 问题应该符合{self.role}的特点
2. 难度等级：{difficulty}
3. 针对职位：{position}
"""
            
            if resume_text:
                prompt += f"\n候选人简历信息：{resume_text[:500]}..."  # 限制简历长度
            
            prompt += "\n请返回5个具体的面试问题，每行一个问题。"
            
            # 调用AI服务生成问题
            response = await self.ai_manager.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=800
            )
            
            # 解析问题列表
            questions = [q.strip() for q in response.split('\n') if q.strip() and not q.strip().startswith('#')]
            questions = [q for q in questions if len(q) > 10]  # 过滤太短的问题
            
            return questions[:5]  # 最多返回5个问题
            
        except Exception as e:
            logger.error(f"生成{self.role}面试问题失败: {str(e)}")
            return self._get_default_questions()
    
    async def generate_feedback(self, messages: List[Dict[str, Any]], position: str = "通用职位") -> Dict[str, Any]:
        """
        生成面试评估反馈
        
        Args:
            messages: 面试消息历史
            position: 面试职位
            
        Returns:
            Dict[str, Any]: 评估反馈数据
        """
        logger.info(f"生成{self.role}面试评估反馈")
        
        try:
            # 提取用户回答
            user_responses = self._extract_user_responses(messages)
            
            if not user_responses:
                return self._get_default_feedback()
            
            # 构建评估提示
            prompt = f"""作为{self.role}，请对候选人在{position}职位面试中的表现进行评估。

角色描述：{self.description}

候选人的回答：
{chr(10).join([f"{i+1}. {resp}" for i, resp in enumerate(user_responses)])}

请从你的专业角度评估候选人，包括：
1. 在你负责的评估维度上的表现（1-10分）
2. 主要优势（2-3点）
3. 需要改进的方面（2-3点）
4. 具体建议

请以JSON格式返回评估结果，包含score、strengths、improvements、suggestions字段。"""
            
            # 调用AI服务生成评估
            response = await self.ai_manager.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # 较低温度确保评估的一致性
                max_tokens=800
            )
            
            # 尝试解析JSON
            try:
                import json
                feedback_data = json.loads(response)
            except json.JSONDecodeError:
                # 如果解析失败，返回文本格式的反馈
                feedback_data = {
                    "score": 7,
                    "content": response,
                    "interviewer_id": self.interviewer_id,
                    "name": self.name,
                    "role": self.role
                }
            
            # 确保包含必要字段
            feedback_data.update({
                "interviewer_id": self.interviewer_id,
                "name": self.name,
                "role": self.role
            })
            
            return feedback_data
            
        except Exception as e:
            logger.error(f"生成{self.role}面试评估反馈失败: {str(e)}")
            return self._get_default_feedback()
    
    def _extract_user_responses(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        从消息历史中提取用户回答
        
        Args:
            messages: 面试消息历史
            
        Returns:
            List[str]: 用户回答列表
        """
        return [msg["content"] for msg in messages if msg.get("sender_type") == "user"]
    
    def _extract_conversation_history(self, messages: List[Dict[str, Any]], limit: int = 10) -> str:
        """
        提取对话历史并格式化为字符串
        
        Args:
            messages: 面试消息历史
            limit: 最大消息数量限制
            
        Returns:
            str: 格式化的对话历史
        """
        # 限制最近的消息数量
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        # 格式化对话历史
        history = ""
        for msg in recent_messages:
            if msg["sender_type"] == "user":
                history += f"求职者: {msg['content']}\n"
            elif msg["sender_type"] == "interviewer":
                interviewer_id = msg.get("interviewer_id", "未知")
                history += f"面试官({interviewer_id}): {msg['content']}\n"
            else:
                history += f"系统: {msg['content']}\n"
        
        return history
    
    @abstractmethod
    def _get_default_response(self) -> str:
        """获取默认回复（子类实现）"""
        pass
    
    @abstractmethod
    def _get_default_questions(self) -> List[str]:
        """获取默认问题列表（子类实现）"""
        pass
    
    @abstractmethod
    def _get_default_feedback(self) -> Dict[str, Any]:
        """获取默认反馈（子类实现）"""
        pass
