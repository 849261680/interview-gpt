# MiniMax MCP 集成文档

## 概述

本文档介绍了Interview-GPT项目中MiniMax MCP（Model Context Protocol）的集成实现，包括文字转语音(TTS)、语音识别(ASR)和AI对话功能。

## 功能特性

### ✅ 已实现功能

1. **文字转语音 (TTS)**
   - 支持多种中文语音（甜美女性、少女、御姐、成熟女性等）
   - 支持多种男性语音（青涩青年、精英青年、霸道青年等）
   - 支持多语言语音（英语、日语、韩语、西班牙语等）
   - 可调节语速、音量、音调等参数
   - 返回高质量MP3音频文件URL

2. **语音列表获取**
   - 获取所有可用的系统语音
   - 支持语音克隆功能（需要额外配置）

3. **API集成**
   - 完整的后端API实现
   - 前端服务类封装
   - 错误处理和重试机制

### 🚧 待实现功能

1. **语音识别 (ASR)**
   - 实时语音转文字
   - 支持多语言识别
   - 时间戳和置信度信息

2. **AI对话集成**
   - 与DeepSeek等AI服务结合
   - 流式对话响应
   - 上下文管理

## 技术架构

### 后端架构

```
backend/
├── src/
│   ├── api/
│   │   └── minimax_tts.py          # MiniMax TTS API端点
│   ├── services/
│   │   ├── audio_service.py        # 音频服务（集成多种TTS）
│   │   └── minimax_mcp_service.py  # MiniMax MCP服务封装
│   └── ...
├── mcp_tools.py                    # MCP工具包装函数
└── test_minimax_mcp_integration.py # 集成测试脚本
```

### 前端架构

```
frontend/
├── src/
│   ├── services/
│   │   └── MinimaxMCPService.ts    # 前端MiniMax服务
│   ├── pages/
│   │   └── test-minimax-tts.tsx    # TTS测试页面
│   └── ...
```

## API 接口

### 1. 文字转语音

**端点**: `POST /api/api/minimax-tts/synthesize`

**请求体**:
```json
{
  "text": "要转换的文本",
  "voice_id": "female-tianmei",
  "service": "minimax",
  "model": "speech-02-hd",
  "speed": 1.0,
  "vol": 1.0,
  "pitch": 0,
  "emotion": "happy",
  "sample_rate": 32000,
  "bitrate": 128000,
  "channel": 1,
  "format": "mp3",
  "language_boost": "auto"
}
```

**响应**:
```json
{
  "success": true,
  "message": "MiniMax语音合成成功",
  "audio_url": "https://minimax-algeng-chat-tts.oss-cn-wulanchabu.aliyuncs.com/audio%2Ftts-mp3-20250529165458-mINSBpqq.mp3?Expires=86401748508898&OSSAccessKeyId=LTAI5tGLnRTkBjLuYPjNcKQ8&Signature=7im%2F%2BWQ9CSlo7hZbxWUDpD%2FSxCE%3D",
  "audio_path": null,
  "voice_used": "female-tianmei",
  "service": "minimax",
  "error": null
}
```

### 2. 获取语音列表

**端点**: `GET /api/api/minimax-tts/voices?service=minimax`

**响应**:
```json
{
  "success": true,
  "message": "获取MiniMax语音列表成功",
  "voices": "Success. System Voices: ['Name: 甜美女性音色, ID: female-tianmei', ...]",
  "service": "minimax",
  "error": null
}
```

### 3. 服务状态检查

**端点**: `GET /api/api/minimax-tts/status`

**响应**:
```json
{
  "minimax": {
    "available": true,
    "api_key_configured": true,
    "mcp_tools_available": true
  },
  "openai": {
    "available": true,
    "api_key_configured": true
  }
}
```

## 环境配置

### 1. 环境变量

在 `backend/.env` 文件中配置：

```bash
# MiniMax API配置
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_API_HOST=https://api.minimax.chat
MINIMAX_GROUP_ID=your_minimax_group_id_here
MINIMAX_MCP_BASE_PATH=~/Desktop
MINIMAX_API_RESOURCE_MODE=url
```

### 2. 依赖安装

确保已安装MiniMax MCP包：

```bash
pip install minimax-mcp
```

## 使用示例

### 后端使用

```python
from src.services.audio_service import audio_service

# 文字转语音
result = await audio_service.text_to_speech(
    text="你好，欢迎使用AI面试系统！",
    voice_id="female-tianmei",
    service="minimax"
)

if result["success"]:
    audio_url = result["audio_url"]
    print(f"音频URL: {audio_url}")
```

