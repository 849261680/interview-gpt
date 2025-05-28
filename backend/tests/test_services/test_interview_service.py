"""
面试服务测试用例
测试面试服务的业务逻辑
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from src.services.interview_service import (
    create_interview_service,
    get_interview_service,
    send_message_service,
    get_interview_messages_service,
    end_interview_service
)
from src.models.pydantic_models import InterviewCreate, MessageCreate
from src.models.schemas import Interview, Message
from src.utils.exceptions import InterviewNotFoundError


class TestInterviewService:
    """面试服务测试类"""
    
    @pytest.mark.asyncio
    async def test_create_interview_service_success(self, db_session: Session, sample_interview_data):
        """测试成功创建面试服务"""
        interview_data = InterviewCreate(**sample_interview_data)
        
        result = await create_interview_service(interview_data, db=db_session)
        
        assert result.position == sample_interview_data["position"]
        assert result.difficulty == sample_interview_data["difficulty"]
        assert result.status == "active"
        assert result.id is not None
        
        # 验证数据库中确实创建了记录
        db_interview = db_session.query(Interview).filter(Interview.id == result.id).first()
        assert db_interview is not None
        assert db_interview.position == sample_interview_data["position"]
    
    @pytest.mark.asyncio
    async def test_create_interview_service_with_resume(self, db_session: Session, sample_interview_data):
        """测试带简历的面试创建"""
        interview_data = InterviewCreate(**sample_interview_data)
        
        # 模拟文件上传
        mock_resume = Mock()
        mock_resume.filename = "test_resume.pdf"
        mock_resume.read = AsyncMock(return_value=b"fake pdf content")
        
        with patch("os.makedirs"), patch("builtins.open", create=True) as mock_open:
            result = await create_interview_service(interview_data, resume=mock_resume, db=db_session)
            
            assert result.resume_path is not None
            assert "test_resume" not in result.resume_path  # 应该是UUID文件名
            mock_open.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_interview_service_success(self, db_session: Session, sample_interview_data):
        """测试成功获取面试服务"""
        # 先创建面试
        interview_data = InterviewCreate(**sample_interview_data)
        created_interview = await create_interview_service(interview_data, db=db_session)
        
        # 获取面试
        result = await get_interview_service(created_interview.id, db_session)
        
        assert result is not None
        assert result.id == created_interview.id
        assert result.position == sample_interview_data["position"]
    
    @pytest.mark.asyncio
    async def test_get_interview_service_not_found(self, db_session: Session):
        """测试获取不存在的面试"""
        result = await get_interview_service(99999, db_session)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_send_message_service_success(self, db_session: Session, sample_interview_data, sample_message_data):
        """测试成功发送消息服务"""
        # 先创建面试
        interview_data = InterviewCreate(**sample_interview_data)
        created_interview = await create_interview_service(interview_data, db=db_session)
        
        # 发送消息
        message_data = MessageCreate(**sample_message_data)
        result = await send_message_service(created_interview.id, message_data, db_session)
        
        assert result.content == sample_message_data["content"]
        assert result.sender_type == sample_message_data["sender_type"]
        assert result.id is not None
        
        # 验证数据库中确实创建了消息记录
        db_message = db_session.query(Message).filter(Message.id == result.id).first()
        assert db_message is not None
        assert db_message.interview_id == created_interview.id
    
    @pytest.mark.asyncio
    async def test_get_interview_messages_service(self, db_session: Session, sample_interview_data):
        """测试获取面试消息历史服务"""
        # 先创建面试
        interview_data = InterviewCreate(**sample_interview_data)
        created_interview = await create_interview_service(interview_data, db=db_session)
        
        # 发送几条消息
        message1 = MessageCreate(content="第一条消息", sender_type="user")
        message2 = MessageCreate(content="第二条消息", sender_type="interviewer", interviewer_id="technical")
        
        await send_message_service(created_interview.id, message1, db_session)
        await send_message_service(created_interview.id, message2, db_session)
        
        # 获取消息历史
        result = await get_interview_messages_service(created_interview.id, db_session)
        
        assert len(result) >= 4  # 2条系统消息 + 2条我们发送的消息
        
        # 验证消息内容
        user_messages = [msg for msg in result if msg.sender_type == "user"]
        interviewer_messages = [msg for msg in result if msg.sender_type == "interviewer"]
        
        assert len(user_messages) >= 1
        assert len(interviewer_messages) >= 1
    
    @pytest.mark.asyncio
    async def test_end_interview_service_success(self, db_session: Session, sample_interview_data):
        """测试成功结束面试服务"""
        # 先创建面试
        interview_data = InterviewCreate(**sample_interview_data)
        created_interview = await create_interview_service(interview_data, db=db_session)
        
        # 结束面试
        result = await end_interview_service(created_interview.id, db_session)
        
        assert result.status == "completed"
        assert result.completed_at is not None
        
        # 验证数据库中的状态已更新
        db_interview = db_session.query(Interview).filter(Interview.id == created_interview.id).first()
        assert db_interview.status == "completed"
        assert db_interview.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_end_interview_service_not_found(self, db_session: Session):
        """测试结束不存在的面试"""
        with pytest.raises(InterviewNotFoundError):
            await end_interview_service(99999, db_session)


class TestInterviewServiceEdgeCases:
    """面试服务边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_create_interview_database_error(self, sample_interview_data):
        """测试数据库错误情况"""
        interview_data = InterviewCreate(**sample_interview_data)
        
        # 模拟数据库错误
        mock_db = Mock()
        mock_db.add.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            await create_interview_service(interview_data, db=mock_db)
    
    @pytest.mark.asyncio
    async def test_send_message_with_interviewer_id(self, db_session: Session, sample_interview_data):
        """测试发送带面试官ID的消息"""
        # 先创建面试
        interview_data = InterviewCreate(**sample_interview_data)
        created_interview = await create_interview_service(interview_data, db=db_session)
        
        # 发送带面试官ID的消息
        message_data = MessageCreate(
            content="这是技术面试官的问题",
            sender_type="interviewer",
            interviewer_id="technical"
        )
        
        result = await send_message_service(created_interview.id, message_data, db_session)
        
        assert result.interviewer_id == "technical"
        assert result.sender_type == "interviewer"
    
    @pytest.mark.asyncio
    async def test_get_messages_empty_interview(self, db_session: Session, sample_interview_data):
        """测试获取空面试的消息历史"""
        # 创建面试但不发送任何额外消息
        interview_data = InterviewCreate(**sample_interview_data)
        created_interview = await create_interview_service(interview_data, db=db_session)
        
        # 获取消息历史
        result = await get_interview_messages_service(created_interview.id, db_session)
        
        # 应该至少有系统生成的欢迎消息
        assert len(result) >= 1
        system_messages = [msg for msg in result if msg.sender_type == "system"]
        assert len(system_messages) >= 1 