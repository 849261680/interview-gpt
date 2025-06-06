#!/usr/bin/env python3
"""
测试异步面试创建流程
验证面试创建立即返回，CrewAI流程在后台执行
"""
import requests
import time
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_async_interview_creation():
    """测试异步面试创建"""
    
    # API基础URL
    base_url = "http://localhost:8000/api"
    
    logger.info("=== 测试异步面试创建流程 ===")
    
    # 1. 测试面试创建（应该立即返回）
    logger.info("1. 创建面试会话...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/interviews/",
            data={
                "position": "AI应用工程师",
                "difficulty": "medium"
            },
            timeout=10  # 设置10秒超时，应该远小于这个时间
        )
        
        creation_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            interview_id = result.get("id")
            
            logger.info(f"✅ 面试创建成功！")
            logger.info(f"   面试ID: {interview_id}")
            logger.info(f"   创建耗时: {creation_time:.2f}秒")
            logger.info(f"   初始状态: {result.get('status')}")
            
            if creation_time < 5:  # 如果创建时间小于5秒，说明是异步的
                logger.info("✅ 面试创建是异步的，符合预期")
            else:
                logger.warning("⚠️ 面试创建耗时较长，可能仍是同步的")
            
            # 2. 检查面试状态变化
            logger.info("2. 监控面试状态变化...")
            
            for i in range(10):  # 监控10次，每次间隔2秒
                time.sleep(2)
                
                try:
                    status_response = requests.get(f"{base_url}/interview-process/{interview_id}/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get("status")
                        current_stage = status_data.get("current_stage", "unknown")
                        
                        logger.info(f"   第{i+1}次检查: 状态={current_status}, 阶段={current_stage}")
                        
                        if current_status == "active":
                            logger.info("✅ 面试状态已变为active，CrewAI流程已启动")
                            break
                    else:
                        logger.warning(f"获取状态失败: {status_response.status_code}")
                        
                except Exception as e:
                    logger.error(f"检查状态时出错: {str(e)}")
            
            return interview_id
            
        else:
            logger.error(f"❌ 面试创建失败: {response.status_code}")
            logger.error(f"   错误信息: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("❌ 面试创建超时（超过10秒），可能仍是同步执行")
        return None
    except Exception as e:
        logger.error(f"❌ 面试创建异常: {str(e)}")
        return None

def test_websocket_connection(interview_id):
    """测试WebSocket连接"""
    logger.info("3. 测试WebSocket连接...")
    
    try:
        import websocket
        
        ws_url = f"ws://localhost:8000/api/interview-process/{interview_id}/ws"
        
        def on_message(ws, message):
            data = json.loads(message)
            logger.info(f"   WebSocket消息: {data.get('type')} - {data.get('data', {}).get('message', '')}")
        
        def on_error(ws, error):
            logger.error(f"   WebSocket错误: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.info("   WebSocket连接关闭")
        
        def on_open(ws):
            logger.info("✅ WebSocket连接成功")
            # 发送一条测试消息
            ws.send(json.dumps({
                "type": "user_message",
                "data": {
                    "content": "你好，我准备开始面试了"
                }
            }))
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # 运行5秒后关闭
        import threading
        def close_after_delay():
            time.sleep(5)
            ws.close()
        
        threading.Thread(target=close_after_delay).start()
        ws.run_forever()
        
    except ImportError:
        logger.warning("websocket-client未安装，跳过WebSocket测试")
    except Exception as e:
        logger.error(f"WebSocket测试失败: {str(e)}")

if __name__ == "__main__":
    # 测试异步面试创建
    interview_id = test_async_interview_creation()
    
    if interview_id:
        # 测试WebSocket连接
        test_websocket_connection(interview_id)
    
    logger.info("=== 测试完成 ===") 