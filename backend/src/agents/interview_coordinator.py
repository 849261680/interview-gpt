"""面试协调员模块

负责协调整个面试流程，安排面试官，分配任务，收集面试结果，并生成最终的面试报告。
"""

from typing import List, Dict, Any, Optional
import logging

from .base_interviewer import BaseInterviewer
from ..services.ai.ai_service_manager import ai_service_manager
from ..services.ai.crewai_integration import crewai_integration

# 设置日志
logger = logging.getLogger(__name__)


class InterviewCoordinator(BaseInterviewer):
    """
    面试协调员类
    
    负责协调整个面试流程，安排面试官，收集面试结果，生成面试报告
    """
    
    def __init__(self):
        """
        初始化面试协调员
        """
        super().__init__(
            name="王协调",
            role="面试协调员",
            description="你是一位经验丰富的面试协调员，擅长安排面试日程，协调面试官，收集面试结果，并生成最终的面试报告。",
            interviewer_id="coordinator"
        )
        logger.info("初始化面试协调员")
    
    async def _get_default_questions(self, position: str, difficulty: str) -> List[str]:
        """
        获取默认问题列表
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            List[str]: 问题列表
        """
        return [
            "请简单介绍一下你自己和你的工作经验。",
            "你为什么对我们公司和这个职位感兴趣？",
            "你能描述一下你期望的工作环境和团队文化吗？",
            "你对今天的面试有什么期望或问题吗？"
        ]
    
    async def _get_default_response(self, messages: List[Dict[str, Any]]) -> str:
        """
        获取默认回复
        
        Args:
            messages: 面试消息历史
            
        Returns:
            str: 默认回复
        """
        if not messages:
            return "你好，欢迎参加我们的面试。我是面试协调员，负责协调整个面试流程。今天的面试将由技术面试官、产品面试官、行为面试官和HR面试官共同完成。首先，请简单介绍一下你自己和你的工作经验。"
        
        # 根据当前面试阶段给出不同的回复
        last_message = messages[-1]
        if last_message.get("sender_type") == "user":
            return "谢谢你的回答。我们的面试官团队已经准备好了，接下来将由技术面试官进行提问，请做好准备。"
        
        return "我们的面试即将结束，感谢你参加今天的面试。稍后我们会整理面试结果，并尽快给你反馈。你还有什么问题想问我们吗？"
    
    async def _get_default_feedback(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取默认反馈
        
        Args:
            messages: 面试消息历史
            
        Returns:
            Dict[str, Any]: 反馈内容
        """
        return {
            "overall": "候选人在面试中展现出良好的沟通能力和专业素养，面试过程顺利。",
            "score": 8,
            "strengths": ["沟通清晰", "回答有条理", "态度积极"],
            "weaknesses": ["部分问题回答不够深入"],
            "recommendations": "建议进入下一轮面试"
        }
    
    async def start_interview(self, position: str, difficulty: str, resume: str = "") -> Dict[str, Any]:
        """
        启动完整面试流程
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            resume: 简历内容（可选）
            
        Returns:
            Dict: 面试结果，包含状态和报告
        """
        logger.info(f"启动完整面试流程：职位 {position}，难度 {difficulty}")
        
        # 检查CrewAI是否可用
        if not self.crewai.is_available():
            logger.warning("CrewAI不可用，无法使用多Agent面试系统")
            return {
                "status": "error",
                "message": "CrewAI不可用，无法启动多Agent面试系统"
            }
        
        try:
            # 执行完整面试流程
            result = await self.crewai.conduct_interview(
                resume_context=resume,
                position=position,
                difficulty=difficulty
            )
            
            logger.info("完整面试流程执行完成")
            return result
            
        except Exception as e:
            logger.error(f"执行完整面试流程失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def generate_interview_report(self, interview_records: List[Dict[str, Any]]) -> str:
        """
        生成面试报告
        
        Args:
            interview_records: 面试记录列表
            
        Returns:
            str: 面试报告
        """
        logger.info("生成面试报告")
        
        # 构建系统提示
        system_prompt = f"""你是一位经验丰富的面试协调员，负责生成最终的面试报告。
        
请根据以下面试记录，生成一份全面、客观的面试报告。报告应包括：
1. 候选人基本信息
2. 各轮面试的主要内容和亮点
3. 候选人的优势和不足
4. 技术能力评分 (1-10分)
5. 产品能力评分 (1-10分)
6. 综合素质评分 (1-10分)
7. 文化匹配度评分 (1-10分)
8. 总体推荐等级 (强烈推荐/推荐/待定/不推荐)
9. 改进建议

请确保报告格式清晰，内容客观专业。"""
        
        # 构建面试记录文本
        interview_text = ""
        for record in interview_records:
            sender_type = record.get("sender_type", "")
            sender_name = record.get("sender_name", "")
            content = record.get("content", "")
            
            if sender_type == "user":
                interview_text += f"候选人: {content}\n\n"
            else:
                interview_text += f"{sender_name}: {content}\n\n"
        
        # 使用AI生成报告
        try:
            response = await self.ai_manager.generate_content(
                system_prompt=system_prompt,
                user_prompt=f"以下是面试记录，请生成面试报告：\n\n{interview_text}",
                max_tokens=2000
            )
            
            logger.info("面试报告生成完成")
            return response
            
        except Exception as e:
            logger.error(f"生成面试报告失败: {str(e)}")
            return f"生成面试报告失败: {str(e)}"
    
    async def assign_next_interviewer(self, current_interviewer: str, interview_records: List[Dict[str, Any]]) -> str:
        """
        分配下一位面试官
        
        Args:
            current_interviewer: 当前面试官ID
            interview_records: 面试记录列表
            
        Returns:
            str: 下一位面试官ID
        """
        logger.info(f"分配下一位面试官，当前面试官: {current_interviewer}")
        
        # 面试官顺序
        interviewer_sequence = ["coordinator", "technical", "product", "behavioral", "hr", "coordinator"]
        
        try:
            # 获取当前面试官在序列中的位置
            current_index = interviewer_sequence.index(current_interviewer)
            # 返回下一位面试官
            next_interviewer = interviewer_sequence[current_index + 1]
            
            logger.info(f"下一位面试官: {next_interviewer}")
            return next_interviewer
            
        except (ValueError, IndexError):
            # 如果出错，返回协调员
            logger.warning(f"无法确定下一位面试官，返回协调员")
            return "coordinator"
