#!/usr/bin/env python3
"""
测试 MiniMax MCP text_to_audio 功能
"""
import subprocess
import json
import os
import tempfile

def test_minimax_mcp_tts():
    print('=== MiniMax MCP TTS 测试 ===')
    
    # 检查环境变量
    api_key = os.getenv("MINIMAX_API_KEY", "")
    group_id = os.getenv("MINIMAX_GROUP_ID", "")
    
    if not api_key or not group_id:
        print("❌ 环境变量未正确设置")
        return False
    
    print("✅ 环境变量已正确设置")
    
    try:
        # 创建临时输出目录
        output_dir = tempfile.mkdtemp()
        print(f"输出目录: {output_dir}")
        
        # 测试text_to_audio
        print('\n测试 text_to_audio...')
        request = {
            'tool': 'text_to_audio',
            'query': {
                "text": "你好，欢迎参加面试！",
                "voice_id": "female-shaonv",
                "model": "speech-02-hd",
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0,
                "emotion": "happy",
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "output_directory": output_dir
            }
        }
        
        print(f"发送请求: {json.dumps(request, indent=2, ensure_ascii=False)}")
        
        proc = subprocess.Popen(
            ['minimax-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )
        
        request_json = json.dumps(request) + '\n'
        stdout, stderr = proc.communicate(input=request_json, timeout=30)
        
        print(f'返回码: {proc.returncode}')
        if stdout:
            print(f'标准输出: {stdout}')
        if stderr:
            print(f'错误输出: {stderr}')
        
        # 检查输出目录中的文件
        files = os.listdir(output_dir)
        print(f'输出目录中的文件: {files}')
        
        if proc.returncode == 0 and stdout.strip():
            print("✅ text_to_audio 测试成功")
            return True
        else:
            print("❌ text_to_audio 测试失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        proc.kill()
        return False
    except Exception as e:
        print(f'❌ 测试异常: {e}')
        return False

if __name__ == "__main__":
    test_minimax_mcp_tts() 