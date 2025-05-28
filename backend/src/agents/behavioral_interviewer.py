"""
行为面试官实现
负责评估候选人的行为模式、团队协作和处理挑战的能力
"""
from typing import List, Dict, Any
# 临时注释掉crewai依赖
# from crewai import Agent, Task
from .base_interviewer import BaseInterviewer
import logging
import asyncio
import random
import json
from .prompts.behavioral_prompts import (
    BEHAVIORAL_INTERVIEWER_PROMPT,
    BEHAVIORAL_QUESTION_PROMPT,
    BEHAVIORAL_FEEDBACK_PROMPT
)

# 设置日志
logger = logging.getLogger(__name__)

class BehavioralInterviewer(BaseInterviewer):
    """
    行为面试官
    专注于评估候选人的行为模式、团队协作和处理挑战的能力
    """
    
    def __init__(self):
        """初始化行为面试官"""
        super().__init__(
            name="王总",
            role="行为面试官",
            description="部门主管，关注沟通能力和团队协作",
            interviewer_id="behavioral"
        )
    
    def _create_agent(self):
        """
        创建行为面试官的模拟Agent（临时实现）
        
        Returns:
            dict: 模拟Agent对象
        """
        logger.info(f"创建模拟Agent: 行为面试官")
        
        # 返回一个字典来模拟代替Agent对象
        return {
            "role": "行为面试官",
            "goal": "评估候选人的行为模式、团队协作和处理挑战的能力",
            "backstory": "你是一位经验丰富的部门主管，有着多年带领团队的经验。你关注候选人在实际工作中的行为表现。"
        }
    
    async def generate_response(self, messages: List[Dict[str, Any]], position: str = "通用职位", difficulty: str = "medium") -> str:
        """
        生成行为面试官的回复
        
        Args:
            messages: 面试消息历史
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            str: 面试官的回复内容
        """
        logger.info("生成行为面试官回复")
        
        # 使用基类的CrewAI集成方法
        try:
            return await super().generate_response(messages, position, difficulty)
        except Exception as e:
            logger.error(f"CrewAI生成回复失败，使用降级实现: {e}")
            
            # 降级实现：预定义的行为面试官回复
            responses = [
                "谢谢您分享这个例子。能否详细描述一下，当您遇到团队成员之间有不同意见时，您是如何协调和解决这些分歧的？",
                "请提供一个具体的例子，包括情境、您的具体行动和最终结果。",
                "感谢您的回答。接下来，我想了解一下您是如何处理工作中的高压情境的。",
                "您能分享一个您在压力下仍然成功完成任务的例子吗？",
                "这个经历很有价值。您从这次经历中学到了什么？对您后续的工作有什么影响？",
                "能否描述一下您在团队中的角色定位？您通常如何与不同性格的同事合作？",
                "请分享一个您需要快速学习新技能来完成任务的经历。"
            ]
            
            # 随机选择一个回复
            response = random.choice(responses)
            logger.debug(f"行为面试官生成的回复: {response}")
            
            return response
    
    async def generate_questions(self, position: str, difficulty: str, resume_text: str = None) -> List[str]:
        """
        生成行为面试问题
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            resume_text: 简历文本内容（可选）
            
        Returns:
            List[str]: 面试问题列表
        """
        logger.info(f"生成行为面试问题: 职位={position}, 难度={difficulty}")
        
        try:
            # 直接返回预定义的问题列表，不使用Task
            questions = [
                "请描述一个您在团队中遇到冲突的情况，以及您是如何解决的？",
                "分享一个您面临重大挑战的项目经历，您采取了哪些行动，最终结果如何？",
                "请举例说明您如何处理工作中的高压或紧急情况？",
                "描述一次您需要说服团队或上级接受您的想法的经历，您是如何做的？",
                "分享一个您犯错并从中吸取教训的经历？",
                "您是如何处理与困难团队成员合作的？请给出具体例子。",
                "描述一次您需要做出艰难决策的情况，您的思考过程是什么？"
            ]
            
            # 根据难度调整问题数量和深度
            if difficulty == "easy":
                return questions[:3]
            elif difficulty == "medium":
                return questions[:5]
            else:  # hard
                return questions
                
        except Exception as e:
            logger.error(f"生成行为面试问题失败: {str(e)}")
            return [
                "请描述一个您在团队中遇到冲突的情况，以及您是如何解决的？",
                "分享一个您面临挑战的项目经历？",
                "您是如何处理工作压力的？"
            ]
    
    async def generate_feedback(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成行为面试评估反馈
        
        Args:
            messages: 面试消息历史
            
        Returns:
            Dict[str, Any]: 评估反馈数据
        """
        logger.info("生成行为面试评估反馈")
        
        # 提取用户回答
        user_responses = self._extract_user_responses(messages)
        
        # 提取对话历史
        conversation_history = self._extract_conversation_history(messages)
        
        try:
            # 直接返回模拟评估反馈，不使用Task
            feedback = {
                "teamwork": {
                    "score": 88,
                    "feedback": "候选人展示了良好的团队协作意识，能够有效处理团队中的不同意见和冲突。"
                },
                "problem_solving": {
                    "score": 85,
                    "feedback": "解决问题的方法条理清晰，能够系统性分析问题并制定有效的行动计划。"
                },
                "communication": {
                    "score": 90,
                    "feedback": "沟通表达清晰，善于倾听，能够在团队中有效传达想法和反馈。"
                },
                "stress_handling": {
                    "score": 83,
                    "feedback": "在压力和挑战面前展现出良好的适应能力，但在某些高压情境中可以更加从容。"
                },
                "strengths": [
                    "团队协作能力强，能够有效融入团队并促进协作",
                    "沟通能力出色，表达清晰且有条理",
                    "善于分析问题并制定系统性解决方案",
                    "积极主动的工作态度，勇于承担责任"
                ],
                "improvements": [
                    "在处理复杂团队动态时可以更加灵活",
                    "建议在高压情境下保持更加冷静的判断",
                    "可以进一步提升跨部门协作的经验"
                ],
                "overall_feedback": "候选人在行为面试中表现优秀，展示了良好的团队协作能力、沟通技巧和问题解决能力。具备成为优秀团队成员的潜质，建议进入下一轮面试。"
            }
            
            return feedback
                
        except Exception as e:
            logger.error(f"生成行为面试评估反馈失败: {str(e)}")
            return {
                "teamwork": {"score": 80, "feedback": "团队协作能力良好。"},
                "problem_solving": {"score": 75, "feedback": "问题解决能力符合要求。"},
                "communication": {"score": 80, "feedback": "沟通表达能力良好。"},
                "stress_handling": {"score": 75, "feedback": "压力处理能力合理。"},
                "strengths": ["团队意识强", "沟通能力好"],
                "improvements": ["建议加强压力管理"],
                "overall_feedback": "候选人行为表现良好，建议考虑进入下一轮面试。"
            }
    
    def _get_default_response(self) -> str:
        """获取默认回复"""
        return "感谢您的分享。能否详细描述一下您在团队中遇到挑战时的具体处理方式？请提供一个具体的例子。"
    
    def _get_default_questions(self) -> List[str]:
        """获取默认行为面试问题"""
        return [
            "请描述一次您在团队中解决冲突的经历。",
            "能否分享一个您在压力下成功完成任务的例子？",
            "请举例说明您是如何学习新技能或适应新环境的。",
            "描述一次您主动承担额外责任的情况。",
            "请分享一个您从失败中学到重要经验的例子。"
        ]
    
    def _get_default_feedback(self) -> Dict[str, Any]:
        """获取默认行为面试反馈"""
        return {
            "interviewer_id": self.interviewer_id,
            "name": self.name,
            "role": self.role,
            "score": 7,
            "strengths": [
                "具备良好的团队协作意识",
                "沟通表达能力较强"
            ],
            "improvements": [
                "可以提供更多具体的行为案例",
                "建议加强在高压环境下的应对能力"
            ],
            "suggestions": [
                "建议准备更多STAR格式的行为案例",
                "可以加强对团队管理和冲突解决的学习"
            ]
        }
