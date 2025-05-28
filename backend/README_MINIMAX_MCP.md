# MiniMax MCP 实时语音面试集成

## 项目概述

本项目成功集成了 MiniMax MCP (Model Context Protocol) 工具，为 Interview-GPT 项目提供了完整的实时语音面试功能。支持多个 AI 面试官轮流提问，每个面试官都有独特的声音特色。

## 功能特性

### ✅ 已实现功能

1. **多AI面试官语音系统**
   - 技术面试官：male-qn-jingying（精英青年音色）
   - HR面试官：female-yujie（御姐音色）
   - 行为面试官：male-qn-qingse（青涩青年音色）
   - 产品面试官：female-chengshu（成熟女性音色）
   - 总面试官：presenter_male（男性主持人）
   - 系统提示：female-tianmei（甜美女性音色）

2. **实时语音处理**
   - 文字转语音（TTS）- 使用 MiniMax MCP
   - 语音转文字（ASR）- 支持 MiniMax MCP
   - 异步处理，支持并发请求
   - 错误处理和备用方案

3. **完整的服务架构**
   - 模块化设计，易于扩展
   - 统一的API接口
   - 完善的日志记录
   - 配置管理和环境变量支持

## 项目结构

```
backend/
├── src/services/speech/
│   ├── speech_service.py              # 主要语音服务
│   ├── realtime_speech_service.py     # 实时语音处理
│   ├── minimax_mcp_service.py         # MiniMax MCP 服务封装
│   ├── minimax_mcp_integration.py     # 完整集成方案
│   └── real_minimax_service.py        # 真实MCP调用实现
├── demo_minimax_interview.py          # 面试演示脚本
├── test_real_minimax_mcp.py          # MCP测试脚本
├── demo_real_mcp_calls.py            # 真实调用演示
└── static/audio/                      # 音频文件存储
    ├── interview/                     # 面试音频
    ├── demo/                         # 演示音频
    └── mcp_demo/                     # MCP演示音频
```

## 核心服务说明

### 1. SpeechService (speech_service.py)
主要的语音服务类，提供统一的语音处理接口。

**主要功能：**
- 文字转语音（支持多种面试官声音）
- 语音转文字
- 批量语音生成
- 音频文件管理

**使用示例：**
```python
from src.services.speech.speech_service import SpeechService

speech_service = SpeechService()

# 生成技术面试官语音
result = await speech_service.text_to_speech(
    text="请介绍一下你的技术背景",
    interviewer_type="technical"
)
```

### 2. MinimaxMCPIntegration (minimax_mcp_integration.py)
完整的 MiniMax MCP 集成服务，提供高级功能。

**主要功能：**
- 真实的 MiniMax MCP 工具调用
- 智能备用方案
- 批量处理
- 连接测试和状态监控

**使用示例：**
```python
from src.services.speech.minimax_mcp_integration import MinimaxMCPIntegration

mcp_service = MinimaxMCPIntegration()

# 生成面试语音
result = await mcp_service.generate_interview_speech(
    text="你好，欢迎参加面试",
    interviewer_type="system"
)
```

### 3. RealMinimaxService (real_minimax_service.py)
专门处理真实 MiniMax MCP 调用的服务。

**主要功能：**
- 直接调用 MiniMax MCP 工具
- 优化的参数配置
- 详细的错误处理

## 面试官语音配置

| 面试官类型 | 语音ID | 音色名称 | 特点 | 使用场景 |
|-----------|--------|----------|------|----------|
| technical | male-qn-jingying | 精英青年音色 | 专业、严谨 | 技术问题、编程能力 |
| hr | female-yujie | 御姐音色 | 温和、专业 | 职业规划、团队适配 |
| behavioral | male-qn-qingse | 青涩青年音色 | 亲和、耐心 | 行为问题、软技能 |
| product | female-chengshu | 成熟女性音色 | 成熟、理性 | 产品思维、用户理解 |
| final | presenter_male | 男性主持人 | 权威、总结性 | 面试总结、最终评价 |
| system | female-tianmei | 甜美女性音色 | 友好、引导性 | 系统提示、欢迎语 |

## 环境配置

### 环境变量
```bash
# MiniMax API Key（可选，未设置时使用模拟模式）
export MINIMAX_API_KEY=your_api_key_here

# 音频文件存储路径（可选）
export AUDIO_STORAGE_PATH=/path/to/audio/storage
```

### 依赖安装
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 或者安装特定依赖
pip install asyncio aiofiles pathlib
```

## 使用方法

### 1. 运行演示脚本

**基础演示：**
```bash
python demo_minimax_interview.py
```

**真实MCP调用演示：**
```bash
python demo_real_mcp_calls.py
```

**完整测试：**
```bash
python test_real_minimax_mcp.py
```

### 2. 在代码中使用

**简单使用：**
```python
import asyncio
from src.services.speech.speech_service import SpeechService

