# Interview-GPT API 文档

## 概述

Interview-GPT API 是一个基于 FastAPI 构建的 RESTful API，为多AI面试官系统提供后端服务。API 支持面试会话管理、实时消息交互、文件上传和面试评估等功能。

## 基础信息

- **基础URL**: `http://localhost:9999` (开发环境)
- **API版本**: v1
- **API前缀**: `/api`
- **文档地址**: `http://localhost:9999/docs` (Swagger UI)
- **ReDoc地址**: `http://localhost:9999/redoc`

## 认证

当前版本暂不需要认证，所有API端点都是公开的。未来版本将支持JWT认证。

## 响应格式

所有API响应都遵循统一的格式：

### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体的响应数据
  },
  "message": "操作成功" // 可选
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {
      // 错误详情（可选）
    },
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `VALIDATION_ERROR` | 400/422 | 数据验证失败 |
| `INTERVIEW_NOT_FOUND` | 404 | 面试会话未找到 |
| `INTERVIEWER_ERROR` | 500 | 面试官服务错误 |
| `AI_SERVICE_ERROR` | 500 | AI服务错误 |
| `FILE_UPLOAD_ERROR` | 500 | 文件上传错误 |
| `DATABASE_ERROR` | 500 | 数据库操作错误 |
| `INTERNAL_SERVER_ERROR` | 500 | 服务器内部错误 |

## API 端点

### 健康检查

#### GET /
基础健康检查端点

**响应示例:**
```json
{
  "status": "online",
  "message": "Interview-GPT API 正常运行"
}
```

#### GET /health
详细健康检查端点

**响应示例:**
```json
{
  "status": "healthy",
  "service": "Interview-GPT API",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 面试管理

#### POST /api/interviews
创建新的面试会话

**请求体:**
```json
{
  "position": "AI应用工程师",
  "difficulty": "medium"
}
```

**支持的难度级别:**
- `easy`: 初级
- `medium`: 中级  
- `hard`: 高级

**可选文件上传:**
- 支持上传简历文件 (PDF, DOC, DOCX)
- 使用 `multipart/form-data` 格式
- 文件字段名: `resume`

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "position": "AI应用工程师",
    "difficulty": "medium",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": null,
    "resume_path": "/uploads/resumes/uuid-filename.pdf",
    "overall_score": null
  }
}
```

#### GET /api/interviews/{interview_id}
获取面试会话详情

**路径参数:**
- `interview_id`: 面试会话ID

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "position": "AI应用工程师",
    "difficulty": "medium",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": null,
    "resume_path": "/uploads/resumes/uuid-filename.pdf",
    "overall_score": null
  }
}
```

#### POST /api/interviews/{interview_id}/end
结束面试会话

**路径参数:**
- `interview_id`: 面试会话ID

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "position": "AI应用工程师",
    "difficulty": "medium",
    "status": "completed",
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T01:00:00Z",
    "resume_path": "/uploads/resumes/uuid-filename.pdf",
    "overall_score": 85.5
  }
}
```

### 消息管理

#### POST /api/interviews/{interview_id}/messages
发送面试消息

**路径参数:**
- `interview_id`: 面试会话ID

**请求体:**
```json
{
  "content": "我有3年的Python开发经验，熟悉机器学习框架。",
  "sender_type": "user"
}
```

**发送者类型:**
- `user`: 用户/求职者
- `interviewer`: 面试官
- `system`: 系统消息

**面试官消息额外字段:**
```json
{
  "content": "请详细介绍你的项目经验。",
  "sender_type": "interviewer",
  "interviewer_id": "technical"
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "content": "我有3年的Python开发经验，熟悉机器学习框架。",
    "sender_type": "user",
    "interviewer_id": null,
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": null
  }
}
```

#### GET /api/interviews/{interview_id}/messages
获取面试消息历史

**路径参数:**
- `interview_id`: 面试会话ID

**查询参数:**
- `limit`: 限制返回消息数量 (可选，默认100)
- `offset`: 偏移量 (可选，默认0)

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "content": "欢迎参加模拟面试！",
      "sender_type": "system",
      "interviewer_id": null,
      "timestamp": "2024-01-01T00:00:00Z",
      "metadata": null
    },
    {
      "id": 2,
      "content": "你好，我是张工，技术面试官。",
      "sender_type": "interviewer",
      "interviewer_id": "technical",
      "timestamp": "2024-01-01T00:01:00Z",
      "metadata": null
    }
  ]
}
```

### 面试官管理

#### GET /api/interviewers
获取所有可用的面试官类型

**响应示例:**
```json
{
  "success": true,
  "data": {
    "technical": "技术面试官",
    "hr": "HR面试官",
    "behavioral": "行为面试官"
  }
}
```

#### GET /api/interviewers/sequence
获取面试官面试顺序

**响应示例:**
```json
{
  "success": true,
  "data": ["technical", "behavioral", "hr"]
}
```

### 反馈管理

#### GET /api/interviews/{interview_id}/feedback
获取面试反馈

**路径参数:**
- `interview_id`: 面试会话ID

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "interview_id": 1,
    "summary": "候选人表现良好，技术基础扎实...",
    "overall_score": 85.5,
    "skill_scores": {
      "technical": 90,
      "communication": 80,
      "problem_solving": 85
    },
    "strengths": [
      "技术基础扎实",
      "学习能力强"
    ],
    "improvements": [
      "需要提升项目管理经验",
      "可以加强算法基础"
    ],
    "created_at": "2024-01-01T01:00:00Z",
    "interviewer_feedbacks": [
      {
        "interviewer_id": "technical",
        "name": "张工",
        "role": "技术面试官",
        "content": "技术能力符合要求..."
      }
    ]
  }
}
```

## WebSocket 连接

### 连接端点
`ws://localhost:9999/api/ws/{interview_id}`

### 消息格式

#### 发送消息
```json
{
  "type": "message",
  "data": {
    "content": "消息内容",
    "sender_type": "user"
  }
}
```

#### 接收消息
```json
{
  "type": "message",
  "data": {
    "id": 1,
    "content": "面试官回复",
    "sender_type": "interviewer",
    "interviewer_id": "technical",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### 状态更新
```json
{
  "type": "status",
  "data": {
    "status": "interviewer_changed",
    "current_interviewer": "hr",
    "message": "现在由HR面试官接管面试"
  }
}
```

## 使用示例

### 创建面试会话
```bash
curl -X POST "http://localhost:9999/api/interviews" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "AI应用工程师",
    "difficulty": "medium"
  }'
```

### 发送消息
```bash
curl -X POST "http://localhost:9999/api/interviews/1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我有3年Python开发经验",
    "sender_type": "user"
  }'
```

### 获取消息历史
```bash
curl "http://localhost:9999/api/interviews/1/messages"
```

### 结束面试
```bash
curl -X POST "http://localhost:9999/api/interviews/1/end"
```

## 开发指南

### 本地开发
1. 安装依赖: `pip install -r requirements.txt`
2. 启动服务: `uvicorn src.main:app --reload --port 9999`
3. 访问文档: `http://localhost:9999/docs`

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api/test_interview.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 错误处理
API 使用全局错误处理中间件，所有异常都会被捕获并返回标准化的错误响应。开发时可以通过日志查看详细的错误信息。

## 更新日志

### v0.1.0 (2024-01-01)
- 初始版本发布
- 支持面试会话管理
- 支持消息发送和接收
- 支持文件上传
- 支持WebSocket实时通信
- 完整的错误处理机制 