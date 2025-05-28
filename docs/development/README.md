# Interview-GPT 开发文档

## 项目架构

### 整体架构
Interview-GPT 采用前后端分离的架构，使用 Monorepo 管理多个子项目：

```
interview-gpt/
├── frontend/          # Next.js 前端应用
├── backend/           # FastAPI 后端应用
├── shared/            # 前后端共享代码
├── docs/              # 项目文档
└── tests/             # 测试用例
```

### 后端架构

#### 分层架构
```
API Layer (FastAPI)
    ↓
Controller Layer (请求处理)
    ↓
Service Layer (业务逻辑)
    ↓
Model Layer (数据模型)
    ↓
Database Layer (SQLite/SQLAlchemy)
```

#### 核心模块

1. **API模块** (`src/api/`)
   - 路由定义和请求处理
   - WebSocket连接管理
   - 请求验证和响应格式化

2. **服务模块** (`src/services/`)
   - 面试服务 (`interview_service.py`)
   - 反馈服务 (`feedback_service.py`)
   - 语音服务 (`speech/`)

3. **AI代理模块** (`src/agents/`)
   - 基础面试官类 (`base_interviewer.py`)
   - 具体面试官实现 (技术、HR、行为等)
   - 面试官工厂 (`interviewer_factory.py`)

4. **数据模型** (`src/models/`)
   - SQLAlchemy ORM模型 (`schemas.py`)
   - Pydantic数据模型 (`pydantic_models.py`)

5. **工具模块** (`src/utils/`)
   - 自定义异常 (`exceptions.py`)
   - 通用工具函数

6. **中间件** (`src/middlewares/`)
   - 错误处理中间件 (`error_handler.py`)
   - 日志中间件
   - 认证中间件（未来）

### 前端架构

#### 技术栈
- **框架**: Next.js 14 + React 18
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: Redux Toolkit + Context API
- **UI组件**: 自定义组件库

#### 目录结构
```
frontend/src/
├── components/        # UI组件
│   ├── common/       # 通用组件
│   ├── interview/    # 面试相关组件
│   └── dashboard/    # 仪表板组件
├── pages/            # 页面组件
├── services/         # API服务
├── store/            # 状态管理
├── hooks/            # 自定义钩子
├── types/            # 类型定义
└── utils/            # 工具函数
```

## 开发环境设置

### 前置要求
- Node.js >= 18.0.0
- Python >= 3.9
- Git

### 后端设置

1. **创建虚拟环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **环境变量配置**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

4. **数据库初始化**
```bash
python -m src.db.init_db
```

5. **启动开发服务器**
```bash
uvicorn src.main:app --reload --port 9999
```

### 前端设置

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **环境变量配置**
```bash
cp .env.local.example .env.local
# 编辑 .env.local 文件
```

3. **启动开发服务器**
```bash
npm run dev
```

### 同时启动前后端
```bash
# 在项目根目录
npm run dev
```

## 开发指南

### 代码规范

#### Python代码规范
- 遵循 PEP 8 标准
- 使用类型注解
- 函数和类必须有文档字符串
- 使用 Black 格式化代码
- 使用 isort 排序导入

```python
def create_interview_service(
    interview_data: InterviewCreate,
    resume: Optional[UploadFile] = None,
    db: Session = None
) -> InterviewResponse:
    """
    创建新的面试会话
    
    Args:
        interview_data: 面试创建数据
        resume: 简历文件（可选）
        db: 数据库会话
        
    Returns:
        InterviewResponse: 创建的面试会话数据
        
    Raises:
        ValidationError: 数据验证失败
        DatabaseError: 数据库操作失败
    """
    pass
```

#### TypeScript代码规范
- 使用严格的TypeScript配置
- 所有组件必须有类型定义
- 使用函数式组件和Hooks
- 遵循React最佳实践

```typescript
interface InterviewProps {
  interviewId: number;
  onComplete: (feedback: FeedbackData) => void;
}

const Interview: React.FC<InterviewProps> = ({ 
  interviewId, 
  onComplete 
}) => {
  // 组件实现
};
```

### 错误处理

#### 后端错误处理
1. **使用自定义异常**
```python
from src.utils.exceptions import InterviewNotFoundError

if not interview:
    raise InterviewNotFoundError(interview_id)
```

2. **服务层错误处理**
```python
try:
    result = await some_operation()
    return result
except DatabaseError as e:
    logger.error(f"数据库操作失败: {e}")
    raise
except Exception as e:
    logger.error(f"未知错误: {e}")
    raise InterviewGPTException("操作失败")
```

#### 前端错误处理
1. **API调用错误处理**
```typescript
try {
  const response = await api.createInterview(data);
  return response.data;
} catch (error) {
  if (error.response?.status === 404) {
    throw new Error('面试会话未找到');
  }
  throw new Error('创建面试失败');
}
```