async def main():
    speech_service = SpeechService()
    
    # 生成语音
    result = await speech_service.text_to_speech(
        text="你好，欢迎参加面试",
        interviewer_type="system"
    )
    
    print(f"语音文件: {result}")

asyncio.run(main())
```

**高级使用：**
```python
import asyncio
from src.services.speech.minimax_mcp_integration import MinimaxMCPIntegration

async def main():
    mcp_service = MinimaxMCPIntegration()
    
    # 批量生成语音
    speech_data = [
        {"text": "技术面试开始", "interviewer_type": "technical"},
        {"text": "HR面试开始", "interviewer_type": "hr"}
    ]
    
    results = await mcp_service.batch_generate_interview_speeches(speech_data)
    
    for result in results:
        if result.get("success"):
            print(f"✓ 生成成功: {result['file_path']}")
        else:
            print(f"✗ 生成失败: {result.get('error')}")

asyncio.run(main())
```

## 测试结果

### 演示脚本测试结果
```
🎉 MiniMax MCP 真实调用演示成功完成！
成功率: 6/6
生成文件: 6 个

📁 生成的文件位置:
   /Users/psx849261680/Desktop/Interview-GPT/backend/static/audio/mcp_demo
```

### 真实MCP工具测试
- ✅ 技术面试官语音生成成功
- ✅ HR面试官语音生成成功  
- ✅ 行为面试官语音生成成功
- ✅ 产品面试官语音生成成功
- ✅ 总面试官语音生成成功
- ✅ 系统提示语音生成成功

### 功能验证
- ✅ MiniMax MCP 工具可用性确认
- ✅ 获取了完整的可用语音列表
- ✅ 成功生成了多个面试官的语音样本
- ✅ 建立了完整的面试官语音映射体系
- ✅ 实现了异步处理和错误处理
- ✅ 支持批量语音生成

## API 接口

### 语音生成接口
```python
async def text_to_speech(text: str, interviewer_type: str = "system") -> str:
    """
    文字转语音
    
    Args:
        text: 要转换的文字
        interviewer_type: 面试官类型
        
    Returns:
        音频文件路径
    """
```

### 语音识别接口
```python
async def speech_to_text(audio_file_path: str) -> str:
    """
    语音转文字
    
    Args:
        audio_file_path: 音频文件路径
        
    Returns:
        识别的文字
    """
```

### 批量处理接口
```python
async def batch_generate_interview_speeches(speech_data: list) -> list:
    """
    批量生成面试语音
    
    Args:
        speech_data: 语音数据列表
        
    Returns:
        生成结果列表
    """
```

## 性能优化

1. **异步处理**：所有语音操作都使用异步处理，提高并发性能
2. **缓存机制**：支持音频文件缓存，避免重复生成
3. **错误恢复**：智能备用方案，确保服务稳定性
4. **资源管理**：自动清理临时文件，优化存储空间

## 扩展功能

### 支持的音频格式
- MP3（默认）
- WAV
- M4A
- OGG

### 支持的语音参数
- 语速调节（0.5-2.0）
- 情感控制（happy, sad, neutral等）
- 音量控制（0-10）
- 音调调节（-12到12）

### 多语言支持
- 中文（默认）
- 英文
- 日文
- 韩文
- 其他语言（根据MiniMax支持情况）

## 故障排除

### 常见问题

1. **API Key 未配置**
   ```
   解决方案：设置 MINIMAX_API_KEY 环境变量
   export MINIMAX_API_KEY=your_api_key_here
   ```

2. **音频文件生成失败**
   ```
   检查：
   - 网络连接是否正常
   - API Key 是否有效
   - 输出目录是否有写权限
   ```

3. **语音质量问题**
   ```
   调整参数：
   - 降低语速（speed=0.8）
   - 调整情感（emotion="neutral"）
   - 选择合适的语音ID
   ```

### 日志查看
```bash
# 查看详细日志
python demo_minimax_interview.py 2>&1 | tee minimax.log

# 过滤错误日志
grep "ERROR" minimax.log
```

## 未来规划

### 短期目标
- [ ] 添加实时语音流处理
- [ ] 支持语音情感分析
- [ ] 优化语音生成速度
- [ ] 添加语音质量评估

### 长期目标
- [ ] 支持多轮对话上下文
- [ ] 集成语音克隆功能
- [ ] 添加语音风格迁移
- [ ] 支持实时语音对话

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目使用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目 Issues
- 邮件联系
- 技术讨论群

---

**最后更新：** 2025-05-26
**版本：** v1.0.0
**状态：** ✅ 生产就绪 