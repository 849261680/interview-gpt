"""
面试API测试用例
测试面试相关的API端点
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestInterviewAPI:
    """面试API测试类"""
    
    def test_create_interview_success(self, client: TestClient, sample_interview_data):
        """测试成功创建面试"""
        response = client.post("/api/interviews", json=sample_interview_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["position"] == sample_interview_data["position"]
        assert data["data"]["difficulty"] == sample_interview_data["difficulty"]
        assert data["data"]["status"] == "active"
        assert "id" in data["data"]
    
    def test_create_interview_invalid_data(self, client: TestClient):
        """测试创建面试时数据验证失败"""
        invalid_data = {
            "position": "",  # 空职位
            "difficulty": "invalid"  # 无效难度
        }
        
        response = client.post("/api/interviews", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_get_interview_success(self, client: TestClient, sample_interview_data):
        """测试成功获取面试"""
        # 先创建面试
        create_response = client.post("/api/interviews", json=sample_interview_data)
        interview_id = create_response.json()["data"]["id"]
        
        # 获取面试
        response = client.get(f"/api/interviews/{interview_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == interview_id
        assert data["data"]["position"] == sample_interview_data["position"]
    
    def test_get_interview_not_found(self, client: TestClient):
        """测试获取不存在的面试"""
        response = client.get("/api/interviews/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERVIEW_NOT_FOUND"
    
    def test_send_message_success(self, client: TestClient, sample_interview_data, sample_message_data):
        """测试成功发送消息"""
        # 先创建面试
        create_response = client.post("/api/interviews", json=sample_interview_data)
        interview_id = create_response.json()["data"]["id"]
        
        # 发送消息
        response = client.post(f"/api/interviews/{interview_id}/messages", json=sample_message_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["content"] == sample_message_data["content"]
        assert data["data"]["sender_type"] == sample_message_data["sender_type"]
    
    def test_send_message_interview_not_found(self, client: TestClient, sample_message_data):
        """测试向不存在的面试发送消息"""
        response = client.post("/api/interviews/99999/messages", json=sample_message_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERVIEW_NOT_FOUND"
    
    def test_get_interview_messages(self, client: TestClient, sample_interview_data, sample_message_data):
        """测试获取面试消息历史"""
        # 先创建面试
        create_response = client.post("/api/interviews", json=sample_interview_data)
        interview_id = create_response.json()["data"]["id"]
        
        # 发送几条消息
        client.post(f"/api/interviews/{interview_id}/messages", json=sample_message_data)
        client.post(f"/api/interviews/{interview_id}/messages", json={
            "content": "请详细介绍一下你的项目经验。",
            "sender_type": "interviewer",
            "interviewer_id": "technical"
        })
        
        # 获取消息历史
        response = client.get(f"/api/interviews/{interview_id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2  # 至少有我们发送的2条消息
    
    def test_end_interview_success(self, client: TestClient, sample_interview_data):
        """测试成功结束面试"""
        # 先创建面试
        create_response = client.post("/api/interviews", json=sample_interview_data)
        interview_id = create_response.json()["data"]["id"]
        
        # 结束面试
        response = client.post(f"/api/interviews/{interview_id}/end")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "completed"
        assert data["data"]["completed_at"] is not None
    
    def test_end_interview_not_found(self, client: TestClient):
        """测试结束不存在的面试"""
        response = client.post("/api/interviews/99999/end")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERVIEW_NOT_FOUND"


@pytest.mark.asyncio
class TestInterviewAPIAsync:
    """面试API异步测试类"""
    
    async def test_concurrent_message_sending(self, client: TestClient, sample_interview_data):
        """测试并发发送消息"""
        import asyncio
        
        # 创建面试
        create_response = client.post("/api/interviews", json=sample_interview_data)
        interview_id = create_response.json()["data"]["id"]
        
        # 并发发送多条消息
        async def send_message(content: str):
            return client.post(f"/api/interviews/{interview_id}/messages", json={
                "content": content,
                "sender_type": "user"
            })
        
        tasks = [
            send_message(f"消息 {i}")
            for i in range(5)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证所有消息都成功发送
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code == 200 