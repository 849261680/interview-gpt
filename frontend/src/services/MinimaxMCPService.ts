/**
 * MiniMax MCP 语音面试服务
 * 集成语音识别(ASR)、语音合成(TTS)和实时AI对话
 */

export interface MinimaxConfig {
  apiKey: string;
  groupId: string;
  baseUrl?: string;
  model?: string;
}

export interface ASRConfig {
  language?: string;
  sampleRate?: number;
  format?: string;
  enablePunctuation?: boolean;
  enableWordTimestamp?: boolean;
}

export interface TTSConfig {
  voice?: string;
  speed?: number;
  volume?: number;
  pitch?: number;
  audioFormat?: string;
}

export interface ChatConfig {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  stream?: boolean;
}

export interface ASRResult {
  text: string;
  confidence: number;
  duration: number;
  segments?: Array<{
    text: string;
    start: number;
    end: number;
    confidence: number;
  }>;
}

export interface TTSResult {
  audioUrl: string;
  duration: number;
  format: string;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  content: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  finishReason?: string;
}

class MinimaxMCPService {
  private config: MinimaxConfig;
  private wsConnection: WebSocket | null = null;
  private isConnected: boolean = false;
  private messageQueue: any[] = [];
  private eventListeners: Map<string, Function[]> = new Map();

  constructor(config: MinimaxConfig) {
    // 直接使用后端API的完整URL，避免前端代理问题
    const apiBaseUrl = 'http://localhost:8000/api/speech/minimax-mcp';
    
    // 先获取用户配置，然后才强制覆盖baseUrl
    const userConfig = {...config};
    delete userConfig.baseUrl; // 删除用户可能提供的baseUrl
    
    this.config = {
      // 修改为直接使用后端API的完整URL
      baseUrl: apiBaseUrl,
      model: 'abab6.5s-chat',
      ...userConfig
    };
    
    console.log('[MiniMaxMCP] 初始化服务，直接连接后端API:', apiBaseUrl);
  }

  /**
   * 初始化MCP连接
   */
  async initialize(): Promise<void> {
    try {
      // 检查配置
      if (!this.config.apiKey || !this.config.groupId) {
        throw new Error('MiniMax API Key 和 Group ID 是必需的');
      }

      // 建立WebSocket连接用于实时通信
      await this.connectWebSocket();
      
      console.log('MiniMax MCP 服务初始化成功');
    } catch (error) {
      console.error('MiniMax MCP 初始化失败:', error);
      throw error;
    }
  }

  /**
   * 建立WebSocket连接
   */
  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // 注意：这里使用模拟的WebSocket连接
        // 实际项目中需要使用MiniMax提供的WebSocket端点
        const wsUrl = `wss://api.minimax.chat/v1/ws?token=${this.config.apiKey}&group_id=${this.config.groupId}`;
        
        // 由于MiniMax可能不提供WebSocket，我们使用HTTP轮询模拟实时效果
        this.isConnected = true;
        resolve();
        
