"""
面试流程管理器
负责管理整个面试过程、面试官轮换和面试状态
提供实时通信和状态更新
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ...models.schemas import Interview, Message
from ...agents.interviewer_factory import InterviewerFactory
from ...schemas.interview import MessageCreate

# 设置日志
logger = logging.getLogger(__name__)

# 面试阶段定义
INTERVIEW_STAGES = {
    "introduction": {
        "description": "面试介绍阶段",
        "interviewer_id": "system",
        "max_messages": 2,
        "next_stage": "technical"
    },
    "technical": {
        "description": "技术面试阶段",
        "interviewer_id": "technical",
        "max_messages": 8,
        "next_stage": "hr"
    },
    "hr": {
        "description": "人力资源面试阶段",
        "interviewer_id": "hr",
        "max_messages": 6,
        "next_stage": "product_manager"
    },
    "product_manager": {
        "description": "产品经理面试阶段",
        "interviewer_id": "product_manager",
        "max_messages": 6,
        "next_stage": "behavioral"
    },
    "behavioral": {
        "description": "行为面试阶段",
        "interviewer_id": "behavioral",
        "max_messages": 6,
        "next_stage": "senior"
    },
    "senior": {
        "description": "总面试官阶段",
        "interviewer_id": "senior",
        "max_messages": 4,
        "next_stage": "conclusion"
    },
    "conclusion": {
        "description": "面试总结阶段",
        "interviewer_id": "system",
        "max_messages": 2,
        "next_stage": "feedback"
    },
    "feedback": {
        "description": "面试评估反馈阶段",
        "interviewer_id": "system",
        "max_messages": 1,
        "next_stage": None
    }
}


class InterviewManager:
    """
    面试流程管理器
    负责管理整个面试过程、面试官轮换和状态转换
    在原有功能的基础上增加面试阶段管理和WebSocket通信所需的功能
    """
    
    def __init__(self, interview_id: int, db: Session):
        """
        初始化面试管理器
        
        Args:
            interview_id: 面试ID
            db: 数据库会话
        """
        self.interview_id = interview_id
        self.db = db
        self.current_stage = "introduction"
        self.stage_message_count = {stage: 0 for stage in INTERVIEW_STAGES}
        self.interviewer_factory = InterviewerFactory()
        
    async def initialize_interview(self) -> None:
        """
        初始化面试，创建欢迎消息
        """
        logger.info(f"初始化面试: ID={self.interview_id}")
        
        # 使用传入的db或默认的self.db
        _db = self.db
        
        # 查询面试
        interview = _db.query(Interview).filter(Interview.id == self.interview_id).first()
        
        if not interview:
            logger.error(f"生成评估失败，面试不存在: ID={self.interview_id}")
            return
        
        # 检查面试状态
        if interview.status != "active":
            raise ValueError(f"面试状态不是活跃状态: {interview.status}")
        
        # 获取已有消息数量
        existing_messages = self.db.query(Message).filter(
            Message.interview_id == self.interview_id
        ).count()
        
        # 如果没有消息，创建欢迎消息
        if existing_messages == 0:
            welcome_message = Message(
                interview_id=self.interview_id,
                content="欢迎参加模拟面试！我们将从技术面试开始，请放松并准备好回答问题。",
                sender_type="system"
            )
            self.db.add(welcome_message)
            self.db.commit()
            
            # 更新消息计数
            self.stage_message_count["introduction"] += 1
            
            # 创建第一个面试官消息
            await self.switch_interviewer()
        else:
            # 加载当前面试阶段
            await self.load_current_stage()
    
    async def load_current_stage(self) -> None:
        """
        从消息历史加载当前面试阶段
        """
        logger.info(f"加载当前面试阶段: ID={self.interview_id}")
        
        # 获取所有面试官消息
        interviewer_messages = self.db.query(Message).filter(
            Message.interview_id == self.interview_id,
            Message.sender_type.in_(["system", "interviewer"])
        ).order_by(Message.timestamp).all()
        
        if not interviewer_messages:
            self.current_stage = "introduction"
            return
        
        # 分析消息确定当前阶段
        interviewer_counts = {}
        
        for message in interviewer_messages:
            interviewer_id = message.interviewer_id or "system"
            interviewer_counts[interviewer_id] = interviewer_counts.get(interviewer_id, 0) + 1
        
        # 查找最后一个面试官消息
        last_interviewer_message = interviewer_messages[-1]
        last_interviewer_id = last_interviewer_message.interviewer_id or "system"
        
        # 确定当前阶段
        for stage, config in INTERVIEW_STAGES.items():
            if config["interviewer_id"] == last_interviewer_id:
                self.current_stage = stage
                break
        
        # 更新阶段消息计数
        for interviewer_id, count in interviewer_counts.items():
            for stage, config in INTERVIEW_STAGES.items():
                if config["interviewer_id"] == interviewer_id:
                    self.stage_message_count[stage] = count
    
    async def process_user_message(self, message_content: str, db: Session) -> Tuple[Message, Optional[Message]]:
        """
        处理用户消息并生成面试官回复
        
        Args:
            message_content: 用户消息内容
            
        Returns:
            Dict[str, Any]: 面试官回复消息
        """
        logger.info(f"处理用户消息: 面试ID={self.interview_id}")
        
        # 保存用户消息
        user_message = Message(
            interview_id=self.interview_id,
            content=message_content,
            sender_type="user"
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # 获取面试消息历史
        messages = await self.get_interview_messages()
        
        # 确定当前面试官
        current_interviewer_id = INTERVIEW_STAGES[self.current_stage]["interviewer_id"]
        
        # 获取面试官实例
        interviewer = self.interviewer_factory.get_interviewer(current_interviewer_id)
        
        # 生成面试官回复
        try:
            response_content = await interviewer.generate_response(messages)
            
            # 保存面试官回复
            interviewer_message = Message(
                interview_id=self.interview_id,
                content=response_content,
                sender_type="interviewer" if current_interviewer_id != "system" else "system",
                interviewer_id=None if current_interviewer_id == "system" else current_interviewer_id
            )
            db.add(interviewer_message)
            db.commit()
            db.refresh(interviewer_message)
            
            # 更新阶段消息计数
            self.stage_message_count[self.current_stage] += 1
            
            # 返回用户消息和面试官回复
            return user_message, interviewer_message
            
        except Exception as e:
            logger.error(f"生成面试官回复失败: {str(e)}")
            # 创建一个通用回复
            fallback_message = Message(
                interview_id=self.interview_id,
                content="感谢您的回答。您刊才提到的内容很有见地。我想继续了解一下，您在之前的工作中是如何解决类似问题的？",
                sender_type="interviewer" if current_interviewer_id != "system" else "system",
                interviewer_id=None if current_interviewer_id == "system" else current_interviewer_id
            )
            db.add(fallback_message)
            db.commit()
            db.refresh(fallback_message)
            
            # 更新阶段消息计数
            self.stage_message_count[self.current_stage] += 1
            
            return user_message, fallback_message
    
    def should_switch_interviewer(self) -> bool:
        """
        判断是否应该切换到下一个面试官
        
        Returns:
            bool: 是否应该切换
        """
        # 获取当前阶段配置
        stage_config = INTERVIEW_STAGES[self.current_stage]
        
        # 检查消息数量是否达到阈值
        if self.stage_message_count[self.current_stage] >= stage_config["max_messages"]:
            return True
            
        return False
    
    async def switch_interviewer(self, db: Session = None) -> Optional[Dict[str, Any]]:
        """
        切换到下一个面试官
        
        Returns:
            Optional[Dict[str, Any]]: 新面试官的介绍消息，如果面试结束则返回None
        """
        # 获取当前阶段配置
        current_stage_config = INTERVIEW_STAGES[self.current_stage]
        
        # 获取下一阶段
        next_stage = current_stage_config["next_stage"]
        
        # 如果没有下一阶段，结束面试
        if next_stage is None:
            await self.end_interview()
            return None
        
        logger.info(f"切换面试阶段: {self.current_stage} -> {next_stage}")
        
        # 更新当前阶段
        self.current_stage = next_stage
        next_stage_config = INTERVIEW_STAGES[next_stage]
        
        # 创建面试官切换消息
        transition_message = None
        interviewer_intro = None
        
        # 使用传入的db或默认的self.db
        _db = db if db is not None else self.db
        
        # 如果不是从introduction阶段切换，则添加一个过渡消息
        if current_stage_config["interviewer_id"] != "system":
            # 创建过渡消息
            transition_content = f"感谢您完成{current_stage_config['description']}，现在我们将进入{next_stage_config['description']}。"
            
            transition_message = Message(
                interview_id=self.interview_id,
                content=transition_content,
                sender_type="system"
            )
            _db.add(transition_message)
            _db.commit()
            _db.refresh(transition_message)
        
        # 获取新面试官
        new_interviewer_id = next_stage_config["interviewer_id"]
        
        # 如果不是系统消息，创建新面试官介绍
        if new_interviewer_id != "system":
            interviewer = self.interviewer_factory.get_interviewer(new_interviewer_id)
            
            # 获取面试信息
            interview = self.db.query(Interview).filter(Interview.id == self.interview_id).first()
            
            # 生成面试问题
            if interview:
                questions = await interviewer.generate_questions(
                    position=interview.position,
                    difficulty=interview.difficulty
                )
                
                # 选择第一个问题作为介绍
                intro_question = questions[0] if questions else f"您好，我是{interviewer.name}，{interviewer.role}。请问您能介绍一下自己吗？"
                
                # 创建介绍消息
                intro_content = f"您好，我是{interviewer.name}，{interviewer.role}。{intro_question}"
                
                intro_message = Message(
                    interview_id=self.interview_id,
                    content=intro_content,
                    sender_type="interviewer",
                    interviewer_id=new_interviewer_id
                )
                _db.add(intro_message)
                _db.commit()
                _db.refresh(intro_message)
                
                # 更新阶段消息计数
                self.stage_message_count[next_stage] += 1
        
        # 如果是结束阶段，创建结束消息
        if next_stage == "conclusion":
            conclusion_content = "感谢您参加本次模拟面试。我们现在将结束面试并生成评估报告，请稍候查看您的面试反馈。"
            
            conclusion_message = Message(
                interview_id=self.interview_id,
                content=conclusion_content,
                sender_type="system"
            )
            self.db.add(conclusion_message)
            self.db.commit()
            self.db.refresh(conclusion_message)
            
            # 更新阶段消息计数
            self.stage_message_count[next_stage] += 1
            
            # 触发面试结束
            await self.end_interview()
        
        # 返回新面试官介绍消息
        if intro_message:
            return {
                "id": intro_message.id,
                "content": intro_message.content,
                "sender_type": intro_message.sender_type,
                "interviewer_id": intro_message.interviewer_id,
                "timestamp": intro_message.timestamp.isoformat()
            }
        elif transition_message:
            return {
                "id": transition_message.id,
                "content": transition_message.content,
                "sender_type": transition_message.sender_type,
                "interviewer_id": None,
                "timestamp": transition_message.timestamp.isoformat()
            }
        else:
            return None
    
    async def get_interview_messages(self) -> List[Dict[str, Any]]:
        """
        获取面试消息历史
        
        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        # 查询消息记录
        messages = self.db.query(Message).filter(
            Message.interview_id == self.interview_id
        ).order_by(Message.timestamp).all()
        
        # 转换为字典列表
        return [
            {
                "id": message.id,
                "content": message.content,
                "sender_type": message.sender_type,
                "interviewer_id": message.interviewer_id,
                "timestamp": message.timestamp
            }
            for message in messages
        ]
    
    def get_interview_status(self) -> Dict[str, Any]:
        """
        获取面试当前状态
        
        Returns:
            Dict[str, Any]: 面试状态信息
        """
        # 查询面试信息
        interview = self.db.query(Interview).filter(Interview.id == self.interview_id).first()
        
        if not interview:
            return {
                "interview_id": self.interview_id,
                "status": "cancelled",
                "position": "未知",
                "difficulty": "medium"
            }
        
        # 获取当前面试官ID
        active_interviewer = None
        if self.current_stage in INTERVIEW_STAGES:
            active_interviewer = INTERVIEW_STAGES[self.current_stage]["interviewer_id"]
            if active_interviewer == "system":
                active_interviewer = None
        
        return {
            "interview_id": self.interview_id,
            "status": interview.status,
            "position": interview.position,
            "difficulty": interview.difficulty,
            "active_interviewer": active_interviewer
        }
    
    async def advance_to_next_stage(self, db: Session) -> Dict[str, Any]:
        """
        进入下一个面试阶段
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 切换结果
        """
        logger.info(f"请求进入下一阶段: ID={self.interview_id}, 当前阶段={self.current_stage}")
        
        # 获取当前阶段配置
        current_stage_config = INTERVIEW_STAGES.get(self.current_stage)
        if not current_stage_config:
            return {
                "success": False,
                "message": f"无效的当前阶段: {self.current_stage}"
            }
        
        # 获取下一阶段
        next_stage = current_stage_config["next_stage"]
        if not next_stage:
            return {
                "success": False,
                "message": "已经是最后一个阶段"
            }
        
        # 切换面试官
        result = await self.switch_interviewer(db)
        if not result:
            return {
                "success": False,
                "message": "切换面试官失败"
            }
        
        return {
            "success": True,
            "stage": self.current_stage,
            "message": result
        }
    
    async def end_interview(self, db: Session = None) -> Dict[str, Any]:
        """
        结束面试，更新状态并触发评估生成
        """
        logger.info(f"结束面试: ID={self.interview_id}")
        
        # 使用传入的db或默认的self.db
        _db = db if db is not None else self.db
        
        # 查询面试
        interview = _db.query(Interview).filter(Interview.id == self.interview_id).first()
        
        if not interview:
            return {
                "success": False,
                "message": f"面试不存在: ID={self.interview_id}"
            }
        
        # 如果面试已经结束，直接返回
        if interview.status != "active":
            return {
                "success": False,
                "message": f"面试已经结束: 状态={interview.status}"
            }
            
        # 更新面试状态
        interview.status = "completed"
        interview.end_time = datetime.utcnow()
        _db.commit()
        
        # 触发评估生成（异步）
        asyncio.create_task(self._generate_feedback(_db))
        
        logger.info(f"面试结束: ID={self.interview_id}")
        
        return {
            "success": True,
            "message": "面试已成功结束"
        }
        
    async def _generate_feedback(self, db: Session = None) -> None:
        """
        生成面试评估报告（内部方法）
        
        Args:
            db: 可选的数据库会话，如果不提供则使用self.db
        """
        # 使用传入的db或默认的self.db
        _db = db if db is not None else self.db
        
        # 查询面试
        interview = _db.query(Interview).filter(Interview.id == self.interview_id).first()
        
        if not interview:
            logger.error(f"生成评估失败，面试不存在: ID={self.interview_id}")
            return
            
        # 调用评估服务生成报告
        from ..feedback_service import generate_feedback_service
        
        logger.info(f"开始生成面试评估报告: ID={self.interview_id}")
        
        try:
            # 生成评估报告
            feedback_result = await generate_feedback_service.generate_interview_feedback(
                interview_id=self.interview_id,
                db=_db
            )
            
            logger.info(f"面试评估报告生成成功: ID={self.interview_id}")
            
        except Exception as e:
            logger.error(f"生成面试评估报告失败: {str(e)}")
            # 生成错误时可以创建一个默认的评估报告
        
        try:
            # 获取面试消息
            messages = await self.get_interview_messages()
            
            # 生成评估
            await generate_feedback_service(
                interview_id=self.interview_id,
                messages=messages,
                db=self.db
            )
            
            logger.info(f"面试评估报告生成完成: ID={self.interview_id}")
            
        except Exception as e:
            logger.error(f"生成面试评估报告失败: {str(e)}")


async def get_or_create_interview_manager(interview_id: int, db: Session) -> InterviewManager:
    """
    获取或创建面试管理器
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        InterviewManager: 面试管理器实例
    """
    # 创建管理器
    manager = InterviewManager(interview_id, db)
    
    # 初始化
    await manager.initialize_interview()
    
    return manager
