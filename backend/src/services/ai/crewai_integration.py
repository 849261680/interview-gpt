"""
CrewAI集成模块
提供多智能体协作功能，用于构建复杂的面试场景
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

# 导入DeepSeek配置
from .deepseek_config import get_deepseek_model_config, get_deepseek_prompt_for_interviewer, is_deepseek_available

logger = logging.getLogger(__name__)

# 尝试导入CrewAI
try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
    logger.info("CrewAI功能已启用，项目将使用多智能体协作")
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI功能禁用，项目将使用真实AI服务而非多智能体协作")

# 如果CrewAI不可用，将会抛出异常
if not CREWAI_AVAILABLE:
    # 定义异常类
    class CrewAINotAvailableError(Exception):
        """当CrewAI不可用时抛出的异常"""
        pass


class CrewAIIntegration:
    """CrewAI集成类"""
    
    def __init__(self):
        self.available = CREWAI_AVAILABLE
        self.agents = {}
        self.crews = {}
        self.interview_agents = {}
        self.interview_tasks = {}
        self.interview_crew = None
        
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI不可用，无法使用多智能体功能")
            # 注意我们在这里不抛出异常，而是在调用方法时抛出
    
    def is_available(self) -> bool:
        """检查CrewAI是否可用"""
        return self.available
    
    def get_status(self) -> Dict[str, Any]:
        """获取CrewAI集成状态"""
        return {
            "available": self.available,
            "agents_count": len(self.agents) if self.available else 0,
            "crews_count": len(self.crews) if self.available else 0,
            "agents": list(self.agents.keys()) if self.available else [],
            "crews": list(self.crews.keys()) if self.available else []
        }
        
    def create_agent(self, *args, **kwargs):
        """创建CrewAI智能体"""
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法创建智能体")
        
        # 如果CrewAI可用，则创建真实的Agent对象
        return Agent(*args, **kwargs)
    
    def create_task(self, *args, **kwargs):
        """创建CrewAI任务"""
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法创建任务")
        
        # 如果CrewAI可用，则创建真实的Task对象
        return Task(*args, **kwargs)
    
    def create_crew(self, *args, **kwargs):
        """创建CrewAI团队"""
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法创建团队")
        
        # 如果CrewAI可用，则创建真实的Crew对象
        return Crew(*args, **kwargs)
    
    async def initialize_interview_agents(self, position: str, difficulty: str):
        """
        初始化面试智能体
        
        Args:
            position: 面试职位
            difficulty: 面试难度
        """
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法初始化面试智能体")
            
        logger.info(f"初始化面试智能体：职位 {position}，难度 {difficulty}")
        
        # 检查是否可以使用DeepSeek API
        use_deepseek = is_deepseek_available()
        if use_deepseek:
            logger.info("使用DeepSeek API初始化智能体")
            from crewai import LLM
            
            # 配置DeepSeek LLM
            model_config = get_deepseek_model_config()
            llm = LLM(
                model=f"deepseek/{model_config['model']}",
                temperature=model_config['temperature'],
                max_tokens=model_config['max_tokens'],
                api_key=model_config['api_key'],
                api_base=model_config['api_base']
            )
            logger.info("DeepSeek LLM初始化完成")
        else:
            logger.info("未配置DeepSeek API，使用默认LLM")
            llm = None
            
        # 创建面试协调员
        self.interview_agents["coordinator"] = Agent(
            role="面试协调员",
            goal="协调面试流程，生成面试报告",
            backstory="""你是一位经验丰富的面试协调员，擅长安排面试日程，协调面试官，
            收集面试结果，并生成最终的面试报告。你的目标是确保面试顺利进行，
            帮助候选人充分展示自己的能力，同时为公司选择合适的人才。""",
            allow_delegation=True,
            verbose=True,
            llm=llm,  # 使用DeepSeek LLM
            system_prompt=get_deepseek_prompt_for_interviewer("coordinator") if use_deepseek else None
        )
        
        # 创建技术面试官
        self.interview_agents["technical"] = Agent(
            role="技术面试官",
            goal="评估候选人的技术能力",
            backstory="""你是一位资深的技术面试官，擅长提出技术问题，审查代码，
            评估候选人的技术水平和解决问题的能力。你需要根据候选人应聘的职位 {position} 
            和面试难度 {difficulty} 调整问题的深度和广度。""".format(
                position=position, difficulty=difficulty
            ),
            allow_delegation=True,
            verbose=True,
            llm=llm,  # 使用DeepSeek LLM
            system_prompt=get_deepseek_prompt_for_interviewer("technical") if use_deepseek else None
        )
        
        # 创建产品面试官
        self.interview_agents["product"] = Agent(
            role="产品面试官",
            goal="评估候选人的产品sense和产品设计能力",
            backstory="""你是一位资深的产品面试官，擅长提出产品相关问题，要求候选人分析产品案例，
            评估候选人的产品sense、产品设计能力、市场分析能力和用户洞察力。
            你需要根据候选人应聘的职位 {position} 和面试难度 {difficulty} 调整问题的深度和广度。""".format(
                position=position, difficulty=difficulty
            ),
            allow_delegation=True,
            verbose=True,
            llm=llm,  # 使用DeepSeek LLM
            system_prompt=get_deepseek_prompt_for_interviewer("product_manager") if use_deepseek else None
        )
        
        # 创建行为面试官
        self.interview_agents["behavioral"] = Agent(
            role="行为面试官",
            goal="评估候选人的综合素质",
            backstory="""你是一位专业的行为面试官，擅长提出行为面试问题，了解候选人的过往经历和行为模式，
            评估候选人的沟通能力、团队合作能力、领导力等。你需要根据候选人应聘的职位 {position} 
            和面试难度 {difficulty} 调整问题的深度和广度。""".format(
                position=position, difficulty=difficulty
            ),
            allow_delegation=True,
            verbose=True,
            llm=llm,  # 使用DeepSeek LLM
            system_prompt=get_deepseek_prompt_for_interviewer("behavioral") if use_deepseek else None
        )
        
        # 创建HR面试官
        self.interview_agents["hr"] = Agent(
            role="HR面试官",
            goal="评估候选人与公司文化的匹配程度，进行薪资谈判",
            backstory="""你是一位资深的HR面试官，擅长了解候选人的价值观，评估其与公司文化的匹配程度，
            并与候选人进行薪资谈判，达成双方都满意的薪资协议。你需要根据候选人应聘的职位 {position} 
            和面试难度 {difficulty} 调整问题的深度和广度。""".format(
                position=position, difficulty=difficulty
            ),
            allow_delegation=True,
            verbose=True,
            llm=llm,  # 使用DeepSeek LLM
            system_prompt=get_deepseek_prompt_for_interviewer("hr") if use_deepseek else None
        )
        
        logger.info("面试智能体初始化完成")
        return self.interview_agents
    
    async def initialize_interview_tasks(self, resume_context: str = ""):
        """
        初始化面试任务 - 针对层级执行模式优化
        
        Args:
            resume_context: 简历上下文（可选）
        """
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法初始化面试任务")
            
        logger.info("初始化面试任务")
        
        # 创建主任务 - 面试协调员作为管理者角色
        main_task = Task(
            description=f"""
            你是一个面试协调员，负责组织一场针对'{self.position}'职位的面试，难度为{self.difficulty}。
            面试应该全面评估候选人的能力，包括技术能力、产品思维、综合素质和与公司文化的契合度。
            
            【你作为面试协调员的核心职责】：
            1. 管理整个面试流程，确保有序进行
            2. 根据不同阶段委派任务给相应的专业面试官
            3. 引导面试方向，确保覆盖所有重要评估点
            4. 在面试官之间进行平滑过渡
            5. 最终汇总所有面试官的评估生成综合报告
            
            【面试流程】：
            1. 介绍阶段：由你负责介绍面试，欢迎候选人，请他们做自我介绍
            2. 技术面试阶段：委派技术面试官评估候选人的技术能力
            3. 产品面试阶段：委派产品经理面试官评估候选人的产品思维
            4. 行为面试阶段：委派行为面试官评估候选人的综合素质
            5. HR面试阶段：委派HR面试官评估与公司文化契合度
            6. 总结阶段：由你总结面试，并生成最终评估报告
            
            {f'【候选人简历信息】：{resume_context}' if resume_context else ''}
            
            【关键指令】：
            - 在每个阶段开始时，使用委派工具(delegate_work)将任务委派给相应面试官
            - 在需要了解更多信息时，使用提问工具(ask_question)向其他面试官咨询
            - 确保每个面试环节评估重点明确，不重复
            - 监控面试进度，适时引导下一个环节
            - 面试结束时整合所有面试官的评估，生成综合报告
            
            【最终交付】：
            生成一份综合评估报告，包括：
            - 候选人各方面能力的评分(1-100)和具体评价
            - 总体推荐意见（强烈推荐、推荐、考虑、不推荐）
            - 优势和待提升方面的具体分析
            """,
            agent=self.interview_agents["coordinator"],
            expected_output="完整的面试过程记录和评估报告"
        )
        
        # 技术面试任务
        technical_task = Task(
            description=f"""
            你是技术面试官，负责评估应聘'{self.position}'职位的候选人的技术能力，面试难度为{self.difficulty}。
            
            【评估重点】：
            - 技术知识深度和广度
            - 解决问题的能力
            - 代码质量和工程实践
            - 系统设计思路
            - 技术学习能力
            
            {f'候选人简历中的技术背景：{resume_context}' if resume_context else ''}
            
            请提出针对性的技术问题，深入评估候选人的技术实力。你的问题应该由浅入深，覆盖基础知识和高级概念。
            根据候选人的回答，给出1-100分的技术能力评分，并提供详细的评价。
            """,
            agent=self.interview_agents["technical"],
            expected_output="技术能力评估报告，包含评分和详细评价"
        )
        
        # 产品面试任务
        product_task = Task(
            description=f"""
            你是产品面试官，负责评估应聘'{self.position}'职位的候选人的产品思维，面试难度为{self.difficulty}。
            
            【评估重点】：
            - 产品思维和用户视角
            - 市场分析能力
            - 产品设计理念
            - 产品策略和决策能力
            - 跨部门协作能力
            
            {f'候选人简历中的产品经验：{resume_context}' if resume_context else ''}
            
            请提出产品相关的问题，评估候选人的产品思维和设计能力。你可以设计产品案例或情景问题。
            根据候选人的回答，给出1-100分的产品能力评分，并提供详细的评价。
            """,
            agent=self.interview_agents["product_manager"],
            expected_output="产品能力评估报告，包含评分和详细评价"
        )
        
        # 行为面试任务
        behavioral_task = Task(
            description=f"""
            你是行为面试官，负责评估应聘'{self.position}'职位的候选人的综合素质，面试难度为{self.difficulty}。
            
            【评估重点】：
            - 沟通能力和表达清晰度
            - 团队协作能力
            - 领导力和影响力
            - 解决冲突的能力
            - 学习成长意愿
            
            {f'候选人简历中的软技能和经历：{resume_context}' if resume_context else ''}
            
            请使用STAR法则（情境、任务、行动、结果）提问，评估候选人的行为模式和工作风格。
            根据候选人的回答，给出1-100分的综合素质评分，并提供详细的评价。
            """,
            agent=self.interview_agents["behavioral"],
            expected_output="综合素质评估报告，包含评分和详细评价"
        )
        
        # HR面试任务
        hr_task = Task(
            description=f"""
            你是HR面试官，负责评估应聘'{self.position}'职位的候选人与公司文化的契合度，面试难度为{self.difficulty}。
            
            【评估重点】：
            - 价值观与公司文化的匹配度
            - 职业发展规划
            - 稳定性和忠诚度
            - 薪资期望的合理性
            - 入职意愿和时间
            
            {f'候选人简历中的职业经历：{resume_context}' if resume_context else ''}
            
            请提出关于候选人职业规划、工作动机和价值观的问题，评估其与公司文化的契合度。
            根据候选人的回答，给出1-100分的文化契合度评分，并提供详细的评价。
            """,
            agent=self.interview_agents["hr"],
            expected_output="文化契合度评估报告，包含评分和详细评价"
        )
        
        # 保存所有任务
        self.interview_tasks["main"] = main_task
        self.interview_tasks["technical"] = technical_task
        self.interview_tasks["product"] = product_task
        self.interview_tasks["behavioral"] = behavioral_task
        self.interview_tasks["hr"] = hr_task
        
        # 注意：在层级执行模式下，我们不需要显式设置任务依赖关系
        # 协调员作为经理角色会自动决定任务的分配和执行顺序
        
        logger.info("面试任务初始化完成")
        return self.interview_tasks
    
    async def initialize_interview_crew(self):
        """初始化面试团队"""
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法初始化面试团队")
            
        if not self.interview_agents or not self.interview_tasks:
            raise ValueError("请先初始化面试智能体和面试任务")
            
        logger.info("初始化面试团队")
        
        # 配置协调员作为管理者智能体
        coordinator_agent = self.interview_agents.get('coordinator')
        
        # 如果没有找到协调员智能体，则创建一个
        if not coordinator_agent:
            logger.warning("未找到面试协调员智能体，创建默认协调员")
            from ...agents.interviewer_factory import InterviewerFactory
            factory = InterviewerFactory()
            coordinator_agent = factory.get_coordinator_agent()
        
        # 创建Crew，指定协调员作为管理者智能体
        self.interview_crew = Crew(
            agents=list(self.interview_agents.values()),
            tasks=list(self.interview_tasks.values()),
            process=Process.hierarchical,  # 使用层级执行模式
            manager_agent=coordinator_agent,  # 明确指定协调员作为管理者
            verbose=True
        )
        
        logger.info(f"面试团队初始化完成: {len(self.interview_agents)} 个智能体, {len(self.interview_tasks)} 个任务, 管理者: {coordinator_agent.role}")
        
        return self.interview_crew
    
    async def conduct_interview(self, resume_context: str = "", position: str = "通用职位", difficulty: str = "medium"):
        """
        执行完整面试流程
        
        Args:
            resume_context: 简历上下文（可选）
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            Dict: 面试报告
        """
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法执行面试")
            
        logger.info(f"开始执行面试：职位 {position}，难度 {difficulty}")
        
        # 初始化面试智能体
        await self.initialize_interview_agents(position, difficulty)
        
        # 初始化面试任务
        await self.initialize_interview_tasks(resume_context)
        
        # 初始化面试团队
        await self.initialize_interview_crew()
        
        # 执行面试
        try:
            logger.info("开始执行面试流程")
            result = self.interview_crew.kickoff()
            logger.info("面试流程执行完成")
            return {
                "status": "success",
                "report": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"执行面试失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def conduct_interview_round(self, interviewer_type: str, messages: List[Dict[str, Any]], position: str = "通用职位", difficulty: str = "medium"):
        """
        执行单轮面试（单个面试官）
        
        Args:
            interviewer_type: 面试官类型 (coordinator, technical, product, behavioral, hr)
            messages: 面试消息历史
            position: 面试职位
            difficulty: 面试难度
            
        Returns:
            str: 面试官的回复
        """
        if not self.available:
            raise CrewAINotAvailableError("CrewAI不可用，无法执行单轮面试")
        
        # 获取面试上下文
        interview_context = ""
        for msg in messages[-10:]:  # 只取最近10条消息
            sender = "候选人" if msg.get("sender_type") == "user" else "面试官"
            interview_context += f"{sender}: {msg.get('content', '')}\n"
        
        # 检查是否可以使用DeepSeek API
        use_deepseek = is_deepseek_available()
        if use_deepseek:
            logger.info(f"单轮面试使用DeepSeek API: {interviewer_type}")
            from crewai import LLM
            
            # 配置DeepSeek LLM
            model_config = get_deepseek_model_config()
            llm = LLM(
                model=f"deepseek/{model_config['model']}",
                temperature=model_config['temperature'],
                max_tokens=model_config['max_tokens'],
                api_key=model_config['api_key'],
                api_base=model_config['api_base']
            )
            logger.info("单轮面试 DeepSeek LLM初始化完成")
        else:
            logger.info(f"单轮面试使用默认LLM: {interviewer_type}")
            llm = None
        
        # 创建临时Agent
        if interviewer_type == "technical":
            agent_role = "技术面试官"
            goal = "评估候选人的技术能力"
            backstory = f"你是一位资深的技术面试官，正在面试应聘{position}职位的候选人，难度设置为{difficulty}。"
            system_prompt = get_deepseek_prompt_for_interviewer("technical") if use_deepseek else None
        elif interviewer_type == "product":
            agent_role = "产品面试官"
            goal = "评估候选人的产品sense和产品设计能力"
            backstory = f"你是一位资深的产品面试官，正在面试应聘{position}职位的候选人，难度设置为{difficulty}。"
            system_prompt = get_deepseek_prompt_for_interviewer("product_manager") if use_deepseek else None
        elif interviewer_type == "behavioral":
            agent_role = "行为面试官"
            goal = "评估候选人的综合素质"
            backstory = f"你是一位专业的行为面试官，正在面试应聘{position}职位的候选人，难度设置为{difficulty}。"
            system_prompt = get_deepseek_prompt_for_interviewer("behavioral") if use_deepseek else None
        elif interviewer_type == "hr":
            agent_role = "HR面试官"
            goal = "评估候选人与公司文化的匹配程度，进行薪资谈判"
            backstory = f"你是一位资深的HR面试官，正在面试应聘{position}职位的候选人，难度设置为{difficulty}。"
            system_prompt = get_deepseek_prompt_for_interviewer("hr") if use_deepseek else None
        else:  # coordinator 或其他
            agent_role = "面试协调员"
            goal = "协调面试流程，委派任务给专业面试官，生成面试报告"
            backstory = f"""你是一位经验丰富的面试协调员，正在组织应聘{position}职位的候选人的面试，难度设置为{difficulty}。
            你的责任是管理整个面试流程，将不同环节的任务委派给相应的专业面试官，并确保面试覆盖所有重要评估点。
            当需要深入评估候选人的特定能力时，你可以向相应的专业面试官提问或委派任务。
            """
            system_prompt = get_deepseek_prompt_for_interviewer("coordinator") if use_deepseek else None
        
        agent = Agent(
            role=agent_role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            llm=llm,  # 使用DeepSeek LLM
            system_prompt=system_prompt
        )
        
        # 创建临时任务
        if interviewer_type == "coordinator":
            task = Task(
                description=f"""根据以下面试记录，继续面试协调工作：
{interview_context}

