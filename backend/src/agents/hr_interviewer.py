"""
HR面试官实现
负责评估候选人的职业素养、文化匹配度和职业发展
"""
from typing import List, Dict, Any
# 临时注释掉crewai依赖
# from crewai import Agent, Task
from .base_interviewer import BaseInterviewer
import logging
import asyncio
import random
import json
from .prompts.hr_prompts import (
    HR_INTERVIEWER_PROMPT,
    HR_QUESTION_PROMPT,
    HR_FEEDBACK_PROMPT
)

# 设置日志
logger = logging.getLogger(__name__)

class HRInterviewer(BaseInterviewer):
    """
    HR面试官
    专注于评估候选人的职业素养、沟通能力和文化匹配度
    """
    
    def __init__(self):
        """初始化HR面试官"""
        super().__init__(
            name="李萍",
            role="HR面试官",
            description="人力资源总监，关注职业规划和公司文化匹配度",
            interviewer_id="hr"
        )
    
    def _create_agent(self):
        """
        创建HR面试官的模拟Agent（临时实现）
        
        Returns:
            dict: 模拟Agent对象
        """
        logger.info(f"创建模拟Agent: HR面试官")
        
        # 返回一个字典来模拟代替Agent对象
        return {
            "role": "HR面试官",
            "goal": "评估候选人的职业素养、沟通能力和文化匹配度",
            "backstory": "你是一位经验丰富的人力资源总监，有8年以上招聘经验。你擅长评估候选人的软技能、职业动机和长期发展潜力。"
        }
    
    async def generate_response(self, messages: List[Dict[str, Any]], position: str = "通用职位", difficulty: str = "medium") -> str:
        """
        生成HR面试官的回复
        
        Args:
            messages: 面试消息历史
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            str: 面试官的回复内容
        """
        logger.info("生成HR面试官回复")
        
        # 使用基类的CrewAI集成方法
        try:
            return await super().generate_response(messages, position, difficulty)
        except Exception as e:
            logger.error(f"CrewAI生成回复失败，使用降级实现: {e}")
            
            # 降级实现：预定义的HR面试官回复
            responses = [
                "感谢您的分享。能否描述一下您理想的工作环境和公司文化是什么样的？",
                "您认为什么样的团队氛围能让您发挥最大的潜力？",
                "非常感谢您的回答。接下来，我想了解一下您对职业发展的规划。",
                "您对未来3-5年的职业发展有什么计划？",
                "您为什么选择我们公司？您对这个职位有什么期待？",
                "您在之前的工作中最有成就感的事情是什么？",
                "您如何平衡工作和生活？您认为什么样的工作节奏适合您？"
            ]
            
            # 随机选择一个回复
            response = random.choice(responses)
            logger.debug(f"HR面试官生成的回复: {response}")
            
            return response
    
    async def generate_questions(self, position: str, difficulty: str, resume_text: str = None) -> List[str]:
        """
        生成HR面试问题
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            resume_text: 简历文本内容（可选）
            
        Returns:
            List[str]: 面试问题列表
        """
        logger.info(f"生成HR面试问题: 职位={position}, 难度={difficulty}")
        
        try:
            # 直接返回预定义的问题列表，不使用Task
            questions = [
                "请简单介绍一下您自己，以及为什么对这个职位感兴趣？",
                "您理想的工作环境和团队文化是什么样的？",
                "您能分享一下您的长期职业规划吗？",
                "您如何处理工作中的压力和挑战？",
                "在您过去的工作经历中，您最自豪的成就是什么？",
                "您为什么选择离开上一份工作？",
                "您认为您的哪些品质和经验最适合这个职位？"
            ]
            
            # 根据难度调整问题数量和深度
            if difficulty == "easy":
                return questions[:3]
            elif difficulty == "medium":
                return questions[:5]
            else:  # hard
                return questions
                
        except Exception as e:
            logger.error(f"生成HR面试问题失败: {str(e)}")
            return [
                "请简单介绍一下您自己，以及为什么对这个职位感兴趣？",
                "您对未来的职业发展有什么规划？",
                "您认为您的哪些特质最适合这个职位？"
            ]
    
    async def generate_feedback(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成HR面试评估反馈
        
        Args:
            messages: 面试消息历史
            
        Returns:
            Dict[str, Any]: 评估反馈数据
        """
        logger.info("生成HR面试评估反馈")
        
        # 提取用户回答
        user_responses = self._extract_user_responses(messages)
        
        # 提取对话历史
        conversation_history = self._extract_conversation_history(messages)
        
        try:
            # 直接返回模拟评估反馈，不使用Task
            feedback = {
                "communication": {
                    "score": 90,
                    "feedback": "候选人表达清晰，逻辑性强，能够准确传达自己的想法和经验。"
                },
                "professionalism": {
                    "score": 87,
                    "feedback": "展示了良好的职业素养，回答专业且成熟，表现出对工作的认真态度。"
                },
                "culture_fit": {
                    "score": 85,
                    "feedback": "候选人的价值观与公司文化较为契合，注重团队协作和持续学习。"
                },
                "career_planning": {
                    "score": 88,
                    "feedback": "职业规划清晰且合理，展示了对个人发展和行业趋势的良好认识。"
                },
                "strengths": [
                    "沟通表达能力出色，能够清晰传达复杂概念",
                    "职业规划清晰，对自身发展有明确目标",
                    "团队意识强，注重协作和共同成长",
                    "积极主动的学习态度和适应能力"
                ],
                "improvements": [
                    "可以进一步提升对公司业务模式的理解",
                    "在处理工作冲突的例子中可以更加主动",
                    "建议增强对行业趋势的关注和分析"
                ],
                "overall_feedback": "候选人整体表现优秀，展示了良好的沟通能力、职业素养和文化匹配度。职业规划清晰且与岗位发展路径契合。建议进入下一轮面试，是很有潜力的人选。"
            }
            
            return feedback
                
        except Exception as e:
            logger.error(f"生成HR面试评估反馈失败: {str(e)}")
            return {
                "communication": {"score": 80, "feedback": "沟通表达能力良好。"},
                "professionalism": {"score": 75, "feedback": "职业素养符合要求。"},
                "culture_fit": {"score": 80, "feedback": "与公司文化有较好匹配度。"},
                "career_planning": {"score": 75, "feedback": "职业规划合理。"},
                "strengths": ["沟通能力强", "职业态度积极"],
                "improvements": ["建议加强行业认知"],
                "overall_feedback": "候选人整体表现良好，建议考虑进入下一轮面试。"
            }
    
    def _get_default_response(self) -> str:
        """获取默认回复"""
        return "感谢您的回答。能否详细介绍一下您的职业规划，以及您认为这个职位如何帮助您实现职业目标？"
    
    def _get_default_questions(self) -> List[str]:
        """获取默认HR面试问题"""
        return [
            "请简单介绍一下您自己，包括您的教育背景和工作经历。",
            "您为什么想要加入我们公司？对这个职位有什么期待？",
            "请描述一下您理想的工作环境和团队氛围。",
            "您的职业规划是什么？未来3-5年希望在哪些方面有所发展？",
            "您在之前的工作中遇到过什么挑战？是如何解决的？"
        ]
    
    def _get_default_feedback(self) -> Dict[str, Any]:
        """获取默认HR面试反馈"""
        return {
            "interviewer_id": self.interviewer_id,
            "name": self.name,
            "role": self.role,
            "score": 7,
            "strengths": [
                "具备良好的沟通表达能力",
                "职业态度积极正面"
            ],
            "improvements": [
                "可以更详细地分享具体工作经验",
                "建议加强对公司和行业的了解"
            ],
            "suggestions": [
                "建议在面试前深入了解公司文化和业务",
                "可以准备更多具体的工作案例来展示能力"
            ]
        }
