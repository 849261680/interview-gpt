"""
面试流程管理器
负责管理整个面试过程、面试官轮换和状态转换
提供实时通信和状态更新
符合CrewAI顺序执行规范，不使用面试协调员
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import traceback

from ...models.schemas import Interview, Message, User
# 使用新的CrewAI架构，不再需要InterviewerFactory
from ..ai.crewai_integration import get_crewai_integration
from ...schemas.interview import MessageCreate

# 面试阶段配置 - 符合CrewAI顺序执行规范：简历解析 → HR面试 → 技术面试 → 行为面试 → 面试评估
INTERVIEW_STAGES = {
    "resume_analysis": {
        "description": "简历解析阶段",
        "interviewer_id": "resume_analyzer",
        "max_messages": 4,
        "next_stage": "hr_interview"
    },
    "hr_interview": {
        "description": "HR面试阶段",
        "interviewer_id": "hr",
        "max_messages": 6,
        "next_stage": "technical_interview"
    },
    "technical_interview": {
        "description": "技术面试阶段",
        "interviewer_id": "technical",
        "max_messages": 8,
        "next_stage": "behavioral_interview"
    },
    "behavioral_interview": {
        "description": "行为面试阶段",
        "interviewer_id": "behavioral",
        "max_messages": 6,
        "next_stage": "interview_evaluation"
    },
    "interview_evaluation": {
        "description": "面试评估阶段",
        "interviewer_id": "interview_evaluator",
        "max_messages": 2,
        "next_stage": None  # 最后一个阶段
    }
}

# 设置日志
logger = logging.getLogger(__name__)

class InterviewManager:
    """
    面试流程管理器
    负责管理整个面试过程、面试官轮换和状态转换
    符合CrewAI顺序执行规范，不使用面试协调员
    """
    
    def __init__(self, interview_id: int, db: Session):
        """
        初始化面试管理器
        
        Args:
            interview_id: 面试ID
            db: 数据库会话
        """
        logger.info(f"[InterviewManager.__init__] 创建面试管理器实例 - Interview ID: {interview_id}")
        
        # 立即验证面试ID是否存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            # 获取数据库中所有面试ID用于调试
            all_interviews = db.query(Interview.id, Interview.status, Interview.position).all()
            logger.error(f"[InterviewManager.__init__] 面试ID {interview_id} 不存在于数据库中")
            logger.error(f"[InterviewManager.__init__] 数据库中现有的面试ID: {[i.id for i in all_interviews]}")
            logger.error(f"[InterviewManager.__init__] 调用栈: {traceback.format_stack()}")
            raise ValueError(f"面试ID {interview_id} 不存在于数据库中。现有面试ID: {[i.id for i in all_interviews]}")
        
        logger.info(f"[InterviewManager.__init__] 面试验证成功 - ID: {interview.id}, Status: {interview.status}, Position: {interview.position}")
        
        self.interview_id = interview_id
        self.db = db
        self.current_stage = "resume_analysis"  # 从简历解析阶段开始
        self.stage_message_count = {stage: 0 for stage in INTERVIEW_STAGES}
        # 使用CrewAI集成替代面试官工厂
        self.crewai_integration = get_crewai_integration()
        
    async def initialize_interview(self) -> None:
        """
        初始化面试，创建欢迎消息
        """
        logger.info(f"[initialize_interview] 开始初始化面试 - Interview ID: {self.interview_id}")
        
        try:
            # 再次验证面试存在（防御性编程）
            interview = self.db.query(Interview).filter(Interview.id == self.interview_id).first()
            
            if not interview:
                logger.error(f"[initialize_interview] 面试不存在 - ID: {self.interview_id}")
                raise ValueError(f"面试不存在: ID={self.interview_id}")
            
            logger.info(f"[initialize_interview] 面试信息 - ID: {interview.id}, Status: {interview.status}, Position: {interview.position}")
            
            # 检查面试状态
            if interview.status != "active":
                logger.warning(f"[initialize_interview] 面试状态不是活跃状态 - Status: {interview.status}")
                raise ValueError(f"面试状态不是活跃状态: {interview.status}")
            
            # 获取已有消息数量
            existing_messages = self.db.query(Message).filter(
                Message.interview_id == self.interview_id
            ).count()
            logger.info(f"[initialize_interview] 现有消息数量: {existing_messages}")
            
            # 如果没有消息，创建欢迎消息
            if existing_messages == 0:
                logger.info(f"[initialize_interview] 创建欢迎消息 - Interview ID: {self.interview_id}")
                await self._create_welcome_message(interview)
            else:
                logger.info(f"[initialize_interview] 面试已有消息，跳过初始化 - Interview ID: {self.interview_id}")
                await self._restore_interview_state()
                
        except Exception as e:
            logger.error(f"[initialize_interview] 初始化失败 - Interview ID: {self.interview_id}, Error: {str(e)}")
            logger.error(f"[initialize_interview] 错误详情: {traceback.format_exc()}")
            raise
    
    async def _create_welcome_message(self, interview: Interview) -> None:
        """创建欢迎消息 - 启动CrewAI顺序执行流程"""
        try:
            # 设置初始阶段为简历解析
            self.current_stage = "resume_analysis"
            logger.info(f"[_create_welcome_message] 设置初始阶段: {self.current_stage}")
            
            # 检查是否启用CrewAI
            from ...services.ai.crewai_integration import get_crewai_integration
            crewai_service = get_crewai_integration()
            
            if crewai_service.available:
                logger.info(f"[_create_welcome_message] 启动CrewAI顺序执行流程")
                
                # 启动CrewAI顺序执行流程
                await self._start_crewai_interview(interview, crewai_service)
            else:
                logger.warning(f"[_create_welcome_message] CrewAI不可用，使用传统单面试官模式")
                
                # 回退到传统单面试官模式
                await self._start_traditional_interview(interview)
                
        except Exception as e:
            logger.error(f"[_create_welcome_message] 创建欢迎消息失败: {str(e)}")
            # 回退到传统模式
            await self._start_traditional_interview(interview)
    
    async def _start_crewai_interview(self, interview: Interview, crewai_service) -> None:
        """启动CrewAI顺序执行面试流程"""
        try:
            logger.info(f"[_start_crewai_interview] 开始CrewAI顺序执行面试")
            
            # 准备CrewAI输入参数
            inputs = {
                "position": interview.position,
                "difficulty": interview.difficulty,
                "resume_context": interview.resume_content or "",
                "interview_id": self.interview_id
            }
            
            # 启动CrewAI顺序执行流程
            result = await crewai_service.conduct_interview(
                resume_context=inputs["resume_context"],
                position=inputs["position"],
                difficulty=inputs["difficulty"]
            )
            
            if result.get("success"):
                logger.info(f"[_start_crewai_interview] CrewAI面试启动成功")
                
                # 从CrewAI结果中提取第一条消息作为欢迎消息
                if result.get("messages") and len(result["messages"]) > 0:
                    first_message = result["messages"][0]
                    
                    welcome_message = Message(
                        interview_id=self.interview_id,
                        content=first_message.get("content", "欢迎参加面试！"),
                        sender_type="interviewer",
                        interviewer_id=first_message.get("interviewer_id", "resume_analyzer")
                    )
                    self.db.add(welcome_message)
                    self.db.commit()
                    
                    logger.info(f"[_start_crewai_interview] CrewAI欢迎消息创建成功")
                else:
                    # 如果CrewAI没有返回消息，创建默认欢迎消息
                    await self._create_default_welcome_message(interview)
            else:
                logger.error(f"[_start_crewai_interview] CrewAI面试启动失败: {result.get('error')}")
                # 回退到传统模式
                await self._start_traditional_interview(interview)
                
        except Exception as e:
            logger.error(f"[_start_crewai_interview] CrewAI面试启动异常: {str(e)}")
            # 回退到传统模式
            await self._start_traditional_interview(interview)
    
    async def _start_traditional_interview(self, interview: Interview) -> None:
        """启动传统单面试官模式"""
        try:
            logger.info(f"[_start_traditional_interview] 启动传统面试模式")
            
            # 获取简历分析师
            resume_analyzer = self.interviewer_factory.get_interviewer("resume_analyzer")
            if not resume_analyzer:
                logger.error(f"[_start_traditional_interview] 无法获取简历分析师")
                await self._create_default_welcome_message(interview)
                return
            
            # 获取简历内容
            resume_content = interview.resume_content if interview.resume_content else ""
            logger.info(f"[_start_traditional_interview] 简历内容长度: {len(resume_content)} 字符")
            
            # 使用简历分析师的智能生成方法创建欢迎消息
            welcome_content = await resume_analyzer.generate_response(
                messages=[],  # 空消息历史会触发欢迎消息生成
                position=interview.position,
                difficulty=interview.difficulty,
                resume_content=resume_content
            )
            
            welcome_message = Message(
                interview_id=self.interview_id,
                content=welcome_content,
                sender_type="interviewer",
                interviewer_id="resume_analyzer"
            )
            self.db.add(welcome_message)
            self.db.commit()
            
            logger.info(f"[_start_traditional_interview] 传统模式欢迎消息创建成功")
            
        except Exception as e:
            logger.error(f"[_start_traditional_interview] 传统模式启动失败: {str(e)}")
            await self._create_default_welcome_message(interview)
    
    async def _create_default_welcome_message(self, interview: Interview) -> None:
        """创建默认欢迎消息"""
        try:
            welcome_content = f"您好！欢迎参加{interview.position}职位的面试。我是您的面试官，让我们开始今天的面试吧！请先简单介绍一下您自己。"
            
            welcome_message = Message(
                interview_id=self.interview_id,
                content=welcome_content,
                sender_type="interviewer",
                interviewer_id="resume_analyzer"
            )
            self.db.add(welcome_message)
            self.db.commit()
            
            logger.info(f"[_create_default_welcome_message] 默认欢迎消息创建成功")
            
        except Exception as e:
            logger.error(f"[_create_default_welcome_message] 创建默认欢迎消息失败: {str(e)}")
            raise
    
    async def _restore_interview_state(self) -> None:
        """恢复面试状态"""
        try:
            # 获取最后一条系统消息来恢复状态
            last_message = self.db.query(Message).filter(
                Message.interview_id == self.interview_id
            ).order_by(Message.timestamp.desc()).first()
            
            if last_message:
                logger.info(f"[_restore_interview_state] 恢复面试状态 - 最后消息来自: {last_message.sender_type}")
                # 这里可以添加更复杂的状态恢复逻辑
            
        except Exception as e:
            logger.error(f"[_restore_interview_state] 恢复面试状态失败: {str(e)}")
            # 不抛出异常，使用默认状态
    
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
            self.current_stage = "resume_analysis"  # 默认从简历解析开始
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
            Tuple[Message, Optional[Message]]: 用户消息和面试官回复消息
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
        
        # 检查是否启用CrewAI
        from ...services.ai.crewai_integration import get_crewai_integration
        crewai_service = get_crewai_integration()
        
        if crewai_service.available:
            logger.info(f"[process_user_message] 使用CrewAI处理用户消息")
            return await self._process_with_crewai(user_message, message_content, db, crewai_service)
        else:
            logger.info(f"[process_user_message] 使用传统模式处理用户消息")
            return await self._process_with_traditional(user_message, message_content, db)
    
    async def _process_with_crewai(self, user_message: Message, message_content: str, db: Session, crewai_service) -> Tuple[Message, Optional[Message]]:
        """使用CrewAI处理用户消息"""
        try:
            # 获取面试消息历史
            messages = await self.get_interview_messages()
            
            # 获取当前面试官
            current_stage_config = INTERVIEW_STAGES.get(self.current_stage)
            if not current_stage_config:
                logger.error(f"无效的面试阶段: {self.current_stage}")
                return user_message, None
            
            current_interviewer_id = current_stage_config["interviewer_id"]
            
            # 使用CrewAI进行面试轮次处理
            response = await crewai_service.conduct_interview_round(
                interviewer_type=current_interviewer_id,
                messages=messages,
                position=self.get_interview_position(),
                difficulty=self.get_interview_difficulty()
            )
            
            if response.get("success") and response.get("content"):
                # 保存面试官回复
                interviewer_message = Message(
                    interview_id=self.interview_id,
                    content=response["content"],
                    sender_type="interviewer",
                    interviewer_id=current_interviewer_id
                )
                db.add(interviewer_message)
                db.commit()
                db.refresh(interviewer_message)
                
                # 更新阶段消息计数
                self.stage_message_count[self.current_stage] += 1
                
                # 检查是否需要切换到下一个面试官
                if self.should_switch_interviewer():
                    logger.info(f"[_process_with_crewai] 达到阶段消息上限，准备切换面试官")
                    await self.switch_interviewer(db)
                
                logger.info(f"[_process_with_crewai] CrewAI面试官回复生成成功: {current_interviewer_id}")
                return user_message, interviewer_message
            else:
                logger.error(f"[_process_with_crewai] CrewAI处理失败: {response.get('error')}")
                # 回退到传统模式
                return await self._process_with_traditional(user_message, message_content, db)
                
        except Exception as e:
            logger.error(f"[_process_with_crewai] CrewAI处理异常: {str(e)}")
            # 回退到传统模式
            return await self._process_with_traditional(user_message, message_content, db)
    
    async def _process_with_traditional(self, user_message: Message, message_content: str, db: Session) -> Tuple[Message, Optional[Message]]:
        """使用传统模式处理用户消息"""
        try:
            # 获取面试消息历史
            messages = await self.get_interview_messages()
            
            # 获取当前面试官
            current_stage_config = INTERVIEW_STAGES.get(self.current_stage)
            if not current_stage_config:
                logger.error(f"无效的面试阶段: {self.current_stage}")
                return user_message, None
            
            current_interviewer_id = current_stage_config["interviewer_id"]
            current_interviewer = self.interviewer_factory.get_interviewer(current_interviewer_id)
            
            if not current_interviewer:
                logger.error(f"无法获取面试官: {current_interviewer_id}")
                return user_message, None
            
            # 生成面试官回复
            # 如果是简历分析师，传递简历内容
            if current_interviewer_id == "resume_analyzer":
                response_content = await current_interviewer.generate_response(
                    messages=messages,
                    position=self.get_interview_position(),
                    difficulty=self.get_interview_difficulty(),
                    resume_content=self.get_resume_content()
                )
            else:
                response_content = await current_interviewer.generate_response(
                    messages=messages,
                    position=self.get_interview_position(),
                    difficulty=self.get_interview_difficulty()
                )
            
            # 保存面试官回复
            interviewer_message = Message(
                interview_id=self.interview_id,
                content=response_content,
                sender_type="interviewer",
                interviewer_id=current_interviewer_id
            )
            db.add(interviewer_message)
            db.commit()
            db.refresh(interviewer_message)
            
            # 更新阶段消息计数
            self.stage_message_count[self.current_stage] += 1
            
            # 检查是否需要切换到下一个面试官
            if self.should_switch_interviewer():
                logger.info(f"[_process_with_traditional] 达到阶段消息上限，准备切换面试官")
                await self.switch_interviewer(db)
            
            logger.info(f"[_process_with_traditional] 传统模式面试官回复生成成功: {current_interviewer_id}")
            return user_message, interviewer_message
            
        except Exception as e:
            logger.error(f"[_process_with_traditional] 传统模式处理失败: {str(e)}")
            return user_message, None
    
    def should_switch_interviewer(self) -> bool:
        """
        判断是否应该切换面试官
        
        Returns:
            bool: 是否应该切换面试官
        """
        current_stage_config = INTERVIEW_STAGES.get(self.current_stage)
        if not current_stage_config:
            return False
        
        max_messages = current_stage_config.get("max_messages", 0)
        current_messages = self.stage_message_count.get(self.current_stage, 0)
        
        return current_messages >= max_messages
    
    async def switch_interviewer(self, db: Session = None) -> Optional[Dict[str, Any]]:
        """
        切换到下一个面试官
        
        Args:
            db: 数据库会话
            
        Returns:
            Optional[Dict[str, Any]]: 切换结果信息
        """
        logger.info(f"切换面试官: 当前阶段={self.current_stage}")
        
        current_stage_config = INTERVIEW_STAGES.get(self.current_stage)
        if not current_stage_config:
            logger.error(f"无效的面试阶段: {self.current_stage}")
            return None
        
        next_stage = current_stage_config.get("next_stage")
        if not next_stage:
            logger.info("已到达最后一个面试阶段，面试结束")
            return await self.end_interview(db)
        
        # 切换到下一个阶段
        self.current_stage = next_stage
        next_stage_config = INTERVIEW_STAGES.get(next_stage)
        next_interviewer_id = next_stage_config["interviewer_id"]
        
        # 获取下一个面试官
        next_interviewer = self.interviewer_factory.get_interviewer(next_interviewer_id)
        if not next_interviewer:
            logger.error(f"无法获取下一个面试官: {next_interviewer_id}")
            return None
        
        # 创建切换消息
        if db:
            transition_content = f"感谢您的回答。现在让我们进入{next_stage_config['description']}，由{next_interviewer.name}为您继续面试。"
            transition_message = Message(
                interview_id=self.interview_id,
                content=transition_content,
                sender_type="interviewer",
                interviewer_id=next_interviewer_id
            )
            db.add(transition_message)
            db.commit()
        
        logger.info(f"面试官切换成功: {self.current_stage} -> {next_stage}")
        
        return {
            "status": "switched",
            "previous_stage": current_stage_config["description"],
            "current_stage": next_stage_config["description"],
            "current_interviewer": next_interviewer.name,
            "interviewer_id": next_interviewer_id
        }
    
    def get_interview_position(self) -> str:
        """获取面试职位"""
        interview = self.db.query(Interview).filter(Interview.id == self.interview_id).first()
        return interview.position if interview else "通用职位"
    
    def get_interview_difficulty(self) -> str:
        """获取面试难度"""
        interview = self.db.query(Interview).filter(Interview.id == self.interview_id).first()
        return interview.difficulty if interview else "medium"
    
    def get_resume_content(self) -> str:
        """获取简历内容"""
        interview = self.db.query(Interview).filter(Interview.id == self.interview_id).first()
        return interview.resume_content if interview and interview.resume_content else ""
    
    async def get_interview_messages(self) -> List[Dict[str, Any]]:
        """
        获取面试消息历史
        
        Returns:
            List[Dict[str, Any]]: 消息历史列表
        """
        messages = self.db.query(Message).filter(
            Message.interview_id == self.interview_id
        ).order_by(Message.timestamp).all()
        
        return [
            {
                "id": msg.id,
                "content": msg.content,
                "sender_type": msg.sender_type,
                "interviewer_id": msg.interviewer_id,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in messages
        ]
    
    def get_interview_status(self) -> Dict[str, Any]:
        """
        获取面试状态信息
        
        Returns:
            Dict[str, Any]: 面试状态信息
        """
        current_stage_config = INTERVIEW_STAGES.get(self.current_stage, {})
        
        return {
            "interview_id": self.interview_id,
            "current_stage": self.current_stage,
            "stage_description": current_stage_config.get("description", ""),
            "current_interviewer": current_stage_config.get("interviewer_id", ""),
            "stage_progress": {
                "current_messages": self.stage_message_count.get(self.current_stage, 0),
                "max_messages": current_stage_config.get("max_messages", 0)
            },
            "total_stages": len(INTERVIEW_STAGES),
            "completed_stages": list(INTERVIEW_STAGES.keys()).index(self.current_stage) if self.current_stage in INTERVIEW_STAGES else 0,
            "is_final_stage": current_stage_config.get("next_stage") is None
        }
    
    async def advance_to_next_stage(self, db: Session) -> Dict[str, Any]:
        """
        强制推进到下一个面试阶段
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 推进结果
        """
        logger.info(f"强制推进到下一个面试阶段: 当前阶段={self.current_stage}")
        
        current_stage_config = INTERVIEW_STAGES.get(self.current_stage)
        if not current_stage_config:
            return {"status": "error", "message": "无效的面试阶段"}
        
        next_stage = current_stage_config.get("next_stage")
        if not next_stage:
            return {"status": "completed", "message": "已到达最后一个面试阶段"}
        
        # 切换到下一个阶段
        result = await self.switch_interviewer(db)
        
        if result:
            return {"status": "success", "result": result}
        else:
            return {"status": "error", "message": "切换面试官失败"}
    
    async def end_interview(self, db: Session = None) -> Dict[str, Any]:
        """
        结束面试
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 结束面试结果
        """
        logger.info(f"结束面试: ID={self.interview_id}")
        
        try:
            # 更新面试状态
            if db:
                interview = db.query(Interview).filter(Interview.id == self.interview_id).first()
                if interview:
                    interview.status = "completed"
                    db.commit()
            
            # 生成面试反馈
            await self._generate_feedback(db)
            
            logger.info(f"面试结束成功: ID={self.interview_id}")
            
            return {
                "status": "completed",
                "message": "面试已完成",
                "interview_id": self.interview_id,
                "final_stage": self.current_stage
            }
            
        except Exception as e:
            logger.error(f"结束面试失败: {str(e)}")
            return {
                "status": "error",
                "message": f"结束面试失败: {str(e)}"
            }
    
    async def _generate_feedback(self, db: Session = None) -> None:
        """
        生成面试反馈
        
        Args:
            db: 数据库会话
        """
        try:
            logger.info(f"生成面试反馈: ID={self.interview_id}")
            
            # 获取所有消息
            messages = await self.get_interview_messages()
            
            # 生成简单的反馈消息
            feedback_content = "感谢您参加本次模拟面试！我们的面试团队已经完成了对您的全面评估。您在技术能力、产品思维、行为表现和综合素质等方面都有不错的表现。我们会尽快整理详细的面试报告并给您反馈。"
            
            if db:
                feedback_message = Message(
                    interview_id=self.interview_id,
                    content=feedback_content,
                    sender_type="system",
                    interviewer_id="system"
                )
                db.add(feedback_message)
                db.commit()
            
            logger.info(f"面试反馈生成成功: ID={self.interview_id}")
            
        except Exception as e:
            logger.error(f"生成面试反馈失败: {str(e)}")


async def get_or_create_interview_manager(interview_id: int, db: Session) -> InterviewManager:
    """
    获取或创建面试管理器实例
    
    Args:
        interview_id: 面试ID
        db: 数据库会话
        
    Returns:
        InterviewManager: 面试管理器实例
    """
    try:
        manager = InterviewManager(interview_id, db)
        await manager.load_current_stage()
        return manager
    except Exception as e:
        logger.error(f"创建面试管理器失败: {str(e)}")
        raise
