"""
CrewAI集成模块
提供多智能体协作功能，用于构建复杂的面试场景
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# 强制禁用CrewAI导入，避免版本兼容性问题
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


# 创建全局实例
crewai_integration = CrewAIIntegration()


def get_crewai_integration() -> CrewAIIntegration:
    """获取CrewAI集成实例"""
    return crewai_integration 