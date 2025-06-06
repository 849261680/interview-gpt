"""
符合CrewAI官方标准的面试团队实现
使用@CrewBase装饰器和YAML配置文件
纯CrewAI架构，不依赖传统面试官系统
"""
import logging
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# 尝试导入CrewAI
try:
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai.project import CrewBase, agent, task, crew
    from crewai.agents.agent_builder.base_agent import BaseAgent
    from crewai_tools import PDFSearchTool, DOCXSearchTool, TXTSearchTool, FileReadTool
    CREWAI_AVAILABLE = True
    logger.info("CrewAI功能已启用，使用官方标准配置")
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI功能禁用，无法使用多智能体协作")

# 导入集中化LLM配置
from ...config.llm_config import get_llm

# 检查CrewAI工具是否可用
try:
    from crewai_tools import PDFSearchTool, DOCXSearchTool, TXTSearchTool, FileReadTool
    CREWAI_TOOLS_AVAILABLE = True
    logger.info("CrewAI工具包已启用")
except ImportError as e:
    CREWAI_TOOLS_AVAILABLE = False
    logger.warning(f"CrewAI工具包不可用: {e}")


class CrewAINotAvailableError(Exception):
    """当CrewAI不可用时抛出的异常"""
    pass


@CrewBase
class InterviewCrew:
    """
    面试团队类 - 符合CrewAI官方标准
    使用YAML配置文件和装饰器模式
    纯CrewAI架构实现
    """
    
    # 配置文件路径 - 使用绝对路径
    agents_config = str(Path(__file__).parent.parent.parent.parent.parent / 'backend' / 'src' / 'config' / 'agents.yaml')
    tasks_config = str(Path(__file__).parent.parent.parent.parent.parent / 'backend' / 'src' / 'config' / 'tasks.yaml')
    
    # 自动收集的agents和tasks列表
    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self, position: str = "通用职位", difficulty: str = "medium", resume_context: str = ""):
        """
        初始化面试团队
        
        Args:
            position: 面试职位
            difficulty: 面试难度
            resume_context: 简历上下文
        """
        if not CREWAI_AVAILABLE:
            raise CrewAINotAvailableError("CrewAI不可用，无法创建面试团队")
            
        self.position = position
        self.difficulty = difficulty
        self.resume_context = resume_context
        
        # 初始化LLM配置
        self.llm = self._setup_llm()
        
        # 调用父类初始化
        super().__init__()
        
        logger.info(f"面试团队初始化完成：职位={position}, 难度={difficulty}")
        logger.info(f"使用配置文件: agents={self.agents_config}, tasks={self.tasks_config}")
    
    def _setup_llm(self) -> Optional[LLM]:
        """
        设置LLM配置 - 使用集中化配置
        
        Returns:
            LLM: 配置好的LLM实例，如果不可用则返回None
        """
        llm = get_llm()
        if llm:
            logger.info("使用集中化LLM配置")
        else:
            logger.warning("未配置LLM，请设置相应的API密钥")
        return llm
    
    @agent
    def resume_analyzer(self) -> Agent:
        """创建简历分析师 - 使用CrewAI官方文档工具"""
        return Agent(
            config=self.agents_config['resume_analyzer'],
            tools=[
                PDFSearchTool(),    # 处理PDF简历
                DOCXSearchTool(),   # 处理Word简历
                TXTSearchTool(),    # 处理文本简历
                FileReadTool()      # 通用文件读取
            ],
            verbose=True
        )
    
    @agent
    def hr_interviewer(self) -> Agent:
        """创建HR面试官"""
        return Agent(
            config=self.agents_config['hr_interviewer'],
            verbose=True
        )
    
    @agent
    def technical_interviewer(self) -> Agent:
        """创建技术面试官"""
        return Agent(
            config=self.agents_config['technical_interviewer'],
            verbose=True
        )
    
    @agent
    def behavioral_interviewer(self) -> Agent:
        """创建行为面试官"""
        return Agent(
            config=self.agents_config['behavioral_interviewer'],
            verbose=True
        )
    
    @agent
    def interview_evaluator(self) -> Agent:
        """创建面试评估官"""
        return Agent(
            config=self.agents_config['interview_evaluator'],
            verbose=True
        )
    
    @task
    def resume_analysis_task(self) -> Task:
        """创建简历分析任务"""
        return Task(
            config=self.tasks_config['resume_analysis_task']
        )
    
    @task
    def hr_interview_task(self) -> Task:
        """创建HR面试任务"""
        return Task(
            config=self.tasks_config['hr_interview_task']
        )
    
    @task
    def technical_interview_task(self) -> Task:
        """创建技术面试任务"""
        return Task(
            config=self.tasks_config['technical_interview_task']
        )
    
    @task
    def behavioral_interview_task(self) -> Task:
        """创建行为面试任务"""
        return Task(
            config=self.tasks_config['behavioral_interview_task']
        )
    
    @task
    def final_evaluation_task(self) -> Task:
        """创建最终评估任务"""
        return Task(
            config=self.tasks_config['final_evaluation_task']
        )
    
    @crew
    def crew(self) -> Crew:
        """创建面试团队"""
        return Crew(
            agents=self.agents,  # 自动收集的agents
            tasks=self.tasks,    # 自动收集的tasks
            process=Process.sequential,  # 顺序执行
            verbose=True,
            memory=False,  # 暂时禁用记忆功能，避免OpenAI API依赖
            # embedder={
            #     "provider": "openai",
            #     "config": {
            #         "model": "text-embedding-3-small"
            #     }
            # }
        )


