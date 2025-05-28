"""
语音处理API端点
处理语音转文本和文本转语音请求
"""
import base64
import logging
import tempfile
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.schemas import Interview
from ...services.speech.speech_service import SpeechService

router = APIRouter()
logger = logging.getLogger(__name__)

# 创建语音服务实例
speech_service = SpeechService()

@router.post("/{interview_id}/speech_to_text")
async def convert_speech_to_text(
    interview_id: int,
    audio_data: Dict[str, str] = Body(...),
    db: Session = Depends(get_db)
):
    """
    将语音转换为文本
    
    Args:
        interview_id: 面试ID
        audio_data: 包含音频数据的字典，格式为 {"audio_data": "base64编码的音频数据"}
        db: 数据库会话
    
    Returns:
        转换后的文本
    """
    logger.info(f"处理语音转文本请求: 面试ID={interview_id}")
    
    # 验证面试是否存在
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview or interview.status != "active":
        raise HTTPException(status_code=404, detail="面试不存在或未激活")
    
    try:
        # 获取音频数据
        base64_audio = audio_data.get("audio_data")
        if not base64_audio:
            raise HTTPException(status_code=400, detail="缺少音频数据")
        
        # 将Base64解码为二进制数据
        audio_binary = base64.b64decode(base64_audio)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(audio_binary)
        
        try:
            # 调用语音服务转换为文本
            text = await speech_service.speech_to_text(temp_file_path)
            
            # 返回转换结果
            return {"text": text}
            
        finally:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        logger.error(f"语音转文本失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音转文本处理失败: {str(e)}")

@router.post("/{interview_id}/audio_response")
async def generate_audio_response(
    interview_id: int,
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    为指定消息生成语音回复
    
    Args:
        interview_id: 面试ID
        message_id: 消息ID
        db: 数据库会话
    
    Returns:
        生成的音频URL
    """
    logger.info(f"处理文本转语音请求: 面试ID={interview_id}, 消息ID={message_id}")
    
    # 验证面试是否存在
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    try:
        # 查询消息内容
        message = db.query(Message).filter(
            Message.id == message_id,
            Message.interview_id == interview_id
        ).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        # 如果消息不是面试官或系统发送的，则拒绝处理
        if message.sender_type not in ["interviewer", "system"]:
            raise HTTPException(status_code=400, detail="只能为面试官或系统消息生成语音")
        
        # 生成语音
        audio_url = await speech_service.text_to_speech(
            text=message.content,
            voice_id=message.interviewer_id or "system"
        )
        
        return {"audio_url": audio_url}
        
    except Exception as e:
        logger.error(f"生成语音回复失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成语音回复失败: {str(e)}")
