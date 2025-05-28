#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API 测试脚本
用于测试 DeepSeek API 的连通性和功能正确性
"""

import os
import sys
import json
import requests
import argparse
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("deepseek-test")

# 加载环境变量
load_dotenv()

# 配置选项
parser = argparse.ArgumentParser(description="测试 DeepSeek API 连接")
parser.add_argument("--host", default="localhost", help="API 主机名")
parser.add_argument("--port", default="8000", help="API 端口")
parser.add_argument("--path", default="api/deepseek", help="API 路径")
parser.add_argument("--direct", action="store_true", help="直接测试 DeepSeek API，不通过后端")
parser.add_argument("--test-failure", action="store_true", help="测试失败情况")
args = parser.parse_args()


def test_deepseek_direct():
    """直接测试 DeepSeek API (不通过我们的后端)"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("缺少 DEEPSEEK_API_KEY 环境变量")
        return False
    
    base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    logger.info(f"直接测试 DeepSeek API: {base_url}")
    logger.info(f"使用模型: {model}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一位专业的面试官，请简要介绍自己。"},
            {"role": "user", "content": "你好，请问你是谁？"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions", 
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("DeepSeek API 调用成功")
            logger.info(f"响应内容: {result['choices'][0]['message']['content'][:100]}...")
            return True
        else:
            logger.error(f"DeepSeek API 调用失败: HTTP {response.status_code}")
            logger.error(f"错误详情: {response.text}")
            return False
    except Exception as e:
        logger.error(f"DeepSeek API 调用异常: {str(e)}")
        return False


def test_backend_api():
    """测试通过后端调用 DeepSeek API"""
    host = args.host
    port = args.port
    path = args.path
    base_url = f"http://{host}:{port}"
    
    # 测试 API 状态
    logger.info(f"测试 API 状态: {base_url}/{path}/status")
    try:
        status_response = requests.get(f"{base_url}/{path}/status")
        if status_response.status_code == 200:
            logger.info(f"API 状态检查成功: {status_response.json()}")
        else:
            logger.error(f"API 状态检查失败: HTTP {status_response.status_code}")
            logger.error(f"错误详情: {status_response.text}")
            return False
    except Exception as e:
        logger.error(f"API 状态检查异常: {str(e)}")
        return False
    
    # 测试聊天 API
    logger.info(f"测试聊天 API: {base_url}/{path}/chat")
    headers = {"Content-Type": "application/json"}
    
    messages = [
        {"role": "system", "content": "你是一位专业的面试官，请简要介绍自己。"},
        {"role": "user", "content": "你好，请问你是谁？"}
    ]
    
    # 如果测试失败情况，使用无效的消息格式
    if args.test_failure:
        messages = [{"invalid_field": "invalid_value"}]
    
    data = {
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        # 首先发送 OPTIONS 请求测试 CORS
        options_response = requests.options(
            f"{base_url}/{path}/chat",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        logger.info(f"CORS 预检测试: HTTP {options_response.status_code}")
        logger.info(f"响应头: {dict(options_response.headers)}")
        
        # 然后发送实际的 POST 请求
        response = requests.post(
            f"{base_url}/{path}/chat", 
            headers=headers,
            json=data,
            timeout=30
        )
        
        logger.info(f"API 响应: HTTP {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and result.get("success", False):
            logger.info("后端 API 调用成功")
            if "data" in result and "choices" in result["data"]:
                content = result["data"]["choices"][0]["message"]["content"]
                logger.info(f"响应内容: {content[:100]}...")
            return True
        else:
            logger.error(f"后端 API 调用失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        logger.error(f"后端 API 调用异常: {str(e)}")
        return False


def main():
    logger.info("===== DeepSeek API 测试开始 =====")
    
    success = False
    if args.direct:
        logger.info("直接测试 DeepSeek API...")
        success = test_deepseek_direct()
    else:
        logger.info("通过后端测试 DeepSeek API...")
        success = test_backend_api()
    
    if success:
        logger.info("✅ 测试成功完成")
        return 0
    else:
        logger.error("❌ 测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
