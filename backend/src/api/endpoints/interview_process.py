"""
面试流程API端点
提供面试流程控制、面试官轮换和消息处理的API接口
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
import json

from ...db.database import get_db
from ...models.schemas import Interview, Message
from ...models.pydantic_models import MessageCreate, MessageResponse
# 使用新的CrewAI架构，不再需要InterviewerFactory
from ...services.ai.crewai_integration import get_crewai_integration
from ...services.interview_service import send_message_service, get_interview_messages_service
# 替换音频服务导入
from ...services.speech.speech_service import SpeechService
# 添加面试管理器导入
from ...services.interview.interview_manager import get_or_create_interview_manager
# 添加音频处理函数导入
from ...services.audio.text_to_speech import get_interviewer_voice, text_to_speech, save_audio_file
from ...services.audio.speech_recognition import recognize_speech

# 设置日志
logger = logging.getLogger(__name__)

# 创建语音服务实例
speech_service = SpeechService()

# 使用CrewAI集成替代面试官工厂
# interviewer_factory = InterviewerFactory()  # 已删除

# 创建路由
router = APIRouter()

# 存储活跃的WebSocket连接
active_connections: Dict[int, List[WebSocket]] = {}


@router.post("/{interview_id}/messages", response_model=MessageResponse)
async def send_message(
    interview_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    发送面试消息并获取面试官回复
    
    Args:
        interview_id: 面试ID
        message: 消息内容
        
    Returns:
        MessageResponse: 面试官回复消息
    """
    logger.info(f"发送面试消息: 面试ID={interview_id}")
    
    try:
        # 获取面试管理器
        interview_manager = await get_or_create_interview_manager(interview_id, db)
        
        # 处理用户消息并获取回复
        user_msg, ai_msg = await interview_manager.process_user_message(message.content, db)
        
        # 返回面试官回复消息
        return MessageResponse(
            id=ai_msg.id if ai_msg else user_msg.id,
            content=ai_msg.content if ai_msg else "消息已收到",
            sender_type=ai_msg.sender_type if ai_msg else "system",
            interviewer_id=ai_msg.interviewer_id if ai_msg else None,
            timestamp=ai_msg.timestamp if ai_msg else user_msg.timestamp
        )
        
    except Exception as e:
        logger.error(f"处理面试消息失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"处理面试消息失败: {str(e)}"
        )


