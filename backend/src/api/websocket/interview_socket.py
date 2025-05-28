"""
面试WebSocket模块
处理面试过程中的实时通信
"""
import json
import logging
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ...models.schemas import Interview, Message
from ...services.interview_service import get_interview_service, send_message_service

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接: {interview_id: {client_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        # 面试会话状态: {interview_id: interview_state}
        self.interview_states: Dict[int, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, interview_id: int, client_id: str, db: Session) -> None:
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket连接
            interview_id: 面试ID
            client_id: 客户端ID
            db: 数据库会话
        """
        await websocket.accept()
        
        # 初始化面试连接字典
        if interview_id not in self.active_connections:
            self.active_connections[interview_id] = {}
        
        # 保存连接
        self.active_connections[interview_id][client_id] = websocket
        
        # 创建面试管理器（如果不存在）
        if interview_id not in self.interview_states:
            # 初始化面试状态
            self.interview_states[interview_id] = {
                "interview_id": interview_id,
                "active": True,
                "current_stage": "technical",  # 当前面试阶段（技术面试、HR面试等）
                "last_message_time": None
            }
        
        # 获取面试历史消息
        history = await self.get_history(interview_id, db)
        
        # 发送历史消息
        await self.send_personal_message(
            {
                "type": "history",
                "data": {
                    "messages": history
                }
            },
            websocket
        )
        
        # 发送当前面试状态
        status = self.interview_managers[interview_id].get_interview_status()
        await self.send_personal_message(
            {
                "type": "status",
                "data": status
            },
            websocket
        )
        
        logger.info(f"客户端 {client_id} 已连接到面试 {interview_id}")
    
    def disconnect(self, interview_id: int, client_id: str) -> None:
        """
        断开WebSocket连接
        
        Args:
            interview_id: 面试ID
            client_id: 客户端ID
        """
        if (
            interview_id in self.active_connections and 
            client_id in self.active_connections[interview_id]
        ):
            del self.active_connections[interview_id][client_id]
            
            # 如果没有连接，清理面试管理器
            if not self.active_connections[interview_id]:
                if interview_id in self.interview_managers:
                    del self.interview_managers[interview_id]
                del self.active_connections[interview_id]
                
            logger.info(f"客户端 {client_id} 已断开与面试 {interview_id} 的连接")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        """
        发送个人消息
        
        Args:
            message: 消息内容
            websocket: WebSocket连接
        """
        await websocket.send_text(json.dumps(message))
    
    async def broadcast(self, message: Dict[str, Any], interview_id: int) -> None:
        """
        广播消息给所有连接到特定面试的客户端
        
        Args:
            message: 消息内容
            interview_id: 面试ID
        """
        if interview_id in self.active_connections:
            disconnected_clients = []
            
            for client_id, websocket in self.active_connections[interview_id].items():
                try:
                    await self.send_personal_message(message, websocket)
                except Exception as e:
                    logger.error(f"广播消息失败: {e}")
                    disconnected_clients.append(client_id)
            
            # 清理断开的连接
            for client_id in disconnected_clients:
                self.disconnect(interview_id, client_id)
    
    async def get_history(self, interview_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        获取面试历史消息
        
        Args:
            interview_id: 面试ID
            db: 数据库会话
            
        Returns:
            历史消息列表
        """
        # 查询面试消息
        messages = db.query(Message).filter(
            Message.interview_id == interview_id
        ).order_by(Message.timestamp.asc()).all()
        
        # 格式化消息
        return [
            {
                "id": message.id,
                "content": message.content,
                "sender_type": message.sender_type,
                "interviewer_id": message.interviewer_id,
                "timestamp": message.timestamp.isoformat()
            } for message in messages
        ]
    
    async def process_message(self, data: Dict[str, Any], interview_id: int, db: Session) -> Dict[str, Any]:
        """
        处理接收到的消息
        
        Args:
            data: 消息数据
            interview_id: 面试ID
            db: 数据库会话
            
        Returns:
            处理结果
        """
        if interview_id not in self.interview_managers:
            return {
                "type": "error",
                "data": {
                    "message": "面试不存在或已结束"
                }
            }
        
        manager = self.interview_managers[interview_id]
        message_type = data.get("type", "")
        
        if message_type == "message":
            # 处理用户消息
            content = data.get("content", "").strip()
            if not content:
                return {
                    "type": "error",
                    "data": {
                        "message": "消息内容不能为空"
                    }
                }
            
            # 保存用户消息并获取回复
            user_msg, ai_msg = await manager.process_user_message(content, db)
            
            # 返回用户消息和AI回复
            return {
                "type": "message",
                "data": {
                    "user_message": {
                        "id": user_msg.id,
                        "content": user_msg.content,
                        "sender_type": user_msg.sender_type,
                        "timestamp": user_msg.timestamp.isoformat()
                    },
                    "ai_message": {
                        "id": ai_msg.id,
                        "content": ai_msg.content,
                        "sender_type": ai_msg.sender_type,
                        "interviewer_id": ai_msg.interviewer_id,
                        "timestamp": ai_msg.timestamp.isoformat()
                    } if ai_msg else None
                }
            }
            
        elif message_type == "next_stage":
            # 切换到下一个阶段
            stage_result = await manager.advance_to_next_stage(db)
            
            if not stage_result["success"]:
                return {
                    "type": "error",
                    "data": {
                        "message": stage_result["message"]
                    }
                }
            
            # 返回新阶段信息
            return {
                "type": "new_stage",
                "data": {
                    "stage": stage_result["stage"],
                    "message": {
                        "id": stage_result["message"].id,
                        "content": stage_result["message"].content,
                        "sender_type": stage_result["message"].sender_type,
                        "interviewer_id": stage_result["message"].interviewer_id,
                        "timestamp": stage_result["message"].timestamp.isoformat()
                    }
                }
            }
            
        elif message_type == "end_interview":
            # 结束面试
            end_result = await manager.end_interview(db)
            
            if not end_result["success"]:
                return {
                    "type": "error",
                    "data": {
                        "message": end_result["message"]
                    }
                }
            
            # 返回结束面试信息
            return {
                "type": "interview_ended",
                "data": {
                    "message": "面试已结束，正在生成评估报告",
                    "feedback_url": f"/interview/{interview_id}/feedback"
                }
            }
        
        # 未知消息类型
        return {
            "type": "error",
            "data": {
                "message": f"未知的消息类型: {message_type}"
            }
        }

# 创建全局连接管理器实例
connection_manager = ConnectionManager()

async def handle_websocket(
    websocket: WebSocket, 
    interview_id: int, 
    client_id: str, 
    db: Session
) -> None:
    """
    处理WebSocket连接
    
    Args:
        websocket: WebSocket连接
        interview_id: 面试ID
        client_id: 客户端ID
        db: 数据库会话
    """
    # 连接WebSocket
    await connection_manager.connect(websocket, interview_id, client_id, db)
    
    try:
        # 持续接收消息
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                # 解析JSON数据
                message_data = json.loads(data)
                
                # 处理消息
                response = await connection_manager.process_message(message_data, interview_id, db)
                
                # 如果是消息类型，需要广播给所有连接的客户端
                if response["type"] in ["message", "new_stage", "interview_ended"]:
                    await connection_manager.broadcast(response, interview_id)
                else:
                    # 发送个人响应
                    await connection_manager.send_personal_message(response, websocket)
                
            except json.JSONDecodeError:
                # 发送错误消息
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "data": {
                            "message": "无效的JSON数据"
                        }
                    },
                    websocket
                )
    except WebSocketDisconnect:
        # 断开连接
        connection_manager.disconnect(interview_id, client_id)
    except Exception as e:
        # 处理其他异常
        logger.error(f"WebSocket处理异常: {e}")
        connection_manager.disconnect(interview_id, client_id)
