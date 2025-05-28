"""
面试官工厂类
负责创建和管理不同类型的面试官实例
"""
from typing import Dict, Type
import logging
from .base_interviewer import BaseInterviewer
from .technical_interviewer import TechnicalInterviewer
from .hr_interviewer import HRInterviewer
from .behavioral_interviewer import BehavioralInterviewer
from .product_manager_interviewer import ProductManagerInterviewer
from .senior_interviewer import SeniorInterviewer

# 设置日志
logger = logging.getLogger(__name__)

class InterviewerFactory:
    """
    面试官工厂类
    使用工厂模式管理面试官的创建和获取
    """
    
    # 面试官类型映射
    _interviewer_types: Dict[str, Type[BaseInterviewer]] = {
        "technical": TechnicalInterviewer,
        "hr": HRInterviewer,
        "behavioral": BehavioralInterviewer,
        "product_manager": ProductManagerInterviewer,
        "senior": SeniorInterviewer,
    }
    
    # 面试官实例缓存
    _interviewers: Dict[str, BaseInterviewer] = {}
    
    @classmethod
    def get_interviewer(cls, interviewer_id: str) -> BaseInterviewer:
        """
        获取面试官实例
        如果实例不存在，则创建新实例
        
        Args:
            interviewer_id: 面试官ID
            
        Returns:
            BaseInterviewer: 面试官实例
            
        Raises:
            ValueError: 如果面试官类型不存在
        """
        # 检查缓存中是否已有该实例
        if interviewer_id in cls._interviewers:
            return cls._interviewers[interviewer_id]
        
        # 检查面试官类型是否有效
        if interviewer_id not in cls._interviewer_types:
            logger.error(f"无效的面试官类型: {interviewer_id}")
            raise ValueError(f"无效的面试官类型: {interviewer_id}")
        
        # 创建新的面试官实例
        interviewer_class = cls._interviewer_types[interviewer_id]
        interviewer = interviewer_class()
        
        # 缓存实例
        cls._interviewers[interviewer_id] = interviewer
        logger.info(f"创建面试官: {interviewer_id}")
        
        return interviewer
    
    @classmethod
    def get_all_interviewer_types(cls) -> Dict[str, str]:
        """
        获取所有可用的面试官类型
        
        Returns:
            Dict[str, str]: 面试官ID和描述的映射
        """
        return {
            "technical": "技术面试官",
            "hr": "HR面试官",
            "behavioral": "行为面试官",
        }
    
    @classmethod
    def get_interviewer_sequence(cls) -> list:
        """
        获取面试官顺序
        
        Returns:
            list: 面试官ID列表，按照面试进行的顺序排列
        """
        return ["technical", "behavioral", "hr"]
