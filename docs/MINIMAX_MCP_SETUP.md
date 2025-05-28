# MiniMax MCP 实时AI语音面试设置指南

## 🚀 功能概述

本项目已集成MiniMax MCP技术栈，实现了完整的实时AI语音面试功能：

- **🎤 语音识别 (ASR)**: 使用MiniMax语音识别API，支持高精度中文识别
- **🔊 语音合成 (TTS)**: 使用MiniMax语音合成API，支持多种音色
- **🤖 智能对话**: 使用MiniMax Chat API，支持流式响应
- **⚡ 实时交互**: 基于MCP协议的实时通信

## 📋 环境配置

### 1. 获取MiniMax API密钥

1. 访问 [MiniMax开放平台](https://api.minimax.chat)
2. 注册账号并完成实名认证
3. 创建应用获取以下信息：
   - `API Key`: 用于API调用认证
   - `Group ID`: 用于标识应用组

### 2. 配置环境变量

在 `frontend/` 目录下创建 `.env.local` 文件：

```bash
# MiniMax MCP 配置
NEXT_PUBLIC_MINIMAX_API_KEY=your_minimax_api_key_here
NEXT_PUBLIC_MINIMAX_GROUP_ID=your_minimax_group_id_here
NEXT_PUBLIC_MINIMAX_BASE_URL=https://api.minimax.chat

# 其他配置
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. 安装依赖

```bash
cd frontend
npm install
```

## 🛠️ 技术架构

### 核心服务模块

```typescript
// MiniMax MCP 服务
class MinimaxMCPService {
  // 语音识别
  async speechToText(audioBlob: Blob): Promise<ASRResult>
  
  // 语音合成
  async textToSpeech(text: string): Promise<TTSResult>
  
  // 智能对话
  async chat(messages: ChatMessage[]): Promise<ChatResponse>
  
  // 流式对话
  async streamChat(messages: ChatMessage[]): AsyncGenerator<string>
}
```

### 配置管理

```typescript
// 面试官语音配置
const interviewerVoiceMapping = {
  technical: 'male-qingsong',    // 技术面试官 - 清爽男声
  hr: 'female-zhiyu',           // HR面试官 - 知性女声
  product: 'male-chunhou',      // 产品经理 - 醇厚男声
  final: 'male-chunhou'         // 总面试官 - 醇厚男声
}

// 面试场景提示词
const interviewPrompts = {
  technical: {
    systemPrompt: "你是一位资深的技术面试官...",
    welcomeMessage: "你好！我是李工，负责今天的技术面试。"
  }
  // ... 其他面试官配置
}
```

## 🎯 功能特性

### 1. 语音识别功能
- ✅ 高精度中文语音识别
- ✅ 实时音量检测和可视化
- ✅ 录音时长显示
- ✅ 识别置信度显示
- ✅ 错误处理和降级方案

### 2. 语音合成功能
- ✅ 多种音色支持（甜美女声、清爽男声等）
- ✅ 面试官角色语音匹配
- ✅ 语音参数调节（语速、音调、音量）
- ✅ 播放状态控制

### 3. 智能对话功能
- ✅ 基于MiniMax Chat API
- ✅ 流式响应显示
- ✅ 上下文记忆管理
- ✅ 面试场景专业提示词
- ✅ 多轮对话支持

### 4. 用户界面
- ✅ 现代化设计风格
- ✅ 实时状态指示器
- ✅ MCP连接状态显示
- ✅ 流式打字效果
- ✅ 响应式布局

## 🚀 使用指南

### 1. 启动服务

```bash
# 启动前端服务
cd frontend
npm run dev

# 启动后端服务（另一个终端）
cd backend
python main.py
```

### 2. 开始面试

1. 访问：`http://localhost:3011/interview/3274`
2. 检查MCP连接状态（右上角绿色指示器）
3. 点击"开始AI面试"按钮
4. 授权麦克风权限

### 3. 语音交互

**录音回答：**
- 点击 🎤 按钮开始录音
- 说出你的回答
- 再次点击 ⏹️ 停止录音
- 系统自动识别并获取AI回复

**文字回答：**
- 在输入框中输入回答
- 按 Enter 发送或点击"发送"按钮

**语音播放：**
- AI回复会自动语音播放
- 可点击消息旁的 🔊 按钮重播
- 播放时可点击"停止"按钮中断

## 🔧 配置选项

### 语音识别配置

```typescript
const asrConfig = {
  language: 'zh-CN',           // 识别语言
  sampleRate: 16000,           // 采样率
  format: 'wav',               // 音频格式
  enablePunctuation: true,     // 启用标点符号
  enableWordTimestamp: false   // 词级时间戳
}
```

### 语音合成配置

```typescript
const ttsConfig = {
  speed: 1.0,                  // 语速
  volume: 1.0,                 // 音量
  pitch: 1.0,                  // 音调
  audioFormat: 'mp3'           // 音频格式
}
```

### 对话配置

```typescript
const chatConfig = {
  temperature: 0.7,            // 创造性
  maxTokens: 2000,             // 最大令牌数
  topP: 0.9,                   // 核采样
  stream: true                 // 流式响应
}
```

## 🌐 API端点

### MiniMax API 端点

```
# 语音识别
POST https://api.minimax.chat/v1/speech_to_text

# 语音合成
POST https://api.minimax.chat/v1/text_to_speech

# 智能对话
POST https://api.minimax.chat/v1/text/chatcompletion_v2
```

### 请求示例

```javascript
// 语音识别
const formData = new FormData();
formData.append('file', audioBlob, 'audio.wav');
formData.append('language', 'zh-CN');

const response = await fetch('/v1/speech_to_text', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'X-Group-Id': groupId
  },
  body: formData
});

// 智能对话
const response = await fetch('/v1/text/chatcompletion_v2', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'X-Group-Id': groupId,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'abab6.5s-chat',
    messages: [
      { role: 'system', content: '你是一位面试官...' },
      { role: 'user', content: '用户的回答' }
    ],
    stream: true
  })
});
```

## 🔒 安全与隐私

### 数据处理
- 🔐 API密钥安全存储在环境变量中
- 🚫 录音数据仅在识别时传输，不永久存储
- 🛡️ 所有API调用使用HTTPS加密
- 🔒 对话历史仅在会话期间保留

### 权限管理
- 🎤 明确的麦克风权限请求
- 🔊 语音播放无需特殊权限
- ⚙️ 用户可随时关闭语音功能
- 🔄 连接状态实时显示

## 🐛 故障排除

### 常见问题

**Q: MCP连接失败怎么办？**
A: 检查API密钥和Group ID是否正确配置，确保网络连接正常

**Q: 语音识别不准确？**
A: 确保环境安静，说话清晰，检查麦克风权限

**Q: 语音合成没有声音？**
A: 检查系统音量设置，确保浏览器未被静音

**Q: 流式响应中断？**
A: 检查网络连接，可能是API调用超时

### 错误代码

- `MCP_001`: API密钥无效
- `MCP_002`: Group ID错误
- `ASR_001`: 语音识别失败
- `TTS_001`: 语音合成失败
- `CHAT_001`: 对话API调用失败

## 📊 性能优化

### 建议配置
- 使用高质量麦克风获得更好的识别效果
- 确保稳定的网络连接以支持流式响应
- 适当调整语音参数以获得最佳体验

### 监控指标
- MCP连接状态
- API调用延迟
- 语音识别准确率
- 用户交互响应时间

## 🔮 未来规划

### 短期计划
- 🌍 多语言语音识别支持
- 🎭 更多语音角色选择
- 📊 语音质量评估
- 🔄 实时语音转文字

### 长期目标
- 🤖 AI语音情感分析
- 📈 面试表现评分
- 🎯 个性化面试训练
- 🔗 更多AI服务集成

---

**注意**: 使用MiniMax MCP功能需要有效的API密钥。如果未配置或配置错误，系统将自动降级到模拟模式，部分功能可能受限。

**技术支持**: 如有问题请查看控制台日志或联系开发团队。 