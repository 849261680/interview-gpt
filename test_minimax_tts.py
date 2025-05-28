#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
MiniMax MCP文本转语音测试脚本
'''

import os
import sys
import json
from datetime import datetime

# 设置输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 确保环境变量已正确设置
api_key = os.environ.get("MINIMAX_API_KEY")
group_id = os.environ.get("MINIMAX_GROUP_ID")

if not api_key or not group_id:
    print("错误: 请确保已设置MINIMAX_API_KEY和MINIMAX_GROUP_ID环境变量")
    print(f"当前API密钥长度: {len(api_key) if api_key else 0}")
    print(f"当前Group ID: {group_id if group_id else '未设置'}")
    sys.exit(1)

# 我们将直接使用API调用，不尝试导入MCP工具
print("将使用直接API调用来生成语音")

# 我们不再需要这个函数，直接使用API调用

def test_api():
    """使用MiniMax API直接生成语音"""
    import requests
    
    url = "https://api.minimax.chat/v1/text_to_speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Group-Id": group_id,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": "这是一个MiniMax API直接调用测试，生成的声音将保存在output目录中。",
        "voice": "female-qingse",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0,
        "audio_format": "mp3",
        "model": "speech-01",
        "request_id": f"tts_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    print("\n尝试直接调用MiniMax API...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 如果API返回了音频URL，下载到本地
            if "audio_url" in result:
                audio_url = result["audio_url"]
                print(f"\n成功获取音频URL: {audio_url}")
                
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    output_file = os.path.join(OUTPUT_DIR, f"api_tts_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
                    with open(output_file, "wb") as f:
                        f.write(audio_response.content)
                    print(f"成功下载音频文件: {output_file}")
                    return output_file
                else:
                    print(f"下载音频失败: {audio_response.status_code}")
            else:
                print("API响应中没有音频URL")
        else:
            print(f"API调用失败: {response.text}")
            
    except Exception as e:
        print(f"API调用过程中发生错误: {e}")
    
    return None

if __name__ == "__main__":
    print("=== MiniMax文本转语音测试 ===")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 直接调用API生成语音
    print("开始调用MiniMax API生成语音...")
    result_file = test_api()
    
    if result_file:
        print(f"\n测试成功完成! 生成的音频文件: {result_file}")
    else:
        print("\n测试失败，无法生成语音")