### 前端使用

```typescript
import { MinimaxMCPService } from '../services/MinimaxMCPService';

// 创建服务实例
const minimaxService = new MinimaxMCPService({
  apiKey: 'your-api-key',
  groupId: 'your-group-id'
});

// 文字转语音
const ttsResult = await minimaxService.textToSpeech(
  "你好，欢迎使用AI面试系统！",
  "female-tianmei",
  {
    speed: 1.0,
    volume: 1.0,
    pitch: 0,
    audioFormat: 'mp3'
  }
);

// 播放音频
const audio = new Audio(ttsResult.audioUrl);
audio.play();
```

## 可用语音列表

### 中文语音

#### 女性语音
- `female-tianmei` - 甜美女性音色
- `female-shaonv` - 少女音色
- `female-yujie` - 御姐音色
- `female-chengshu` - 成熟女性音色

#### 男性语音
- `male-qn-qingse` - 青涩青年音色
- `male-qn-jingying` - 精英青年音色
- `male-qn-badao` - 霸道青年音色
- `male-qn-daxuesheng` - 青年大学生音色

#### 专业语音
- `presenter_male` - 男性主持人
- `presenter_female` - 女性主持人
- `audiobook_male_1` - 男性有声书1
- `audiobook_female_1` - 女性有声书1

### 多语言语音

#### 英语
- `English_Trustworthy_Man` - 可信赖的男性
- `English_Graceful_Lady` - 优雅女士
- `English_Aussie_Bloke` - 澳洲男性

#### 日语
- `Japanese_IntellectualSenior` - 知性前辈
- `Japanese_DecisivePrincess` - 果断公主
- `Japanese_GentleButler` - 温柔管家

#### 韩语
- `Korean_SweetGirl` - 甜美女孩
- `Korean_CheerfulBoyfriend` - 开朗男友
- `Korean_ElegantPrincess` - 优雅公主

## 测试

### 1. 运行集成测试

```bash
cd backend
python test_minimax_mcp_integration.py
```

### 2. 使用测试页面

访问前端测试页面：`http://localhost:3000/test-minimax-tts`

### 3. 直接API测试

```bash
# 测试TTS
curl -X POST "http://localhost:8000/api/api/minimax-tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是测试",
    "voice_id": "female-tianmei",
    "service": "minimax"
  }'

# 获取语音列表
curl -X GET "http://localhost:8000/api/api/minimax-tts/voices?service=minimax"

# 检查服务状态
curl -X GET "http://localhost:8000/api/api/minimax-tts/status"
```

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: login fail: Please carry the API secret key in the 'Authorization' field
   解决: 检查MINIMAX_API_KEY环境变量是否正确配置
   ```

2. **MCP工具不可用**
   ```
   错误: No module named 'mcp_tools'
   解决: 确保已安装minimax-mcp包
   ```

3. **音频播放失败**
   ```
   错误: 音频URL无法访问
   解决: 检查网络连接和音频URL有效性
   ```

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查MCP工具状态**
   ```python
   from mcp_tools import mcp_MiniMax_list_voices
   result = mcp_MiniMax_list_voices("all")
   print(result.content)
   ```

3. **验证环境变量**
   ```bash
   echo $MINIMAX_API_KEY
   echo $MINIMAX_API_HOST
   ```

## 性能优化

### 1. 音频缓存

- 实现音频文件本地缓存
- 避免重复生成相同文本的音频

### 2. 并发处理

- 使用异步处理提高响应速度
- 实现请求队列管理

### 3. 错误重试

- 实现指数退避重试机制
- 提供降级方案（浏览器TTS）

## 安全考虑

### 1. API密钥保护

- 不要在前端代码中暴露API密钥
- 使用环境变量管理敏感信息

### 2. 输入验证

- 限制文本长度和内容
- 防止恶意输入注入

### 3. 速率限制

- 实现API调用频率限制
- 监控使用量和成本

## 更新日志

### v1.0.0 (2025-05-29)

- ✅ 实现MiniMax TTS基础功能
- ✅ 添加多语音支持
- ✅ 创建前后端API集成
- ✅ 添加测试页面和文档
- ✅ 实现错误处理和状态检查

### 下一步计划

- 🔄 实现语音识别(ASR)功能
- 🔄 添加实时流式对话
- 🔄 优化音频缓存机制
- 🔄 集成到面试流程中

## 联系支持

如有问题或建议，请：

1. 查看本文档的故障排除部分
2. 检查项目的GitHub Issues
3. 联系开发团队

---

*最后更新: 2025-05-29* 