class InterviewCrewManager:
    """
    面试团队管理器
    管理多个面试团队实例
    """
    
    def __init__(self):
        """初始化面试团队管理器"""
        if not CREWAI_AVAILABLE:
            raise CrewAINotAvailableError("CrewAI不可用，无法创建面试团队管理器")
        
        self.active_crews: Dict[str, InterviewCrew] = {}
        logger.info("面试团队管理器初始化完成")
    
    async def initialize_interview(
        self,
        interview_id: str,
        position: str = "通用职位",
        difficulty: str = "medium",
        resume_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        初始化面试会话 - 支持文件路径参数
        
        Args:
            interview_id: 面试ID
            position: 面试职位
            difficulty: 面试难度
            resume_file_path: 简历文件路径（可选）
            
        Returns:
            Dict: 初始化结果
        """
        try:
            logger.info(f"初始化面试团队: {interview_id}, 职位: {position}, 难度: {difficulty}, 简历文件: {resume_file_path}")
            
            # 创建面试团队
            crew = InterviewCrew(
                position=position,
                difficulty=difficulty,
                resume_context=""  # 使用文件路径而不是文本内容
            )
            
            # 保存到活跃团队列表
            self.active_crews[interview_id] = crew
            
            # 如果有简历文件，执行简历分析任务
            if resume_file_path:
                logger.info(f"开始分析简历文件: {resume_file_path}")
                
                # 执行简历分析任务
                result = crew.crew().kickoff(inputs={
                    "position": position,
                    "difficulty": difficulty,
                    "resume_file_path": resume_file_path
                })
                
                return {
                    "status": "success",
                    "interview_id": interview_id,
                    "message": "面试初始化完成，简历分析已完成",
                    "resume_analysis": result.raw if hasattr(result, 'raw') else str(result),
                    "position": position,
                    "difficulty": difficulty,
                    "resume_file_path": resume_file_path
                }
            else:
                return {
                    "status": "success",
                    "interview_id": interview_id,
                    "message": "面试初始化完成，未提供简历文件",
                    "position": position,
                    "difficulty": difficulty
                }
                
        except Exception as e:
            logger.error(f"初始化面试失败: {interview_id}, 错误: {str(e)}")
            return {
                "status": "error",
                "interview_id": interview_id,
                "error": str(e)
            }

    def create_interview_crew(
        self, 
        crew_id: str, 
        position: str = "通用职位", 
        difficulty: str = "medium", 
        resume_context: str = ""
    ) -> InterviewCrew:
        """
        创建新的面试团队
        
        Args:
            crew_id: 团队ID
            position: 面试职位
            difficulty: 面试难度
            resume_context: 简历上下文
            
        Returns:
            InterviewCrew: 面试团队实例
        """
        logger.info(f"创建面试团队: {crew_id}, 职位: {position}, 难度: {difficulty}")
        
        crew = InterviewCrew(
            position=position,
            difficulty=difficulty,
            resume_context=resume_context
        )
        
        self.active_crews[crew_id] = crew
        return crew
    
    def get_interview_crew(self, crew_id: str) -> Optional[InterviewCrew]:
        """
        获取面试团队
        
        Args:
            crew_id: 团队ID
            
        Returns:
            InterviewCrew: 面试团队实例，如果不存在则返回None
        """
        return self.active_crews.get(crew_id)
    
    def remove_interview_crew(self, crew_id: str) -> bool:
        """
        移除面试团队
        
        Args:
            crew_id: 团队ID
            
        Returns:
            bool: 是否成功移除
        """
        if crew_id in self.active_crews:
            del self.active_crews[crew_id]
            logger.info(f"移除面试团队: {crew_id}")
            return True
        return False
    
    def list_active_crews(self) -> List[str]:
        """
        列出所有活跃的面试团队
        
        Returns:
            List[str]: 团队ID列表
        """
        return list(self.active_crews.keys())
    
    async def conduct_interview(
        self, 
        crew_id: str, 
        position: str = "通用职位", 
        difficulty: str = "medium", 
        resume_context: str = ""
    ) -> Dict[str, Any]:
        """
        异步执行面试流程
        
        Args:
            crew_id: 团队ID
            position: 面试职位
            difficulty: 面试难度
            resume_context: 简历上下文
            
        Returns:
            Dict[str, Any]: 面试启动结果（不等待完成）
        """
        try:
            # 创建或获取面试团队
            crew = self.get_interview_crew(crew_id)
            if not crew:
                crew = self.create_interview_crew(crew_id, position, difficulty, resume_context)
            
            # 立即返回启动成功状态，不等待CrewAI执行完成
            logger.info(f"面试流程启动: {crew_id}")
            
            # 在后台异步执行CrewAI流程
            import asyncio
            asyncio.create_task(self._execute_crew_background(crew, crew_id, position, difficulty, resume_context))
            
            return {
                "status": "success",
                "crew_id": crew_id,
                "message": "面试流程已启动，正在后台执行",
                "position": position,
                "difficulty": difficulty
            }
            
        except Exception as e:
            logger.error(f"面试流程启动失败: {crew_id}, 错误: {str(e)}")
            return {
                "status": "error",
                "crew_id": crew_id,
                "error": str(e)
            }
    
    async def _execute_crew_background(
        self, 
        crew: InterviewCrew, 
        crew_id: str, 
        position: str, 
        difficulty: str, 
        resume_context: str
    ):
        """
        在后台执行CrewAI流程
        
        Args:
            crew: 面试团队实例
            crew_id: 团队ID
            position: 面试职位
            difficulty: 面试难度
            resume_context: 简历上下文
        """
        try:
            logger.info(f"开始后台执行CrewAI流程: {crew_id}")
            
            # 使用线程池执行同步的CrewAI流程，避免阻塞事件循环
            import asyncio
            import concurrent.futures
            
            def run_crew_sync():
                """同步执行CrewAI流程的函数"""
                return crew.crew().kickoff(inputs={
                    "position": position,
                    "difficulty": difficulty,
                    "resume_context": resume_context or "未提供简历信息"
                })
            
            # 在线程池中执行同步操作
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, run_crew_sync)
            
            logger.info(f"CrewAI流程执行完成: {crew_id}")
            
            # 这里可以添加结果处理逻辑，比如保存到数据库、发送WebSocket通知等
            # TODO: 添加结果处理和通知机制
            
        except Exception as e:
            logger.error(f"后台CrewAI流程执行失败: {crew_id}, 错误: {str(e)}")
            # TODO: 添加错误处理和通知机制


# 全局面试团队管理器实例
_interview_crew_manager: Optional[InterviewCrewManager] = None


def get_interview_crew_manager() -> InterviewCrewManager:
    """
    获取全局面试团队管理器实例
    
    Returns:
        InterviewCrewManager: 面试团队管理器实例
    """
    global _interview_crew_manager
    
    if _interview_crew_manager is None:
        if not CREWAI_AVAILABLE:
            raise CrewAINotAvailableError("CrewAI不可用，无法创建面试团队管理器")
        
        _interview_crew_manager = InterviewCrewManager()
    
    return _interview_crew_manager


def is_crewai_available() -> bool:
    """
    检查CrewAI是否可用
    
    Returns:
        bool: CrewAI是否可用
    """
    return CREWAI_AVAILABLE 