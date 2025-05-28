#!/usr/bin/env python3
"""
探索 MiniMax MCP 的实际API
"""
import subprocess
import json
import os

def test_mcp_tools():
    print('=== MiniMax MCP 工具探索 ===')
    
    # 检查环境变量
    api_key = os.getenv("MINIMAX_API_KEY", "")
    if not api_key:
        print("❌ 环境变量未设置")
        return
    
    print("✅ 环境变量已设置")
    
    # 尝试不同的请求格式
    test_requests = [
        {"method": "tools/list"},
        {"method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        {"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1},
    ]
    
    for i, request in enumerate(test_requests):
        print(f'\n--- 测试 {i+1}: {request} ---')
        
        try:
            proc = subprocess.Popen(
                ['minimax-mcp'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )
            
            request_json = json.dumps(request) + '\n'
            stdout, stderr = proc.communicate(input=request_json, timeout=10)
            
            print(f'返回码: {proc.returncode}')
            if stdout:
                print(f'标准输出: {stdout[:500]}...' if len(stdout) > 500 else f'标准输出: {stdout}')
            if stderr:
                print(f'错误输出: {stderr[:500]}...' if len(stderr) > 500 else f'错误输出: {stderr}')
                
        except subprocess.TimeoutExpired:
            print("超时")
            proc.kill()
        except Exception as e:
            print(f'异常: {e}')

if __name__ == "__main__":
    test_mcp_tools() 