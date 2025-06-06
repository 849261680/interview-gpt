"""
集中化LLM配置模块
符合CrewAI官方规范，提供统一的LLM配置管理
"""
import os
import logging
from typing import Optional, Dict, Any
from crewai import LLM

logger = logging.getLogger(__name__)

# DeepSeek API配置
DEEPSEEK_API_KEY_ENV = "DEEPSEEK_API_KEY"
DEEPSEEK_API_BASE_ENV = "DEEPSEEK_API_BASE"
DEFAULT_DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_CHAT_MODEL = "deepseek-chat"

def is_deepseek_available() -> bool:
    """检查是否设置了DeepSeek API密钥"""
    return bool(os.getenv(DEEPSEEK_API_KEY_ENV))

def get_deepseek_api_key() -> Optional[str]:
    """获取DeepSeek API密钥"""
    api_key = os.getenv(DEEPSEEK_API_KEY_ENV)
    if not api_key:
        logger.warning(f"DeepSeek API密钥未设置，请在环境变量中设置{DEEPSEEK_API_KEY_ENV}")
        return None
    return api_key

def get_deepseek_api_base() -> str:
    """获取DeepSeek API基础URL"""
    return os.getenv(DEEPSEEK_API_BASE_ENV, DEFAULT_DEEPSEEK_API_BASE)

def create_deepseek_llm() -> Optional[LLM]:
    """
    创建DeepSeek LLM实例
    
    Returns:
        LLM: 配置好的DeepSeek LLM实例，如果不可用则返回None
    """
    if not is_deepseek_available():
        logger.warning("DeepSeek API不可用，无法创建LLM实例")
        return None
    
    try:
        llm = LLM(
            model=f"deepseek/{DEEPSEEK_CHAT_MODEL}",
            temperature=0.7,
            max_tokens=4000,
            api_key=get_deepseek_api_key(),
            api_base=get_deepseek_api_base()
        )
        logger.info("DeepSeek LLM实例创建成功")
        return llm
    except Exception as e:
        logger.error(f"创建DeepSeek LLM实例失败: {str(e)}")
        return None

def get_default_llm() -> Optional[LLM]:
    """
    获取默认LLM实例
    优先使用DeepSeek，如果不可用则返回None
    
    Returns:
        LLM: 默认LLM实例
    """
    # 优先使用DeepSeek
    deepseek_llm = create_deepseek_llm()
    if deepseek_llm:
        return deepseek_llm
    
    logger.warning("没有可用的LLM配置，请设置相应的API密钥")
    return None

# 全局LLM实例（单例模式）
_global_llm_instance: Optional[LLM] = None

def get_llm() -> Optional[LLM]:
    """
    获取全局LLM实例（单例模式）
    
    Returns:
        LLM: 全局LLM实例
    """
    global _global_llm_instance
    
    if _global_llm_instance is None:
        _global_llm_instance = get_default_llm()
    
    return _global_llm_instance

def reset_llm():
    """重置全局LLM实例，强制重新创建"""
    global _global_llm_instance
    _global_llm_instance = None
    logger.info("全局LLM实例已重置")

# 为了向后兼容，保留原有的函数名
def get_deepseek_model_config(model_name: str = DEEPSEEK_CHAT_MODEL) -> Dict[str, Any]:
    """
    获取DeepSeek模型配置（向后兼容）
    
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