        // 实际WebSocket连接代码（如果MiniMax支持）：
        /*
        this.wsConnection = new WebSocket(wsUrl);
        
        this.wsConnection.onopen = () => {
          this.isConnected = true;
          this.processMessageQueue();
          resolve();
        };
        
        this.wsConnection.onmessage = (event) => {
          this.handleWebSocketMessage(event);
        };
        
        this.wsConnection.onerror = (error) => {
          console.error('WebSocket连接错误:', error);
          reject(error);
        };
        
        this.wsConnection.onclose = () => {
          this.isConnected = false;
          this.reconnectWebSocket();
        };
        */
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 语音识别 - 使用MiniMax ASR
   */
  async speechToText(audioBlob: Blob, config: ASRConfig = {}): Promise<ASRResult> {
    try {
      console.log('[MiniMaxMCP] 开始处理语音识别，通过后端API代理');
      console.log(`[MiniMaxMCP] 音频大小: ${Math.round(audioBlob.size / 1024)}KB, 格式: ${audioBlob.type}`);
      
      // 将音频转换为Base64编码，通过后端API代理发送
      const base64Audio = await this.blobToBase64(audioBlob);
      console.log(`[MiniMaxMCP] Base64编码完成，长度: ${base64Audio.length}字符`);
      
      const requestBody = {
        audio_data: base64Audio,
        language: config.language || 'zh',
        sample_rate: config.sampleRate || 16000,
        format: config.format || 'wav',
        enable_punctuation: config.enablePunctuation !== false,
        enable_timestamp: config.enableWordTimestamp || false
      };

      console.log(`[MiniMaxMCP] 发送请求到后端API: ${this.config.baseUrl}/speech-to-text`);

      const response = await fetch(`${this.config.baseUrl}/speech-to-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`[MiniMaxMCP] 收到后端响应状态: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        console.error(`[MiniMaxMCP] ASR请求失败: ${response.status} ${response.statusText}`);
        throw new Error(`ASR请求失败: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log(`[MiniMaxMCP] ASR请求成功: ${JSON.stringify(result)}`);
      
      if (!result.success) {
        console.error(`[MiniMaxMCP] ASR服务返回错误: ${result.error || '未知错误'}`);
        throw new Error(result.error || 'ASR服务返回错误');
      }

      // 处理响应
      return {
        text: result.text || '',
        confidence: result.confidence || 0,
        duration: result.duration || 0,
        segments: result.segments || []
      };
    } catch (error) {
      console.error('MiniMax ASR调用失败:', error);
      throw error;
    }
  }

  /**
   * 将Blob转换为Base64字符串
   */
  private async blobToBase64(blob: Blob): Promise<string> {
    try {
      console.log(`[MiniMaxMCP] 开始将Blob转换为Base64，大小: ${blob.size}字节, 类型: ${blob.type}`);
      
      if (!blob || blob.size === 0) {
        throw new Error('无效的Blob数据: 空或大小为0');
      }
      
      return new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onloadend = () => {
          try {
            if (typeof reader.result !== 'string') {
              throw new Error('FileReader结果不是字符串');
            }
            
            console.log(`[MiniMaxMCP] FileReader加载完成，结果类型: ${typeof reader.result}`);
            
            // 检查是否包含base64前缀
            if (!reader.result.includes('base64,')) {
              throw new Error('FileReader结果不包含base64前缀');
            }
            
            const base64 = reader.result.split(',')[1];
            console.log(`[MiniMaxMCP] Base64提取完成，长度: ${base64.length}字符`);
            
            resolve(base64);
          } catch (err) {
            console.error('[MiniMaxMCP] 处理FileReader结果时出错:', err);
            reject(err);
          }
        };
        
        reader.onerror = (event) => {
          console.error('[MiniMaxMCP] FileReader错误:', reader.error);
          reject(new Error(`FileReader错误: ${reader.error?.message || '未知错误'}`));
        };
        
        // 添加超时处理
        const timeout = setTimeout(() => {
          if (reader.readyState !== FileReader.DONE) {
            console.error('[MiniMaxMCP] FileReader超时');
            reader.abort();
            reject(new Error('FileReader超时'));
          }
        }, 10000); // 10秒超时
        
        try {
          reader.readAsDataURL(blob);
          console.log('[MiniMaxMCP] 已调用readAsDataURL');
        } catch (err) {
          console.error('[MiniMaxMCP] 调用readAsDataURL时出错:', err);
          clearTimeout(timeout);
          reject(err);
        }
      });
    } catch (err) {
      console.error('[MiniMaxMCP] blobToBase64外部出错:', err);
      throw err;
    }
  }

  /**
   * 语音合成 - 使用MiniMax TTS
   */
  async textToSpeech(text: string, voice: string, config: TTSConfig = {}): Promise<TTSResult> {
    try {
      console.log(`[MiniMaxMCP] 开始调用语音合成，文本长度: ${text.length}，语音: ${voice}`);
      
      // 构建请求体 - 修正为后端期望的格式
      const requestBody = {
        text,
        interviewer_type: voice || "system"  // 将voice映射为interviewer_type
      };

      console.log(`[MiniMaxMCP] 发送请求到后端API: ${this.config.baseUrl}/text-to-speech`);

      // 直接调用后端API，使用完整URL
      const response = await fetch(`${this.config.baseUrl}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`[MiniMaxMCP] 收到后端响应状态: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        console.error(`[MiniMaxMCP] TTS请求失败: ${response.status} ${response.statusText}`);
        throw new Error(`TTS请求失败: ${response.status} ${response.statusText}`);
      }

      // 检查响应的Content-Type头来确定返回的数据类型
      const contentType = response.headers.get('Content-Type') || '';
      
      // 如果是音频文件直接返回
      if (contentType.includes('audio/')) {
        console.log(`[MiniMaxMCP] TTS请求成功: 返回了直接的音频文件`);
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        return {
          audioUrl: audioUrl,
          duration: 0, // 无法直接获取音频时长
          format: contentType.includes('mp3') ? 'mp3' : 'wav'
        };
      }
      
      // 如果是XML/SSML格式(Speech Synthesis Markup Language)
      if (contentType.includes('application/xml') || contentType.includes('text/xml') || contentType.includes('text/html')) {
        console.log(`[MiniMaxMCP] TTS请求返回了XML/SSML格式`);
        const xmlText = await response.text();
        
        // 只能处理SSML的情况下，我们需要告知用户
        console.warn(`[MiniMaxMCP] 收到SSML格式响应，但无法直接处理。后端应返回JSON或音频文件。`);
        throw new Error('TTS服务返回了不支持的XML格式数据，请联系后端开发人员修复此问题');
      }
      
      // 默认尝试解析为JSON
      try {
        const result = await response.text();
        const jsonResult = JSON.parse(result);
        console.log(`[MiniMaxMCP] TTS请求成功: ${JSON.stringify(jsonResult)}`);
        
        if (!jsonResult.success) {
          console.error(`[MiniMaxMCP] TTS服务返回错误: ${jsonResult.error || '未知错误'}`);
          throw new Error(jsonResult.error || 'TTS服务返回错误');
        }
        
        return {
          audioUrl: jsonResult.audio_url || '',
          duration: jsonResult.duration || 0,
          format: jsonResult.format || 'mp3'
        };
      } catch (jsonError) {
        console.error(`[MiniMaxMCP] 无法解析TTS响应: ${jsonError}`);
        throw new Error(`无法解析TTS响应: ${jsonError instanceof Error ? jsonError.message : '未知错误'}`);
      }
    } catch (error) {
      console.error('MiniMax TTS调用失败:', error);
      throw error;
    }
  }

  /**
   * 实时AI对话 - 使用MiniMax Chat
   */
  async chat(messages: ChatMessage[], config: ChatConfig = {}): Promise<ChatResponse> {
    try {
      const requestBody = {
        model: config.model || this.config.model,
        messages: messages.map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        temperature: config.temperature || 0.7,
        max_tokens: config.maxTokens || 2000,
        top_p: config.topP || 0.9,
        stream: config.stream || false
      };

      console.log(`[MiniMaxMCP] 发送请求到后端API代理: ${this.config.baseUrl}/chat`);
      
      const response = await fetch(`${this.config.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`AI对话请求失败: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      return {
        content: result.choices?.[0]?.message?.content || '',
        usage: {
          promptTokens: result.usage?.prompt_tokens || 0,
          completionTokens: result.usage?.completion_tokens || 0,
          totalTokens: result.usage?.total_tokens || 0
        },
        finishReason: result.choices?.[0]?.finish_reason
      };
    } catch (error) {
      console.error('MiniMax Chat调用失败:', error);
      throw error;
    }
  }

  /**
   * 流式对话 - 实时响应
   */
  async streamChat(messages: ChatMessage[], config: ChatConfig = {}): Promise<AsyncGenerator<string, void, unknown>> {
    try {
      // 创建AbortController用于取消请求
      const controller = new AbortController();
      
      const requestBody = {
        model: config.model || this.config.model,
        messages: messages.map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        temperature: config.temperature || 0.7,
        max_tokens: config.maxTokens || 2000,
        top_p: config.topP || 0.9,
        stream: true
      };

      console.log(`[MiniMaxMCP] 发送流式请求到后端API代理: ${this.config.baseUrl}/chat-stream`);
      
      // 暂时使用与chat相同的端点，后续可以添加专门的流式API端点
      const response = await fetch(`${this.config.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`流式对话请求失败: ${response.status} ${response.statusText}`);
      }

      return this.parseStreamResponse(response);
    } catch (error) {
      console.error('MiniMax Stream Chat调用失败:', error);
      throw new Error(`MiniMax Stream Chat调用失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 解析流式响应
   */
  private async* parseStreamResponse(response: Response): AsyncGenerator<string, void, unknown> {
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('无法读取响应流');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              return;
            }
            
            try {
              const parsed = JSON.parse(data);
              const content = parsed.choices?.[0]?.delta?.content;
              
              if (content) {
                yield content;
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * 模拟流式响应
   */
  private async* mockStreamResponse(): AsyncGenerator<string, void, unknown> {
    const response = "很好的回答！让我们深入探讨一下这个问题。在实际工作中，你会如何处理类似的挑战？";
    const words = response.split('');
    
    for (const word of words) {
      yield word;
      await new Promise(resolve => setTimeout(resolve, 50)); // 模拟打字效果
    }
  }

  /**
   * 播放TTS音频
   */
  async playTTSAudio(audioUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);
      
      audio.onended = () => resolve();
      audio.onerror = (error) => reject(error);
      
      audio.play().catch(reject);
    });
  }

  /**
   * 停止音频播放
   */
  stopAudio(): void {
    // 停止所有正在播放的音频
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });
  }

  /**
   * 添加事件监听器
   */
  addEventListener(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  /**
   * 移除事件监听器
   */
  removeEventListener(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * 触发事件
   */
  private emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
  }

  /**
   * 获取连接状态
   */
  isConnectedToMCP(): boolean {
    return this.isConnected;
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.wsConnection) {
      this.wsConnection.close();
    }
    this.isConnected = false;
    this.messageQueue = [];
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig: Partial<MinimaxConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }
}

// 创建全局实例 - 只在客户端创建
let minimaxServiceInstance: MinimaxMCPService | null = null;

export const createMinimaxService = (config: MinimaxConfig): MinimaxMCPService => {
  if (typeof window === 'undefined') {
    return null as any;
  }
  
  minimaxServiceInstance = new MinimaxMCPService(config);
  return minimaxServiceInstance;
};

export const getMinimaxService = (): MinimaxMCPService | null => {
  return minimaxServiceInstance;
};

export default MinimaxMCPService;