@router.post("/{interview_id}/audio_response")
async def generate_audio_response(
    interview_id: int,
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    将面试官的文本回复转换为语音
    
    Args:
        interview_id: 面试ID
        message_id: 消息ID
        
    Returns:
        Dict[str, Any]: 包含音频URL的响应
    """
    logger.info(f"生成语音回复: 面试ID={interview_id}, 消息ID={message_id}")
    
    try:
        # 查询消息
        message = db.query(Message).filter(
            Message.id == message_id,
            Message.interview_id == interview_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=404,
                detail=f"消息不存在: ID={message_id}"
            )
        
        # 检查是否是面试官消息
        if message.sender_type != "interviewer":
            raise HTTPException(
                status_code=400,
                detail="只能为面试官消息生成语音"
            )
        
        # 获取适合的语音
        voice_id = await get_interviewer_voice(message.interviewer_id)
        
        # 将文本转换为语音
        audio_result = await text_to_speech(message.content, voice_id)
        
        if "error" in audio_result:
            raise HTTPException(
                status_code=500,
                detail=f"生成语音失败: {audio_result['error']}"
            )
        
        # 保存音频文件
        save_result = await save_audio_file(audio_result["audio_data"])
        
        if "error" in save_result:
            raise HTTPException(
                status_code=500,
                detail=f"保存音频失败: {save_result['error']}"
            )
        
        # 返回音频URL
        return {
            "audio_url": save_result["file_url"],
            "message_id": message_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成语音回复失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"生成语音回复失败: {str(e)}"
        )


@router.post("/{interview_id}/speech_to_text")
async def process_speech(
    interview_id: int,
    audio_data: str,
    db: Session = Depends(get_db)
):
    """
    处理语音输入并转换为文本
    
    Args:
        interview_id: 面试ID
        audio_data: Base64编码的音频数据
        
    Returns:
        Dict[str, Any]: 包含识别文本的响应
    """
    logger.info(f"处理语音输入: 面试ID={interview_id}")
    
    try:
        # 将语音转换为文本
        result = await recognize_speech(audio_data)
        
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=f"语音识别失败: {result['error']}"
            )
        
        return {
            "text": result["text"],
            "confidence": result["confidence"]
        }
        
    except Exception as e:
        logger.error(f"处理语音输入失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"处理语音输入失败: {str(e)}"
        )


@router.post("/{interview_id}/next_stage")
async def advance_to_next_stage(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    手动推进到下一个面试阶段
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict[str, Any]: 包含新阶段信息的响应
    """
    logger.info(f"手动推进面试阶段: 面试ID={interview_id}")
    
    try:
        # 获取面试管理器
        interview_manager = await get_or_create_interview_manager(interview_id, db)
        
        # 切换到下一个面试官
        response = await interview_manager.switch_interviewer(db)
        
        if response is None:
            return {
                "status": "completed",
                "message": "面试已完成"
            }
        
        return {
            "status": "success",
            "message": "已切换到下一阶段",
            "interviewer_message": response
        }
        
    except Exception as e:
        logger.error(f"推进面试阶段失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"推进面试阶段失败: {str(e)}"
        )


@router.post("/{interview_id}/end")
async def end_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    手动结束面试
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    logger.info(f"手动结束面试: 面试ID={interview_id}")
    
    try:
        # 获取面试管理器
        interview_manager = await get_or_create_interview_manager(interview_id, db)
        
        # 结束面试
        await interview_manager.end_interview(db)
        
        return {
            "status": "success",
            "message": "面试已结束，正在生成评估报告"
        }
        
    except Exception as e:
        logger.error(f"结束面试失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"结束面试失败: {str(e)}"
        )


@router.get("/{interview_id}/status")
async def get_interview_status(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    获取面试状态
    
    Args:
        interview_id: 面试ID
        
    Returns:
        Dict[str, Any]: 面试状态信息
    """
    logger.info(f"获取面试状态: 面试ID={interview_id}")
    
    try:
        # 查询面试记录
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(
                status_code=404,
                detail=f"面试不存在: ID={interview_id}"
            )
        
        # 统计消息数量
        message_count = db.query(Message).filter(Message.interview_id == interview_id).count()
        
        # 获取当前活跃面试官
        active_interviewer = db.query(Message).filter(
            Message.interview_id == interview_id,
            Message.sender_type == "interviewer"
        ).order_by(Message.timestamp.desc()).first()
        
        return {
            "interview_id": interview.id,
            "status": interview.status,
            "position": interview.position,
            "difficulty": interview.difficulty,
            "created_at": interview.created_at.isoformat(),
            "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
            "message_count": message_count,
            "active_interviewer": active_interviewer.interviewer_id if active_interviewer else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取面试状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取面试状态失败: {str(e)}"
        )


# WebSocket接口，用于实时面试通信
@router.websocket("/{interview_id}/ws")
async def websocket_endpoint(websocket: WebSocket, interview_id: int, db: Session = Depends(get_db)):
    """
    WebSocket接口，用于实时面试通信
    
    Args:
        websocket: WebSocket连接
        interview_id: 面试ID
    """
    await websocket.accept()
    
    try:
        # 首先验证面试是否存在
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            # 获取所有现有面试ID用于调试
            all_interviews = db.query(Interview.id, Interview.position).all()
            existing_ids = [i.id for i in all_interviews]
            
            error_message = f"面试ID {interview_id} 不存在。现有面试ID: {existing_ids}"
            logger.error(f"WebSocket连接失败: {error_message}")
            
            # 发送错误信息给前端
            await websocket.send_json({
                "type": "error",
                "data": {
                    "message": error_message,
                    "code": "INTERVIEW_NOT_FOUND",
                    "existing_interviews": existing_ids,
                    "suggested_action": "请创建新的面试或使用现有的面试ID"
                }
            })
            
            # 关闭连接
            await websocket.close(code=4004, reason="Interview not found")
            return
        
        # 添加到活跃连接
        if interview_id not in active_connections:
            active_connections[interview_id] = []
        active_connections[interview_id].append(websocket)
        
        # 获取面试管理器
        interview_manager = await get_or_create_interview_manager(interview_id, db)
        
        # 发送当前面试状态
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if interview:
            await websocket.send_json({
                "type": "status",
                "data": {
                    "interview_id": interview.id,
                    "status": interview.status,
                    "position": interview.position,
                    "difficulty": interview.difficulty
                }
            })
        
        # 发送历史消息
        messages = await interview_manager.get_interview_messages()
        await websocket.send_json({
            "type": "history",
            "data": {
                "messages": [
                    {
                        "id": msg["id"],
                        "content": msg["content"],
                        "sender_type": msg["sender_type"],
                        "interviewer_id": msg["interviewer_id"],
                        "timestamp": msg["timestamp"].isoformat() if hasattr(msg["timestamp"], "isoformat") else msg["timestamp"]
                    }
                    for msg in messages
                ]
            }
        })
        
        # 处理消息
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            
            if msg_data["type"] == "message":
                # 处理用户消息 - 确保提取正确的内容
                message_content = msg_data.get("content", "")
                if isinstance(message_content, dict):
                    # 如果content是字典，提取其中的content字段
                    message_content = message_content.get("content", "")
                elif not isinstance(message_content, str):
                    # 如果不是字符串，转换为字符串
                    message_content = str(message_content)
                
                if not message_content.strip():
                    # 发送错误消息
                    await websocket.send_json({
                        "type": "error",
                        "data": {
                            "message": "消息内容不能为空"
                        }
                    })
                    continue
                
                user_msg, ai_msg = await interview_manager.process_user_message(message_content, db)
                
                # 广播回复给所有连接
                for conn in active_connections.get(interview_id, []):
                    await conn.send_json({
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
                    })
            
            elif msg_data["type"] == "next_stage":
                # 切换到下一个阶段
                response = await interview_manager.switch_interviewer(db)
                
                if response:
                    # 广播新面试官消息
                    for conn in active_connections.get(interview_id, []):
                        await conn.send_json({
                            "type": "new_stage",
                            "data": {
                                "message": response,
                                "stage": interview_manager.current_stage
                            }
                        })
                else:
                    # 面试已结束
                    for conn in active_connections.get(interview_id, []):
                        await conn.send_json({
                            "type": "interview_ended",
                            "data": {
                                "message": "面试已结束，正在生成评估报告"
                            }
                        })
            
            elif msg_data["type"] == "end_interview":
                # 结束面试
                await interview_manager.end_interview(db)
                
                # 通知所有连接
                for conn in active_connections.get(interview_id, []):
                    await conn.send_json({
                        "type": "interview_ended",
                        "data": {
                            "message": "面试已结束，正在生成评估报告"
                        }
                    })
    
    except WebSocketDisconnect:
        # 从活跃连接中移除
        if interview_id in active_connections:
            active_connections[interview_id].remove(websocket)
            if not active_connections[interview_id]:
                del active_connections[interview_id]
    
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        # 尝试发送错误消息
        try:
            await websocket.send_json({
                "type": "error",
                "data": {
                    "message": f"服务器错误: {str(e)}"
                }
            })
        except:
            pass
        
        # 从活跃连接中移除
        if interview_id in active_connections and websocket in active_connections[interview_id]:
            active_connections[interview_id].remove(websocket)
            if not active_connections[interview_id]:
                del active_connections[interview_id]
