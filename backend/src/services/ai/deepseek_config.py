"""DeepSeek API配置模块

提供DeepSeek API的连接配置和模型参数
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# DeepSeek API密钥环境变量名称
DEEPSEEK_API_KEY_ENV = "DEEPSEEK_API_KEY"

# DeepSeek API基础URL环境变量名称
DEEPSEEK_API_BASE_ENV = "DEEPSEEK_API_BASE"

# 默认DeepSeek API基础URL
DEFAULT_DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"

# 模型ID
DEEPSEEK_CHAT_MODEL = "deepseek-chat"
DEEPSEEK_CODER_MODEL = "deepseek-coder"

# 检查是否设置了DeepSeek API密钥
def is_deepseek_available() -> bool:
    """检查是否设置了DeepSeek API密钥"""
    return bool(os.getenv(DEEPSEEK_API_KEY_ENV))

# 获取DeepSeek API密钥
def get_deepseek_api_key() -> Optional[str]:
    """获取DeepSeek API密钥"""
    api_key = os.getenv(DEEPSEEK_API_KEY_ENV)
    if not api_key:
        logger.warning("DeepSeek API密钥未设置，请在环境变量中设置%s", DEEPSEEK_API_KEY_ENV)
        return None
    return api_key

# 获取DeepSeek API基础URL
def get_deepseek_api_base() -> str:
    """获取DeepSeek API基础URL"""
    return os.getenv(DEEPSEEK_API_BASE_ENV, DEFAULT_DEEPSEEK_API_BASE)

# 获取DeepSeek模型配置
def get_deepseek_model_config(model_name: str = DEEPSEEK_CHAT_MODEL) -> Dict[str, Any]:
    """获取DeepSeek模型配置
    
    Args:
        model_name: 模型名称，默认为deepseek-chat
        
    Returns:
        Dict[str, Any]: 模型配置
    """
    return {
        "model": model_name,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 4000,
        "api_key": get_deepseek_api_key(),
        "api_base": get_deepseek_api_base()
    }

# 为不同的面试官类型配置适当的系统提示
def get_deepseek_prompt_for_interviewer(interviewer_type: str) -> str:
    """获取面试官类型对应的系统提示
    
    Args:
        interviewer_type: 面试官类型
        
    Returns:
        str: 系统提示
    """
    prompts = {
        "resume_analyzer": "你是一位专业的简历分析师，负责分析候选人简历，提取关键信息，评估与目标职位的匹配度。请客观、全面地分析简历内容，为后续面试环节提供有价值的参考信息。",
        "hr": "你是一位资深的HR面试官，负责评估候选人与公司文化的匹配度，了解候选人的职业规划和基本情况。请保持友好而专业的态度，营造轻松的面试氛围。",
        "technical": "你是一位资深技术面试官，负责评估候选人的技术能力。请提出有深度的技术问题，并根据候选人的回答进行评估。注重考察技术思维和解决问题的能力。",
        "behavioral": "你是一位专业的行为面试官，负责评估候选人的软技能和行为模式。请使用STAR方法提问，了解候选人过去的经历和行为，评估其综合素质。",
        "interview_evaluator": "你是一位专业的面试评估官，负责收集各面试官的评价，进行综合分析和量化评分。请客观公正地生成最终评估报告，为招聘决策提供依据。",
        # 保留旧的面试官类型以兼容性
        "coordinator": "你是一位经验丰富的面试协调员，负责协调整个面试流程，引导候选人完成不同的面试环节。请保持专业、友好的态度。",
        "product_manager": "你是一位经验丰富的产品面试官，负责评估候选人的产品思维和产品设计能力。请提出产品相关的问题，了解候选人如何思考产品问题。"
    }
    
    return prompts.get(interviewer_type, prompts["hr"])