请作为面试协调员，根据当前面试的阶段和进度，执行以下操作：

1. 判断当前面试处于哪个阶段：技术面试、产品面试、行为面试、HR面试或总结阶段
2. 如果需要切换到下一个面试阶段，则进行面试阶段过渡，并委派对应的面试官
3. 如果在当前阶段需要了解候选人的特定能力，可以直接提问或协调其他面试官参与
4. 如果已完成所有面试阶段，请生成总结性评估

要求：
- 保持专业性和高效的面试流程
- 确保全面评估候选人的能力
- 在合适的时机切换面试阶段或面试官
""",
                agent=agent
            )
        else:
            task = Task(
                description=f"根据以下面试记录，继续面试候选人：\n{interview_context}\n\n请作为{agent_role}，根据候选人的回答给出专业、有深度的评价或提问。",
                agent=agent
        )
        
        # 创建临时Crew并执行
        # 对于单轮面试，我们仍使用sequential流程，因为只有一个智能体和一个任务
        # 这与主面试流程的hierarchical模式不冲突
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            logger.info(f"执行单轮面试：{interviewer_type}")
            result = crew.kickoff()
            logger.info("单轮面试执行完成")
            return result
        except Exception as e:
            logger.error(f"执行单轮面试失败: {str(e)}")
            raise e


# 创建全局实例
crewai_integration = CrewAIIntegration()


def get_crewai_integration() -> CrewAIIntegration:
    """获取CrewAI集成实例"""
    return crewai_integration 