"""
总面试官实现
负责汇总前面面试内容，做出是否推荐的决定，输出面试评估报告
"""
from typing import List, Dict, Any
# 临时注释掉crewai依赖
# from crewai import Agent, Task
from .base_interviewer import BaseInterviewer
import logging
import asyncio
import random
import json
from .prompts.senior_interviewer_prompts import (
    SENIOR_INTERVIEWER_PROMPT,
    SENIOR_INTERVIEWER_ASSESSMENT_PROMPT,
    SENIOR_INTERVIEWER_ADVICE_PROMPT
)

# 设置日志
logger = logging.getLogger(__name__)

class SeniorInterviewer(BaseInterviewer):
    """
    总面试官
    专注于汇总前面面试内容，做出是否推荐的决定，输出面试评估报告
    """
    
    def __init__(self):
        """初始化总面试官"""
        super().__init__(
            name="张总",
            role="总面试官",
            description="高级总监，负责最终评估和决策"
        )
    
    def _create_agent(self):
        """
        创建总面试官的模拟Agent（临时实现）
        
        Returns:
            dict: 模拟Agent对象
        """
        logger.info(f"创建模拟Agent: 总面试官")
        
        # 返回一个字典来模拟代替Agent对象
        return {
            "role": "总面试官",
            "goal": "做出最终评估和录用决定",
            "backstory": "你是一位高级总监，负责最终录用决定。你对公司的所有部门和业务都非常了解。"
        }
    
    async def generate_response(self, messages: List[Dict[str, Any]]) -> str:
        """
        生成总面试官的回复
        
        Args:
            messages: 面试消息历史
            
        Returns:
            str: 面试官的回复内容
        """
        logger.info(f"总面试官生成回复")
        
        # 提取面试历史
        interview_history = self._format_interview_history(messages)
        
        # 获取候选人的最后一条消息
        last_user_message = self._get_last_user_message(messages)
        
        if not last_user_message:
            # 如果没有用户消息，生成初始问题
            return "您好，我是张总，本次面试的总面试官。前面几位面试官已经和您进行了交流，我这边有几个综合性的问题想请您回答。首先，结合您的经历，您认为自己最适合我们公司的哪个岗位，为什么？"
        
        # 生成模拟面试问题
        logger.info("生成模拟面试问题")
        
        try:
            # 生成面试问题
            possible_questions = [
                "根据您前面的面试表现，您认为自己最大的优势是什么？这些优势如何帮助您在未来的工作中发挥价值？",
                "总结一下您的职业规划和目标，您如何看待我们公司在您职业发展中的作用？",
                "如果加入我们团队，您认为自己需要多长时间能够快速融入并产生价值？您会采取哪些具体措施？"
            ]
            response = random.choice(possible_questions)
            
            # 移除可能的引号和多余空格
            response = response.strip().strip('"\'')
            
            return response
            
        except Exception as e:
            logger.error(f"总面试官生成回复失败: {str(e)}")
            # 返回一个通用回复
            return "感谢您的分享。综合前面几轮面试，我想请您总结一下您认为自己的核心优势是什么，以及加入我们团队后，您计划如何快速融入并创造价值？"
    
    async def generate_final_assessment(self, 
                                       technical_content: str,
                                       hr_content: str,
                                       product_content: str,
                                       behavioral_content: str) -> Dict[str, Any]:
        """
        生成最终面试评估报告
        
        Args:
            technical_content: 技术面试内容
            hr_content: HR面试内容
            product_content: 产品经理面试内容
            behavioral_content: 行为面试内容
            
        Returns:
            Dict[str, Any]: 最终面试评估报告
        """
        logger.info(f"总面试官生成最终评估报告")
        
        logger.info("生成模拟评估报告")
        
        try:
            # 生成模拟评估报告
            assessment = "候选人在技术面试、HR面试、产品面试和行为面试中表现良好。"
            
            # 解析评估报告
            assessment_data = self._parse_assessment(assessment)
            
            # 生成模拟改进建议
            logger.info("生成模拟改进建议")
            advice = "建议候选人加强系统设计和技术架构方面的能力，同时提升跨部门协作的沟通能力。"
            
            # 合并评估报告和建议
            assessment_data["improvement_advice"] = advice
            
            return assessment_data
            
        except Exception as e:
            logger.error(f"总面试官生成评估报告失败: {str(e)}")
            # 返回一个通用评估报告
            return self._generate_fallback_assessment()
    
    def _parse_assessment(self, assessment: str) -> Dict[str, Any]:
        """
        解析评估报告文本为结构化数据
        
        Args:
            assessment: 评估报告文本
            
        Returns:
            Dict[str, Any]: 结构化评估数据
        """
        # 简单实现，在实际应用中应该使用更复杂的解析逻辑
        try:
            # 提取评分和各项指标
            technical_score = 4
            professional_score = 3
            product_thinking_score = 4
            behavioral_score = 4
            culture_fit_score = 3
            
            # 计算总分
            total_score = (technical_score + professional_score + 
                           product_thinking_score + behavioral_score + 
                           culture_fit_score) / 5
            
            # 判断推荐级别
            if total_score >= 4.5:
                recommendation = "强烈推荐"
            elif total_score >= 3.5:
                recommendation = "推荐"
            elif total_score >= 2.5:
                recommendation = "待定"
            else:
                recommendation = "不推荐"
            
            return {
                "technical_score": technical_score,
                "professional_score": professional_score,
                "product_thinking_score": product_thinking_score,
                "behavioral_score": behavioral_score,
                "culture_fit_score": culture_fit_score,
                "total_score": total_score,
                "recommendation": recommendation,
                "strengths": [
                    "技术知识扎实",
                    "沟通表达能力强",
                    "产品思维清晰"
                ],
                "improvements": [
                    "可以加强团队协作经验",
                    "建议提升业务价值理解"
                ],
                "recommended_position": "高级开发工程师",
                "overall_assessment": assessment
            }
            
        except Exception as e:
            logger.error(f"解析评估报告失败: {str(e)}")
            return self._generate_fallback_assessment()
    
    def _generate_fallback_assessment(self) -> Dict[str, Any]:
        """
        生成备用评估报告
        
        Returns:
            Dict[str, Any]: 备用评估报告
        """
        return {
            "technical_score": 3,
            "professional_score": 3,
            "product_thinking_score": 3,
            "behavioral_score": 3,
            "culture_fit_score": 3,
            "total_score": 3.0,
            "recommendation": "待定",
            "strengths": [
                "沟通表达流畅",
                "基础技术能力良好",
                "团队协作意识强"
            ],
            "improvements": [
                "建议加强专业深度",
                "可以提升解决复杂问题的能力"
            ],
            "recommended_position": "开发工程师",
            "overall_assessment": "候选人整体表现中等，展现了基本的技术能力和沟通能力。建议安排进一步面试以深入评估其技术深度和解决复杂问题的能力。",
            "improvement_advice": "建议候选人加强技术深度学习，提升解决复杂问题的能力，积累更多实际项目经验。"
        }