2. **组件错误边界**
```typescript
class ErrorBoundary extends React.Component {
  // 错误边界实现
}
```

### 测试策略

#### 测试类型
1. **单元测试**: 测试单个函数或组件
2. **集成测试**: 测试模块间的交互
3. **端到端测试**: 测试完整的用户流程

#### 后端测试
```python
# 单元测试示例
@pytest.mark.asyncio
async def test_create_interview_service_success(db_session, sample_data):
    """测试成功创建面试服务"""
    result = await create_interview_service(sample_data, db=db_session)
    assert result.position == sample_data["position"]
```

#### 前端测试
```typescript
// 组件测试示例
import { render, screen } from '@testing-library/react';
import Interview from './Interview';

test('renders interview component', () => {
  render(<Interview interviewId={1} onComplete={jest.fn()} />);
  expect(screen.getByText('面试开始')).toBeInTheDocument();
});
```

### 数据库管理

#### 模型定义
```python
class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    position = Column(String(100), index=True)
    difficulty = Column(String(20))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 迁移管理
```bash
# 创建迁移
alembic revision --autogenerate -m "Add new table"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### API设计原则

#### RESTful设计
- 使用标准HTTP方法 (GET, POST, PUT, DELETE)
- 资源导向的URL设计
- 统一的响应格式
- 适当的HTTP状态码

#### 响应格式标准化
```json
{
  "success": true,
  "data": { /* 响应数据 */ },
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 性能优化

#### 后端优化
1. **数据库查询优化**
   - 使用索引
   - 避免N+1查询
   - 使用连接查询代替多次查询

2. **缓存策略**
   - Redis缓存热点数据
   - 面试官实例缓存
   - API响应缓存

3. **异步处理**
   - 使用async/await
   - 后台任务队列
   - 非阻塞I/O操作

#### 前端优化
1. **代码分割**
   - 路由级别的代码分割
   - 组件懒加载
   - 第三方库按需加载

2. **状态管理优化**
   - 避免不必要的重渲染
   - 使用useMemo和useCallback
   - 合理的状态结构设计

### 安全考虑

#### 后端安全
1. **输入验证**
   - 使用Pydantic验证所有输入
   - SQL注入防护
   - XSS防护

2. **认证授权**
   - JWT令牌认证
   - 角色基础访问控制
   - API限流

#### 前端安全
1. **数据验证**
   - 客户端输入验证
   - 敏感数据加密存储
   - HTTPS通信

## 部署指南

### 开发环境部署
```bash
# 使用Docker Compose
docker-compose up -d
```

### 生产环境部署

#### 后端部署 (Railway)
1. 连接GitHub仓库
2. 配置环境变量
3. 自动部署

#### 前端部署 (Vercel)
1. 连接GitHub仓库
2. 配置构建命令
3. 自动部署

### 环境变量管理
```bash
# 开发环境
DEBUG=true
DATABASE_URL=sqlite:///./dev.db

# 生产环境
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 最佳实践

### 代码组织
1. **单一职责原则**: 每个模块只负责一个功能
2. **依赖注入**: 使用依赖注入提高可测试性
3. **接口隔离**: 定义清晰的接口边界

### 错误处理
1. **分层错误处理**: 在不同层级处理不同类型的错误
2. **错误日志**: 记录详细的错误信息用于调试
3. **用户友好**: 向用户显示友好的错误消息

### 性能监控
1. **日志记录**: 记录关键操作的性能指标
2. **错误监控**: 实时监控系统错误
3. **用户行为分析**: 分析用户使用模式

### 文档维护
1. **代码注释**: 保持代码注释的及时更新
2. **API文档**: 使用OpenAPI自动生成文档
3. **变更日志**: 记录重要的变更和版本信息

## 故障排除

### 常见问题

#### 后端问题
1. **数据库连接失败**
   - 检查数据库URL配置
   - 确认数据库服务运行状态

2. **AI服务调用失败**
   - 检查API密钥配置
   - 确认网络连接

#### 前端问题
1. **API调用失败**
   - 检查后端服务状态
   - 确认API端点配置

2. **构建失败**
   - 检查依赖版本兼容性
   - 清理node_modules重新安装

### 调试技巧
1. **使用调试器**: 设置断点调试代码
2. **日志分析**: 查看详细的日志信息
3. **网络监控**: 使用浏览器开发者工具监控网络请求

## 贡献指南

### 提交代码
1. Fork项目仓库
2. 创建功能分支
3. 编写测试用例
4. 提交Pull Request

### 代码审查
1. 检查代码质量
2. 运行测试用例
3. 验证功能完整性
4. 确认文档更新

### 发布流程
1. 更新版本号
2. 生成变更日志
3. 创建发布标签
4. 部署到生产环境 