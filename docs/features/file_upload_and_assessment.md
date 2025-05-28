# 文件上传和评估系统功能文档

## 概述

本文档描述了Interview-GPT项目中新增的文件上传（简历上传和解析）和评估系统（详细的面试评估和反馈生成）功能。

## 功能特性

### 1. 文件上传功能

#### 1.1 支持的文件格式
- **PDF文件**: `.pdf`
- **Word文档**: `.docx`, `.doc`
- **文本文件**: `.txt`
- **图片文件**: `.png`, `.jpg`, `.jpeg`, `.tiff` (支持OCR识别)

#### 1.2 文件验证
- 文件大小限制: 最大10MB
- 文件类型验证: 基于MIME类型和文件扩展名
- 文件内容验证: 确保文件不为空且可读

#### 1.3 简历解析功能
- **个人信息提取**: 姓名、邮箱、电话、地址
- **教育背景**: 学校、学位、毕业年份
- **工作经验**: 公司、职位、工作时间
- **技能信息**: 编程语言、框架、数据库、工具
- **项目经验**: 项目描述和技术栈
- **认证信息**: 相关证书和认证
- **语言技能**: 掌握的语言

#### 1.4 智能分析
- **质量评估**: 简历完整性和质量评分
- **内容验证**: 检查必要信息的完整性
- **改进建议**: 提供简历优化建议

### 2. 评估系统功能

#### 2.1 多维度评估
- **技术能力**: 技术知识、问题解决、代码质量、系统设计
- **HR评估**: 沟通能力、职业素养、文化匹配、职业规划
- **行为评估**: 团队合作、问题解决、沟通表达、压力处理
- **产品思维**: 产品思维、用户视角、跨职能协作、商业价值

#### 2.2 智能分析
- **对话分析**: 参与度、回复质量、互动频率
- **技能匹配**: 职位要求匹配度分析
- **表现评估**: 综合表现评分和等级
- **改进计划**: 个性化改进建议和学习资源

#### 2.3 详细反馈
- **面试总结**: 整体表现概述
- **优势分析**: 候选人的突出优点
- **改进建议**: 具体的提升方向
- **推荐决策**: 基于评分的录用建议

## API接口

### 文件上传接口

#### 上传简历
```http
POST /api/files/upload-resume
Content-Type: multipart/form-data

Parameters:
- file: 简历文件 (required)
- interview_id: 面试ID (optional)
- user_id: 用户ID (optional)
```

#### 解析简历
```http
POST /api/files/parse-resume
Content-Type: multipart/form-data

Parameters:
- file: 简历文件 (required)
- save_file: 是否保存文件 (optional, default: false)
```

#### 验证简历内容
```http
POST /api/files/validate-resume
Content-Type: multipart/form-data

Parameters:
- file: 简历文件 (required)
- position: 目标职位 (optional)
```

#### 列出上传文件
```http
GET /api/files/list

Parameters:
- interview_id: 面试ID (optional)
- user_id: 用户ID (optional)
```

#### 删除文件
```http
DELETE /api/files/delete/{file_path}
```

### 评估系统接口

#### 生成全面评估
```http
POST /api/assessment/generate/{interview_id}

Parameters:
- interview_id: 面试ID (required)
- include_resume: 是否包含简历分析 (optional, default: true)
```

#### 获取评估结果
```http
GET /api/assessment/result/{interview_id}
```

#### 获取评估摘要
```http
GET /api/assessment/summary/{interview_id}
```

#### 获取评估分析
```http
GET /api/assessment/analytics/{interview_id}
```

#### 比较评估结果
```http
POST /api/assessment/compare
Content-Type: application/json

Body:
[interview_id1, interview_id2, ...]
```

#### 生成评估报告
```http
GET /api/assessment/report/{interview_id}

Parameters:
- format: 报告格式 (optional, default: "json")
```

## 使用示例

### 1. 上传并解析简历

```python
import requests

# 上传简历文件
with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    data = {'interview_id': 1, 'user_id': 1}
    response = requests.post(
        'http://localhost:8000/api/files/upload-resume',
        files=files,
        data=data
    )

result = response.json()
print(f"上传状态: {result['data']['file_info']['upload_status']}")
print(f"解析结果: {result['data']['parsed_resume']['personal_info']}")
```

### 2. 生成面试评估

```python
import requests

# 生成全面评估
response = requests.post(
    'http://localhost:8000/api/assessment/generate/1',
    params={'include_resume': True}
)

assessment = response.json()
print(f"总体评分: {assessment['data']['overall_assessment']['overall_score']}")
print(f"推荐决策: {assessment['data']['recommendation']['decision']}")
```

