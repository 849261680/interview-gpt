# Google Cloud Speech API 配置指南

## 概述

本指南将帮助你从零开始配置Google Cloud Speech-to-Text API，为Interview-GPT项目提供高质量的语音识别功能。

## 前置条件

1. 有效的Google账户
2. 信用卡或借记卡（用于验证身份，有免费额度）
3. Python 3.9+ 环境

## 详细配置步骤

### 第一步：创建Google Cloud项目

1. **访问Google Cloud Console**
   - 打开 [Google Cloud Console](https://console.cloud.google.com/)
   - 使用你的Google账户登录

2. **创建新项目**
   - 点击顶部的项目选择器
   - 点击"新建项目"
   - 填写项目信息：
     ```
     项目名称: interview-gpt-speech
     项目ID: interview-gpt-speech-[随机数字]
     位置: 无组织
     ```
   - 点击"创建"

3. **记录项目ID**
   - 创建完成后，记录下项目ID（例如：`interview-gpt-speech-123456`）
   - 这个ID稍后会用到

### 第二步：启用计费

1. **设置计费账户**
   - 在左侧菜单中选择"结算"
   - 点击"关联结算账户"
   - 如果没有结算账户，点击"创建结算账户"
   - 填写信用卡信息（用于身份验证）

2. **了解免费额度**
   - Google Speech提供每月前60分钟免费
   - 超出部分按$0.006/15秒计费
   - 新用户还有$300免费试用额度

### 第三步：启用Speech-to-Text API

1. **进入API库**
   - 在左侧菜单中选择"APIs & Services" > "库"
   - 或直接访问：https://console.cloud.google.com/apis/library

2. **搜索并启用API**
   - 在搜索框中输入"Cloud Speech-to-Text API"
   - 点击搜索结果中的"Cloud Speech-to-Text API"
   - 点击"启用"按钮
   - 等待API启用完成（通常需要1-2分钟）

### 第四步：创建服务账户

1. **进入IAM & Admin**
   - 在左侧菜单中选择"IAM & Admin" > "服务账户"
   - 或直接访问：https://console.cloud.google.com/iam-admin/serviceaccounts

2. **创建服务账户**
   - 点击"创建服务账户"
   - 填写服务账户详情：
     ```
     服务账户名称: interview-gpt-speech
     服务账户ID: interview-gpt-speech
     服务账户描述: Speech recognition for Interview-GPT application
     ```
   - 点击"创建并继续"

3. **分配角色**
   - 在"向此服务账户授予对项目的访问权限"部分
   - 点击"选择角色"下拉菜单
   - 搜索并添加以下角色：
     ```
     - Cloud Speech Client
     -   
     ```
   - 点击"继续"

4. **完成创建**
   - "向用户授予访问此服务账户的权限"部分可以跳过
   - 点击"完成"

### 第五步：生成并下载密钥

1. **进入服务账户详情**
   - 在服务账户列表中，点击刚创建的`interview-gpt-speech`服务账户

2. **创建密钥**
   - 切换到"密钥"标签页
   - 点击"添加密钥" > "创建新密钥"
   - 选择"JSON"格式
   - 点击"创建"

3. **下载密钥文件**
   - 系统会自动下载一个JSON文件
   - 文件名类似：`interview-gpt-speech-123456-abcdef123456.json`
   - **重要**：妥善保存这个文件，不要分享给他人

### 第六步：配置环境变量

1. **移动密钥文件**
   ```bash
   # 创建凭据目录
   mkdir -p ~/.config/gcloud
   
   # 移动密钥文件到安全位置
   mv ~/Downloads/interview-gpt-speech-*.json ~/.config/gcloud/credentials.json
   ```

2. **设置环境变量**
   
   **方法1：在.env文件中配置**
   ```bash
   cd /path/to/Interview-GPT/backend
   
   # 编辑.env文件
   nano .env
   ```
   
   添加以下内容：
   ```env
   # Google Speech API配置
   GOOGLE_APPLICATION_CREDENTIALS=/Users/你的用户名/.config/gcloud/credentials.json
   GOOGLE_SPEECH_PROJECT_ID=interview-gpt-speech-123456
   GOOGLE_SPEECH_CREDENTIALS_PATH=/Users/你的用户名/.config/gcloud/credentials.json
   ```

   **方法2：在shell配置文件中设置**
   ```bash
   # 编辑shell配置文件
   nano ~/.zshrc  # 或 ~/.bashrc
   
   # 添加以下行
   export GOOGLE_APPLICATION_CREDENTIALS="/Users/你的用户名/.config/gcloud/credentials.json"
   export GOOGLE_SPEECH_PROJECT_ID="interview-gpt-speech-123456"
   
   # 重新加载配置
   source ~/.zshrc  # 或 source ~/.bashrc
   ```

### 第七步：验证配置

1. **安装Google Cloud CLI（可选）**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # 或下载安装包
   # https://cloud.google.com/sdk/docs/install
   ```

2. **测试认证**
   ```bash
   # 使用gcloud测试
   gcloud auth application-default login
   gcloud config set project interview-gpt-speech-123456
   
   # 测试Speech API
   echo "你好世界" | gcloud ml speech recognize-stream --language-code=zh-CN
   ```

3. **运行项目测试**
   ```bash
   cd /path/to/Interview-GPT/backend
   
   # 激活虚拟环境
   source ../venv311/bin/activate
   
   # 运行测试
   python test_google_speech.py
   ```

## 配置验证清单

完成配置后，请检查以下项目：

- [ ] Google Cloud项目已创建
- [ ] 计费账户已设置
- [ ] Speech-to-Text API已启用
- [ ] 服务账户已创建并分配正确角色
- [ ] JSON密钥文件已下载并保存到安全位置
- [ ] 环境变量已正确设置
- [ ] 测试脚本运行成功

## 常见问题解决

### 1. 认证错误

**错误信息**：
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**解决方案**：
- 检查`GOOGLE_APPLICATION_CREDENTIALS`环境变量是否正确设置
- 确认JSON密钥文件路径正确且文件存在
- 重新启动终端或IDE

### 2. API未启用错误

**错误信息**：
```
google.api_core.exceptions.Forbidden: 403 Cloud Speech-to-Text API has not been used
```

**解决方案**：
- 确认已在Google Cloud Console中启用Speech-to-Text API
- 等待几分钟让API完全激活
- 检查项目ID是否正确

### 3. 权限不足错误

**错误信息**：
```
google.api_core.exceptions.PermissionDenied: 403 The caller does not have permission
```

**解决方案**：
- 确认服务账户有`Cloud Speech Client`角色
- 重新生成密钥文件
- 检查项目计费状态

### 4. 配额超限错误

**错误信息**：
```
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded
```

**解决方案**：
- 检查API使用量是否超过免费额度
- 等待配额重置（通常每分钟重置）
- 考虑升级到付费计划

## 安全最佳实践

### 1. 密钥管理
- 不要将JSON密钥文件提交到版本控制系统
- 定期轮换服务账户密钥（建议每90天）
- 使用最小权限原则，只分配必要的角色

### 2. 访问控制
- 限制服务账户的使用范围
- 监控API使用情况
- 设置预算警报

### 3. 网络安全
- 考虑使用VPC和防火墙规则
- 启用审计日志
- 定期检查访问日志

## 成本优化建议

### 1. 利用免费额度
- 每月前60分钟免费
- 新用户$300试用额度
- 合理规划使用量

### 2. 音频优化
- 使用适当的采样率（16kHz推荐）
- 压缩音频文件
- 移除静音片段

### 3. 监控使用量
- 设置预算警报
- 定期检查使用报告
- 考虑使用其他服务作为备用

## 下一步

配置完成后，你可以：

1. **运行测试**：验证配置是否正确
2. **集成到项目**：Google Speech会自动作为备用服务
3. **监控使用**：在Google Cloud Console中查看使用情况
4. **优化性能**：根据实际使用情况调整配置

## 支持资源

- [Google Cloud Speech-to-Text 文档](https://cloud.google.com/speech-to-text/docs)
- [服务账户最佳实践](https://cloud.google.com/iam/docs/best-practices-for-service-accounts)
- [API 配额和限制](https://cloud.google.com/speech-to-text/quotas)
- [价格计算器](https://cloud.google.com/products/calculator)

---

**注意**：Google Cloud配置是可选的。如果不配置，Interview-GPT会自动使用其他可用的语音识别服务（如MiniMax MCP、OpenAI Whisper等）。 