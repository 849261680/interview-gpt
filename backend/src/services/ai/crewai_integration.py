"""
CrewAI集成服务 - 使用官方顺序流程
采用CrewAI官方推荐的Sequential Process进行面试
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# 尝试导入CrewAI组件
try:
    from crewai import Agent, Task, Crew, Process, LLM
    CREWAI_AVAILABLE = True
    logger.info("CrewAI功能已启用")
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI功能禁用，无法使用多智能体协作")

# 导入传统架构（现在作为主要架构）
try:
    from .interview_crew import get_interview_crew_manager, is_crewai_available
except ImportError:
    try:
        from backend.src.services.ai.interview_crew import get_interview_crew_manager, is_crewai_available
    except ImportError:
        from services.ai.interview_crew import get_interview_crew_manager, is_crewai_available

# 导入配置
try:
    from ...config.llm_config import get_llm, is_deepseek_available, get_deepseek_model_config
except ImportError:
    try:
        from backend.src.config.llm_config import get_llm, is_deepseek_available, get_deepseek_model_config
    except ImportError:
        from config.llm_config import get_llm, is_deepseek_available, get_deepseek_model_config


class CrewAINotAvailableError(Exception):
    """当CrewAI不可用时抛出的异常"""
    pass


class CrewAIIntegration:
    """
    CrewAI集成服务 - 使用官方顺序流程
    
    采用CrewAI官方推荐的Sequential Process进行面试
    任务按预定顺序执行：简历分析 → 技术面试 → 产品经理面试 → 行为面试 → HR面试
    """
    
    def __init__(self):
        """初始化CrewAI集成服务"""
        self.available = CREWAI_AVAILABLE
        
        # 检查Crew架构可用性
        self.crew_available = is_crewai_available()
        
        if self.crew_available:
            logger.info("✅ 使用CrewAI官方顺序流程（Sequential Process）")
            try:
                self.crew_manager = get_interview_crew_manager()
            except Exception as e:
                logger.warning(f"Crew管理器创建失败: {str(e)}")
                self.crew_manager = None
            self.architecture_mode = "sequential"
        else:
            logger.error("❌ CrewAI功能不可用")
            self.architecture_mode = "none"
            self.crew_manager = None
        
        # 传统属性（向后兼容）
        self.interview_agents = {}
        self.interview_tasks = {}
        self.interview_crew = None
        self.persistent_interviewers = {}
        self.interviewer_conversations = {}
        
        logger.info(f"CrewAI集成服务初始化完成，架构模式: {self.architecture_mode}")
    
    def is_available(self) -> bool:
        """检查CrewAI服务是否可用"""
        return self.available and self.crew_available
    
    def get_status(self) -> Dict[str, Any]:
        """获取CrewAI服务状态"""
        # 安全获取活跃Crew数量
        active_crews = 0
        if self.crew_available and hasattr(self, 'crew_manager') and self.crew_manager:
            try:
                if hasattr(self.crew_manager, 'active_crews'):
                    active_crews = len(self.crew_manager.active_crews)
            except:
                active_crews = 0
        
        return {
            "available": self.available,
            "crew_available": self.crew_available,
            "architecture_mode": self.architecture_mode,
            "deepseek_available": is_deepseek_available(),
            "active_crews": active_crews,
            "process_type": "sequential"
        }
    
    async def initialize_interview(
        self,
        interview_id: str,
        position: str = "通用职位",
        difficulty: str = "medium",
        resume_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        初始化面试会话 - 使用顺序流程
        
        Args:
            interview_id: 面试ID
            position: 面试职位
            difficulty: 面试难度
            resume_file_path: 简历文件路径（可选）
            
        Returns:
            Dict: 初始化结果
        """
        if not self.is_available():
            raise CrewAINotAvailableError("CrewAI不可用，无法初始化面试")
        
        logger.info(f"初始化面试会话：ID={interview_id}, 职位={position}, 难度={difficulty}, 简历文件={resume_file_path}")
        
        try:
            # 使用Crew架构初始化（顺序流程）
            if hasattr(self, 'crew_manager') and self.crew_manager:
                return await self.crew_manager.initialize_interview(
                    interview_id=interview_id,
                    position=position,
                    difficulty=difficulty,
                    resume_file_path=resume_file_path
                )
            else:
                raise CrewAINotAvailableError("Crew管理器不可用")
                
        except Exception as e:
            logger.error(f"初始化面试会话失败: {str(e)}")
            return {
                "status": "error",
                "interview_id": interview_id,
                "error": str(e),
                "architecture_used": self.architecture_mode,
                "timestamp": datetime.now().isoformat()
            }
    
    async def conduct_interview(
        self, 
        resume_context: str = "", 
        position: str = "通用职位", 
        difficulty: str = "medium",
        interview_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行完整面试流程 - 使用顺序流程
        
        Args:
            resume_context: 简历上下文
            position: 面试职位
            difficulty: 面试难度
            interview_id: 面试ID（可选，如果不提供会自动生成）
            
        Returns:
            Dict: 面试报告
        """
        if not self.is_available():
            raise CrewAINotAvailableError("CrewAI不可用，无法执行面试")
        
        # 生成面试ID
        if not interview_id:
            interview_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"开始执行面试：ID={interview_id}, 职位={position}, 难度={difficulty}, 架构={self.architecture_mode}")
        
        try:
            # 使用Crew架构（顺序流程）
            return await self.crew_manager.conduct_interview(
                crew_id=interview_id,
                position=position,
                difficulty=difficulty,
                resume_context=resume_context
            )
                
        except Exception as e:
            logger.error(f"执行面试失败: {str(e)}")
            return {
                "status": "error",
                "interview_id": interview_id,
                "error": str(e),
                "architecture_used": self.architecture_mode,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_interview_status(self, interview_id: str) -> Dict[str, Any]:
        """
        获取面试状态
        
        Args:
            interview_id: 面试ID
            
        Returns:
            Dict: 面试状态信息
        """
        if self.architecture_mode == "sequential":
            crew = self.crew_manager.get_interview_crew(interview_id)
            if crew:
                return {
                    "interview_id": interview_id,
                    "status": "active",
                    "current_stage": "unknown",
                    "architecture": "sequential"
                }
        
        return {
            "interview_id": interview_id,
            "status": "not_found",
            "architecture": self.architecture_mode
        }
    
    def get_interview_report(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """
        获取面试报告
        
        Args:
            interview_id: 面试ID
            
        Returns:
            Dict: 面试报告，如果不存在返回None
        """
        if self.architecture_mode == "sequential":
            crew = self.crew_manager.get_interview_crew(interview_id)
            if crew:
                # 这里可以添加获取报告的逻辑
                return {
                    "interview_id": interview_id,
                    "status": "completed",
                    "architecture": "sequential"
                }
        
        return None
    
    def list_active_interviews(self) -> List[str]:
        """
        列出所有活跃的面试
        
        Returns:
            List[str]: 活跃面试ID列表
        """
        if self.architecture_mode == "sequential":
            return self.crew_manager.list_active_crews()
        else:
            return []
    
    def cleanup_interview(self, interview_id: str) -> bool:
        """
        清理面试资源
        
        Args:
            interview_id: 面试ID
            
        Returns:
            bool: 清理是否成功
        """
        if self.architecture_mode == "sequential":
            return self.crew_manager.remove_interview_crew(interview_id)
        else:
            return False
    


    def get_available_interviewers(self) -> List[str]:
        """
        获取可用的面试官列表
        
        Returns:
            List[str]: 面试官类型列表
        """
        return ["resume_analyzer", "technical_interviewer", "product_manager_interviewer", "behavioral_interviewer", "hr_interviewer"]


# 全局实例
_crewai_integration = None

def get_crewai_integration() -> CrewAIIntegration:
    """
    获取CrewAI集成服务的全局实例
    
    Returns:
        CrewAI集成服务实例
    """
    global _crewai_integration
    if _crewai_integration is None:
        _crewai_integration = CrewAIIntegration()
    return _crewai_integration 