/**
 * 真实 MiniMax MCP 语音服务
 * 调用后端的真实 MCP API 端点
 */

export interface RealMCPConfig {
  baseUrl: string;
}

export interface RealMCPASRResult {
  text: string;
  confidence: number;
  method: string;
  success: boolean;
}

export interface RealMCPTTSResult {
  audio_url: string;
  file_name: string;
  voice_name: string;
  interviewer_type: string;
  success: boolean;
  method: string;
}

export interface RealMCPVoice {
  interviewer_type: string;
  voice_id: string;
  voice_name: string;
  description: string;
  emotion: string;
  speed: number;
}

class RealMCPService {
  private config: RealMCPConfig;

  constructor(config: RealMCPConfig) {
    this.config = config;
  }

  /**
   * 语音识别 - 使用真实的 MiniMax MCP
   */
  async speechToText(audioBlob: Blob): Promise<RealMCPASRResult> {
    try {
      console.log('开始真实 MCP 语音识别，音频大小:', audioBlob.size);

      // 将音频转换为 Base64
      const audioBase64 = await this.blobToBase64(audioBlob);
      
      const requestBody = {
        audio_data: audioBase64,
        format: 'wav'
      };

      const response = await fetch(`${this.config.baseUrl}/api/real-mcp-speech/speech-to-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`真实 MCP ASR 请求失败: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      console.log('真实 MCP 语音识别成功:', result);
      
      return {
        text: result.text || '',
        confidence: result.confidence || 0.9,
        method: result.method || 'real_mcp',
        success: result.success || false
      };
    } catch (error) {
      console.error('真实 MCP 语音识别失败:', error);
      
      // 不再降级到模拟结果，直接抛出错误
      throw new Error(`真实 MCP 语音识别失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 文件上传语音识别 - 使用真实的 MiniMax MCP
   */
  async speechToTextFile(audioFile: File): Promise<RealMCPASRResult> {
    try {
      console.log('开始真实 MCP 文件语音识别，文件:', audioFile.name);

      const formData = new FormData();
      formData.append('file', audioFile);

      const response = await fetch(`${this.config.baseUrl}/api/real-mcp-speech/speech-to-text/file`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`真实 MCP 文件 ASR 请求失败: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      console.log('真实 MCP 文件语音识别成功:', result);
      
      return {
        text: result.text || '',
        confidence: result.confidence || 0.9,
        method: result.method || 'real_mcp',
        success: result.success || false
      };
    } catch (error) {
      console.error('真实 MCP 文件语音识别失败:', error);
      throw new Error(`真实 MCP 文件语音识别失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 文字转语音 - 使用真实的 MiniMax MCP
   */
  async textToSpeech(text: string, interviewerType: string = 'system'): Promise<RealMCPTTSResult> {
    try {
      console.log('开始真实 MCP 语音合成，面试官类型:', interviewerType);

      const requestBody = {
        text: text,
        interviewer_type: interviewerType
      };

      const response = await fetch(`${this.config.baseUrl}/api/real-mcp-speech/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`真实 MCP TTS 请求失败: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      console.log('真实 MCP 语音合成成功:', result);
      
      return {
        audio_url: result.audio_url || '',
        file_name: result.file_name || '',
        voice_name: result.voice_name || '',
        interviewer_type: result.interviewer_type || interviewerType,
        success: result.success || false,
        method: result.method || 'real_mcp'
      };
    } catch (error) {
      console.error('真实 MCP 语音合成失败:', error);
      throw new Error(`真实 MCP 语音合成失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 获取可用语音列表
   */
  async getVoices(): Promise<RealMCPVoice[]> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/real-mcp-speech/voices`);

      if (!response.ok) {
        throw new Error(`获取语音列表失败: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      return result.voices || [];
    } catch (error) {
      console.error('获取语音列表失败:', error);
      throw new Error(`获取语音列表失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<any> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/real-mcp-speech/health`);

      if (!response.ok) {
        throw new Error(`健康检查失败: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      return result;
    } catch (error) {
      console.error('真实 MCP 服务健康检查失败:', error);
      throw new Error(`健康检查失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 播放音频
   */
  async playAudio(audioUrl: string): Promise<void> {
    try {
      const audio = new Audio(audioUrl);
      
      return new Promise((resolve, reject) => {
        audio.onended = () => resolve();
        audio.onerror = () => reject(new Error('音频播放失败'));
        audio.play().catch(reject);
      });
    } catch (error) {
      console.error('播放音频失败:', error);
      throw new Error(`播放音频失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 将 Blob 转换为 Base64
   */
  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // 移除 data:audio/wav;base64, 前缀
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  /**
   * 检查服务是否可用
   */
  async isAvailable(): Promise<boolean> {
    try {
      const health = await this.healthCheck();
      return health.status === 'healthy';
    } catch {
      return false;
    }
  }
}

// 创建默认实例
export const createRealMCPService = (config: RealMCPConfig): RealMCPService => {
  return new RealMCPService(config);
};

// 默认配置
const defaultConfig: RealMCPConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
};

// 输出初始化日志
console.log('RealMCPService: 初始化真实 MCP 服务，baseUrl =', defaultConfig.baseUrl);

// 导出默认实例
export const realMCPService = createRealMCPService(defaultConfig);

export default RealMCPService; 