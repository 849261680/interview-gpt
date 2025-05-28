"""
WebSocket路由模块
处理WebSocket连接和实时通信
"""
import uuid
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..websocket.interview_socket import handle_websocket
from ...db.database import get_db

router = APIRouter()

@router.websocket("/interview-process/{interview_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    interview_id: int, 
    db: Session = Depends(get_db)
):
    """
    面试过程WebSocket端点
    处理面试过程中的实时通信
    
    Args:
        websocket: WebSocket连接
        interview_id: 面试ID
        db: 数据库会话
    """
    # 生成客户端ID
    client_id = str(uuid.uuid4())
    
    # 处理WebSocket连接
    await handle_websocket(websocket, interview_id, client_id, db)
