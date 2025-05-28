"""
产品经理面试官实现
负责评估候选人的产品思维、用户视角和跨职能沟通能力
"""
from typing import List, Dict, Any
# 临时注释掉crewai依赖
# from crewai import Agent, Task
from .base_interviewer import BaseInterviewer
import logging
import asyncio
import random
import json
from .prompts.product_manager_prompts import (
    PRODUCT_MANAGER_INTERVIEWER_PROMPT,
    PRODUCT_MANAGER_QUESTION_PROMPT,
    PRODUCT_MANAGER_FEEDBACK_PROMPT
)

# 设置日志
logger = logging.getLogger(__name__)

class ProductManagerInterviewer(BaseInterviewer):
    """
    产品经理面试官
    专注于评估候选人的产品思维、用户视角和跨职能沟通能力
    """
    
    def __init__(self):
        """初始化产品经理面试官"""
        super().__init__(
            name="陈经理",
            role="产品经理面试官",
            description="资深产品总监，关注产品思维和用户视角",
            interviewer_id="product_manager"
        )
    
    def _create_agent(self):
        """
        创建产品经理面试官的模拟Agent（临时实现）
        
        Returns:
            dict: 模拟Agent对象
        """
        logger.info(f"创建模拟Agent: 产品经理面试官")
        
        # 返回一个字典来模拟代替Agent对象
        return {
            "role": "产品经理面试官",
            "goal": "评估候选人的产品思维、用户视角和跨职能沟通能力",
            "backstory": "你是一位资深产品总监，有着丰富的产品规划和管理经验。你关注候选人的产品思维和用户视角。"
        }
    
    async def generate_response(self, messages: List[Dict[str, Any]], position: str = "产品经理", difficulty: str = "medium") -> str:
        """
        生成产品经理面试官的回复
        
        Args:
            messages: 面试消息历史
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            str: 面试官的回复内容
        """
        logger.info(f"产品经理面试官生成回复")
        
        # 使用基类的CrewAI集成方法
        try:
            return await super().generate_response(messages, position, difficulty)
        except Exception as e:
            logger.error(f"CrewAI生成回复失败，使用降级实现: {e}")
            
            # 降级实现：预定义的产品经理面试官回复
            responses = [
                "感谢您的分享。从产品角度看，您能否详细说明一下您是如何平衡用户需求与业务目标的？",
                "很有意思的观点。能否分享一个您参与的产品决策案例，包括您的思考过程和最终结果？",
                "您提到的用户需求很重要。您通常如何验证和优先级排序这些需求？",
                "在产品开发过程中，您如何与技术团队、设计团队协作？能否举个具体例子？",
                "您认为一个成功的产品应该具备哪些关键要素？请结合您的经验说明。",
                "面对竞争激烈的市场，您会如何制定产品策略来保持竞争优势？",
                "用户反馈对产品迭代很重要，您是如何收集和分析用户反馈的？"
            ]
            
            # 随机选择一个回复
            response = random.choice(responses)
            logger.debug(f"产品经理面试官生成的回复: {response}")
            
            return response
    
    async def generate_questions(self, position: str, difficulty: str, resume_text: str = None) -> List[str]:
        """
        生成产品经理面试问题
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            resume_text: 简历文本内容（可选）
            
        Returns:
            List[str]: 面试问题列表
        """
        logger.info(f"生成产品经理面试问题: 职位={position}, 难度={difficulty}")
        
        try:
            # 直接返回预定义的问题列表，不使用Task
            questions = [
                "请分享一个您参与过的产品项目，并说明您是如何理解和定义用户需求的？",
                "描述一次您需要在用户需求和业务目标之间做权衡的经历？",
                "您如何评估一个产品功能的优先级？请分享您的方法论。",
                "在产品开发过程中，您如何与技术、设计、运营等团队协作？",
                "请分析一个您认为成功的产品，并说明它成功的关键因素。",
                "面对用户的负面反馈，您会如何处理和改进产品？",
                "如何在快速变化的市场中保持产品的竞争力？"
            ]
            
            # 根据难度调整问题数量和深度
            if difficulty == "easy":
                return questions[:3]
            elif difficulty == "medium":
                return questions[:5]
            else:  # hard
                return questions
                
        except Exception as e:
            logger.error(f"生成产品经理面试问题失败: {str(e)}")
            return [
                "请分享一个您参与过的产品项目？",
                "您如何理解用户需求？",
                "您认为产品成功的关键是什么？"
            ]
    
    async def generate_feedback(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成产品经理面试评估反馈
        
        Args:
            messages: 面试消息历史
            
        Returns:
            Dict[str, Any]: 评估反馈数据
        """
        logger.info("生成产品经理面试评估反馈")
        
        # 提取用户回答
        user_responses = self._extract_user_responses(messages)
        
        # 提取对话历史
        conversation_history = self._extract_conversation_history(messages)
        
        try:
            # 直接返回模拟评估反馈，不使用Task
            feedback = {
                "product_thinking": {
                    "score": 85,
                    "feedback": "候选人展示了良好的产品思维，能够从用户角度思考问题，理解产品价值。"
                },
                "user_perspective": {
                    "score": 88,
                    "feedback": "对用户需求有深入理解，能够平衡用户体验与业务目标。"
                },
                "cross_functional": {
                    "score": 82,
                    "feedback": "具备跨职能协作能力，能够与技术、设计团队有效沟通。"
                },
                "business_value": {
                    "score": 80,
                    "feedback": "对业务价值有一定理解，但在商业模式分析方面可以进一步提升。"
                },
                "strengths": [
                    "产品思维清晰，能够从用户角度分析问题",
                    "具备良好的沟通表达能力",
                    "对产品生命周期有整体认知",
                    "能够结合具体案例说明观点"
                ],
                "improvements": [
                    "可以加强数据驱动的产品决策能力",
                    "建议提升对商业模式的深度理解",
                    "在产品策略制定方面需要更多实践"
                ],
                "overall_feedback": "候选人在产品思维和用户视角方面表现优秀，具备成为优秀产品经理的潜质。建议在数据分析和商业策略方面进一步提升。"
            }
            
            return feedback
                
        except Exception as e:
            logger.error(f"生成产品经理面试评估反馈失败: {str(e)}")
            return {
                "product_thinking": {"score": 75, "feedback": "产品思维能力良好。"},
                "user_perspective": {"score": 80, "feedback": "用户视角理解到位。"},
                "cross_functional": {"score": 75, "feedback": "跨职能协作能力符合要求。"},
                "business_value": {"score": 70, "feedback": "业务价值理解合理。"},
                "strengths": ["产品思维清晰", "用户导向"],
                "improvements": ["建议加强数据分析能力"],
                "overall_feedback": "候选人产品能力良好，建议考虑进入下一轮面试。"
            }
    
    def _get_default_response(self) -> str:
        """获取默认回复"""
        return "感谢您的回答。从产品角度看，您能否详细说明一下您是如何平衡用户需求与业务目标的？请结合具体案例说明。"
    
    def _get_default_questions(self) -> List[str]:
        """获取默认产品经理面试问题"""
        return [
            "请分享一个您参与过的产品项目，并说明您的角色和贡献。",
            "您如何理解和定义用户需求？请举例说明。",
            "在产品开发中，您如何平衡用户需求和业务目标？",
            "您认为一个成功的产品应该具备哪些关键要素？",
            "面对竞争激烈的市场，您会如何制定产品策略？"
        ]
    
    def _get_default_feedback(self) -> Dict[str, Any]:
        """获取默认产品经理面试反馈"""
        return {
            "interviewer_id": self.interviewer_id,
            "name": self.name,
            "role": self.role,
            "score": 7,
            "strengths": [
                "具备基础的产品思维能力",
                "能够从用户角度思考问题"
            ],
            "improvements": [
                "可以加强产品策略制定能力",
                "建议提升数据驱动决策的经验"
            ],
            "suggestions": [
                "建议多关注成功产品的案例分析",
                "可以加强对商业模式的理解"
            ]
        }
