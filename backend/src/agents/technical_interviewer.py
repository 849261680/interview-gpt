"""
技术面试官实现
负责技术相关的面试问题和评估
"""
from typing import List, Dict, Any
# 临时注释掉crewai依赖
# from crewai import Agent, Task
from .base_interviewer import BaseInterviewer
import logging
import asyncio
import random
import json
from .prompts.technical_prompts import (
    TECHNICAL_INTERVIEWER_PROMPT,
    TECHNICAL_QUESTION_PROMPT,
    TECHNICAL_FEEDBACK_PROMPT
)

# 设置日志
logger = logging.getLogger(__name__)

class TechnicalInterviewer(BaseInterviewer):
    """
    技术面试官
    专注于评估候选人的技术能力、问题解决能力和技术深度
    """
    
    def __init__(self):
        """初始化技术面试官"""
        super().__init__(
            name="张工",
            role="技术面试官",
            description="资深技术专家，关注技术深度和解决问题能力",
            interviewer_id="technical"
        )
    
    def _create_agent(self):
        """
        创建技术面试官的模拟Agent（临时实现）
        
        Returns:
            dict: 模拟Agent对象
        """
        logger.info(f"创建模拟Agent: 技术面试官")
        
        # 返回一个字典来模拟代替Agent对象
        return {
            "role": "技术面试官",
            "goal": "评估候选人的技术能力和解决问题的能力",
            "backstory": "你是一位资深技术专家，有10年以上开发经验，精通多种编程语言和技术栈。"
        }
    
    async def generate_response(self, messages: List[Dict[str, Any]], position: str = "通用职位", difficulty: str = "medium") -> str:
        """
        生成面试官对话回复
        
        Args:
            messages: 消息历史
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            str: 面试官回复文本
        """
        logger.info(f"技术面试官生成回复")
        
        # 使用基类的CrewAI集成方法
        try:
            return await super().generate_response(messages, position, difficulty)
        except Exception as e:
            logger.error(f"CrewAI生成回复失败，使用降级实现: {e}")
            
            # 降级实现：预定义的技术面试官回复
            responses = [
                "能否详细描述一下您最近参与的一个技术项目？具体使用了哪些技术栈？",
                "你如何解决项目中遇到的性能瓶颈问题？能给出一个具体的例子吗？",
                "请描述一下你在开发过程中如何保证代码质量？你使用了哪些工具和方法？",
                "如果你需要优化一个大数据处理系统，你会从哪些方面着手？",
                "您能分享一下您如何学习新技术的吗？您最近学习了哪些新技术？",
                "非常感谢您的详细回答。能否再深入描述一下您在项目中遇到的技术难点及其解决方案？",
                "如果您需要设计一个高并发的系统，您会使用哪些架构模式？为什么？"
            ]
            
            # 随机选择一个回复
            response = random.choice(responses)
            logger.debug(f"技术面试官生成的回复: {response}")
            
            return response
    
    async def generate_questions(self, position: str, difficulty: str, resume_text: str = None) -> List[str]:
        """
        生成技术面试问题
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            resume_text: 简历文本内容（可选）
            
        Returns:
            List[str]: 面试问题列表
        """
        logger.info(f"生成技术面试问题: 职位={position}, 难度={difficulty}")
        
        # 模拟问题列表，实际项目中应该替换为真实的LLM调用
        questions = [
            "请描述一下您最近完成的项目中使用的技术栈和架构设计。",
            "您是如何处理高并发场景下的性能优化问题的？",
            "能否分享一个您在开发过程中遇到的棘手的bug，以及您是如何解决的？",
            "如果您需要设计一个分布式系统，您会考虑哪些因素和技术选型？",
            "请说明您对微服务架构的理解，以及其优缺点。"
        ]
        
        # 根据职位和难度调整问题
        if "AI" in position or "Machine Learning" in position:
            questions.extend([
                "请解释一下您对深度学习和机器学习的区别的理解。",
                "您如何处理机器学习模型中的过拟合问题？",
                "请描述一下您使用过的深度学习框架及其对比。"
            ])
        elif "Backend" in position or "后端" in position:
            questions.extend([
                "请解释一下您如何设计和实现一个高并发的API服务。",
                "您如何优化数据库查询性能？",
                "请讲解一下您对事务一致性和CAP定理的理解。"
            ])
        
        # 根据难度调整
        if difficulty.lower() == "hard" or difficulty.lower() == "困难":
            questions.extend([
                "请设计一个解决分布式系统中数据一致性问题的方案。",
                "如何在不影响用户体验的情况下进行系统重构？",
                "请分析一个复杂算法的时间和空间复杂度，并提出优化方案。"
            ])
        
        # 根据简历内容定制问题
        if resume_text and len(resume_text) > 100:
            logger.info("根据简历内容生成定制问题")
            # 这里在实际项目中应该调用LLM基于简历内容生成定制问题
            questions.append(f"根据您的简历，您在{position}项目中担任了什么角色，遇到了哪些技术挑战？")
        
        # 随机打乱问题列表，选择5-8个问题
        random.shuffle(questions)
        return questions[:min(8, len(questions))]

    async def generate_feedback(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成技术面试评估反馈
        
        Args:
            messages: 面试消息历史
            
        Returns:
            Dict[str, Any]: 评估反馈数据
        """
        logger.info("生成技术面试评估反馈")
        
        # 提取职位信息（如果有）
        position = "技术开发"  # 默认职位
        for msg in messages:
            if msg.get("metadata") and "position" in msg["metadata"]:
                position = msg["metadata"]["position"]
                break
        
        # 提取对话历史
        conversation_history = self._extract_conversation_history(messages)
        
        # 模拟评估反馈，实际项目中应该替换为真实的LLM调用
        feedback = {
            "technical_knowledge": {
                "score": 85,
                "feedback": "候选人展示了扎实的技术基础知识，对所用技术栈有较深理解。"
            },
            "problem_solving": {
                "score": 82,
                "feedback": "解决问题的思路清晰，能够系统性分析问题，但在某些复杂场景的处理上有待提高。"
            },
            "code_quality": {
                "score": 88,
                "feedback": "代码风格良好，注重可维护性和可读性，展示了良好的工程实践。"
            },
            "strengths": [
                "技术基础扎实，对核心概念理解深入",
                "善于分析问题，解决方案考虑周全",
                "持续学习新技术的积极性高"
            ],
            "improvements": [
                "可以加强系统设计方面的经验",
                "在高并发和分布式系统方面需要更多实践",
                "建议拓展更多跨领域的技术知识"
            ],
            "overall_feedback": "候选人技术基础扎实，解决问题能力强，是一位有潜力的技术人才。建议在系统设计和架构方面进一步提升。"
        }
        
        return feedback

    def _get_default_response(self) -> str:
        """获取默认回复"""
        return "感谢您的回答。能否详细介绍一下您在技术方面的经验，特别是在编程和系统设计方面的实践？"
    
    def _get_default_questions(self) -> List[str]:
        """获取默认技术面试问题"""
        return [
            "请详细介绍一下您在Python开发方面的经验，包括使用过的框架和项目实例。",
            "能否描述一下您对面向对象编程的理解？请举例说明封装、继承和多态的概念。",
            "您在项目中是如何处理异常和错误的？请分享一些最佳实践。",
            "请解释一下数据库索引的作用，以及在什么情况下应该创建索引。",
            "您对微服务架构有什么了解？它相比单体架构有哪些优势和挑战？"
        ]
    
    def _get_default_feedback(self) -> Dict[str, Any]:
        """获取默认技术面试反馈"""
        return {
            "interviewer_id": self.interviewer_id,
            "name": self.name,
            "role": self.role,
            "score": 7,
            "strengths": [
                "具备基础的技术理解能力",
                "回答问题时思路清晰"
            ],
            "improvements": [
                "需要加强技术深度的理解",
                "可以多分享具体的项目经验"
            ],
            "suggestions": [
                "建议多做一些技术项目来积累经验",
                "可以深入学习相关技术栈的最佳实践"
            ]
        }
