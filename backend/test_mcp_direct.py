#!/usr/bin/env python3
"""
直接测试 MiniMax MCP 功能
"""
import subprocess
import json
import os
import sys

def test_minimax_mcp():
    print('=== MiniMax MCP 直接测试 ===')
    
    # 检查环境变量
    print('环境变量检查:')
    api_key = os.getenv("MINIMAX_API_KEY", "")
    group_id = os.getenv("MINIMAX_GROUP_ID", "")
    
    print(f'MINIMAX_API_KEY: {"已设置" if api_key else "未设置"} ({api_key[:50] if api_key else ""}...)')
    print(f'MINIMAX_GROUP_ID: {"已设置" if group_id else "未设置"} ({group_id})')
    
    if not api_key or not group_id:
        print("❌ 环境变量未正确设置")
        return False
    
    print("✅ 环境变量已正确设置")
    
    try:
        # 测试list_voices
        print('\n测试 list_voices...')
        request = {
            'tool': 'list_voices',
            'query': {}
        }
        
        print(f"发送请求: {request}")
        
        proc = subprocess.Popen(
            ['minimax-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )
        
        request_json = json.dumps(request) + '\n'
        print(f"请求JSON: {request_json.strip()}")
        
        stdout, stderr = proc.communicate(input=request_json, timeout=15)
        
        print(f'返回码: {proc.returncode}')
        if stdout:
            print(f'标准输出: {stdout}')
        if stderr:
            print(f'错误输出: {stderr}')
        
        if proc.returncode == 0:
            print("✅ list_voices 测试成功")
            return True
        else:
            print("❌ list_voices 测试失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        proc.kill()
        return False
    except Exception as e:
        print(f'❌ 测试异常: {e}')
        return False

if __name__ == "__main__":
    success = test_minimax_mcp()
    sys.exit(0 if success else 1) 