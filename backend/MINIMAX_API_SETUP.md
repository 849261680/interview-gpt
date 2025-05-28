# MiniMax API 配置说明

## 重要提醒

本项目已移除所有模拟实现，现在使用真实的 MiniMax API 进行语音识别和语音合成。

## 配置步骤

### 1. 获取 MiniMax API 密钥

根据你的地区选择对应的平台：

#### 全球版 (Global)
- 访问：https://www.minimax.io/platform/user-center/basic-information/interface-key
- API主机：`https://api.minimaxi.chat` (注意有额外的 "i")

#### 中国大陆版 (Mainland)  
- 访问：https://platform.minimaxi.com/user-center/basic-information/interface-key
- API主机：`https://api.minimax.chat`

### 2. 配置环境变量

在 `backend/.env` 文件中设置以下变量：

```bash
# MiniMax API 配置
MINIMAX_API_KEY=your_real_minimax_api_key_here
MINIMAX_GROUP_ID=your_real_minimax_group_id_here
MINIMAX_API_HOST=https://api.minimax.chat
```

**重要：** API密钥和主机必须匹配你的地区，否则会出现 "Invalid API key" 错误。

### 3. 支持的功能

- ✅ **语音识别 (ASR)**: 将音频转换为文字
- ✅ **语音合成 (TTS)**: 将文字转换为语音
- ✅ **多种语音**: 支持多种预设语音角色
- ✅ **实时处理**: 支持实时语音交互

### 4. API 端点

- **语音识别**: `/v1/speech_to_text`
- **语音合成**: `/v1/t2a_v2`

### 5. 错误排查

#### "Invalid API key" 错误
- 检查 API 密钥是否正确
- 确认 API 主机与你的地区匹配
- 验证 Group ID 是否正确

#### "API密钥未配置" 错误
- 确保在 `.env` 文件中设置了 `MINIMAX_API_KEY` 和 `MINIMAX_GROUP_ID`
- 重启后端服务以加载新的环境变量

### 6. 测试配置

启动后端服务后，可以通过以下端点测试：

```bash
# 测试语音服务健康状态
curl http://localhost:8000/api/real-mcp-speech/health

# 测试语音合成
curl -X POST http://localhost:8000/api/real-mcp-speech/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{"text":"你好，这是一个测试","interviewer_type":"system"}'
```

### 7. 费用说明

使用 MiniMax API 可能会产生费用，请查看官方定价页面了解详情。

## 技术实现

- 使用真实的 MiniMax REST API
- 支持多种音频格式 (WAV, MP3)
- 异步处理，提高性能
- 完整的错误处理和日志记录 