### 3. 获取评估摘要

```python
import requests

# 获取评估摘要
response = requests.get('http://localhost:8000/api/assessment/summary/1')

summary = response.json()
print(f"评分等级: {summary['data']['score_level']['description']}")
print(f"主要优势: {summary['data']['key_strengths']}")
print(f"改进建议: {summary['data']['main_improvements']}")
```

## 配置说明

### 文件上传配置

```python
# 在 file_upload_service.py 中配置
class FileUploadService:
    def __init__(self):
        # 支持的文件类型
        self.supported_types = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            # ...
        }
        
        # 文件大小限制（10MB）
        self.max_file_size = 10 * 1024 * 1024
        
        # 上传目录
        self.upload_dir = Path("uploads/resumes")
```

### 评估系统配置

```python
# 在 assessment_service.py 中配置
class AssessmentService:
    def __init__(self):
        # 评估维度权重
        self.assessment_weights = {
            'technical': {
                'technical_knowledge': 0.3,
                'problem_solving': 0.25,
                'code_quality': 0.25,
                'system_design': 0.2
            },
            # ...
        }
        
        # 评分等级定义
        self.score_levels = {
            90: {'level': 'Outstanding', 'recommendation': 'Strong Hire'},
            80: {'level': 'Good', 'recommendation': 'Hire'},
            # ...
        }
```

## 数据库模型

### 面试表更新
```sql
ALTER TABLE interviews ADD COLUMN resume_path VARCHAR(500);
ALTER TABLE interviews ADD COLUMN overall_score FLOAT;
```

### 反馈表结构
```sql
-- 已存在的表结构，支持新功能
-- feedback 表存储总体反馈
-- interviewer_feedback 表存储各面试官的详细反馈
```

## 错误处理

### 文件上传错误
- `ValidationError`: 文件验证失败
- `FileProcessingError`: 文件处理失败
- `FileUploadError`: 文件上传失败

### 评估系统错误
- `ValidationError`: 数据验证失败
- `AIServiceError`: AI服务错误
- `InterviewNotFoundError`: 面试不存在

## 性能优化

### 文件处理优化
1. **异步处理**: 使用异步I/O处理文件操作
2. **分块读取**: 大文件分块处理，避免内存溢出
3. **缓存机制**: 解析结果缓存，避免重复处理
4. **文件去重**: 基于哈希值的文件去重

### 评估系统优化
1. **并行评估**: 多个面试官评估并行执行
2. **结果缓存**: 评估结果缓存，提高响应速度
3. **增量更新**: 支持增量更新评估结果
4. **批量处理**: 支持批量评估和比较

## 安全考虑

### 文件安全
1. **文件类型验证**: 严格的文件类型检查
2. **文件大小限制**: 防止大文件攻击
3. **病毒扫描**: 集成病毒扫描（可选）
4. **访问控制**: 文件访问权限控制

### 数据安全
1. **敏感信息保护**: 个人信息加密存储
2. **访问日志**: 记录文件访问日志
3. **数据清理**: 定期清理临时文件
4. **权限验证**: API访问权限验证

## 测试覆盖

### 单元测试
- 文件上传服务测试
- 简历解析器测试
- 评估系统服务测试
- API端点测试

### 集成测试
- 完整流程测试
- 错误处理测试
- 性能测试
- 安全测试

## 部署说明

### 依赖安装
```bash
# 安装新增依赖
pip install -r requirements.txt

# 安装NLP模型（可选）
python -m spacy download en_core_web_sm
```

### 目录创建
```bash
# 创建上传目录
mkdir -p uploads/resumes
chmod 755 uploads/resumes
```

### 环境变量
```bash
# 可选的OCR配置
export TESSERACT_CMD=/usr/bin/tesseract
```

## 监控和日志

### 关键指标
- 文件上传成功率
- 简历解析准确率
- 评估生成时间
- API响应时间

### 日志记录
- 文件操作日志
- 评估过程日志
- 错误和异常日志
- 性能指标日志

## 未来扩展

### 功能扩展
1. **多语言支持**: 支持多种语言的简历解析
2. **AI增强**: 集成更先进的AI模型
3. **实时评估**: 实时面试评估和反馈
4. **可视化报告**: 图表化的评估报告

### 技术优化
1. **微服务架构**: 拆分为独立的微服务
2. **分布式存储**: 使用分布式文件存储
3. **机器学习**: 基于历史数据的智能评估
 