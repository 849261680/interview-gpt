/**
 * 语音服务
 * 处理语音识别(ASR)和语音合成(TTS)功能
 */

export interface VoiceConfig {
  apiKey?: string;
  region?: string;
  language?: string;
}

export interface ASRResult {
  text: string;
  confidence: number;
  duration: number;
}

export interface TTSOptions {
  voice?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
}

class VoiceService {
  private config: VoiceConfig;
  private isSupported: boolean;

  constructor(config: VoiceConfig = {}) {
    this.config = {
      language: 'zh-CN',
      ...config
    };
    this.isSupported = this.checkSupport();
  }

  /**
   * 检查浏览器是否支持语音功能
   */
  private checkSupport(): boolean {
    // 只在客户端检查
    if (typeof window === 'undefined') {
      console.warn('VoiceService: 检测到非浏览器环境，语音功能不可用');
      return false;
    }
    
    const hasRecognition = !!(window.SpeechRecognition || (window as any).webkitSpeechRecognition);
    const hasSynthesis = !!window.speechSynthesis;
    
    if (!hasRecognition) {
      console.warn('VoiceService: 浏览器不支持语音识别(SpeechRecognition)API');
    }
    
    if (!hasSynthesis) {
      console.warn('VoiceService: 浏览器不支持语音合成(speechSynthesis)API');
    }
    
    // 只要有一个功能可用就返回true
    const isSupported = hasRecognition || hasSynthesis;
    console.log(`VoiceService: 语音功能检测完成 - ${isSupported ? '支持' : '不支持'}`);
    return isSupported;
  }

  /**
   * 语音识别 - 使用浏览器原生API
   */
  async speechToText(audioBlob: Blob): Promise<ASRResult> {
    return new Promise((resolve, reject) => {
      try {
        // 检查是否在客户端
        if (typeof window === 'undefined') {
          reject(new Error('语音识别只能在浏览器中使用'));
          return;
        }

        // 检查浏览器支持
        const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
          // 如果不支持原生API，可以调用后端API
          this.callBackendASR(audioBlob)
            .then(resolve)
            .catch(reject);
          return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = this.config.language || 'zh-CN';
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event: any) => {
          try {
            const result = event.results[0][0];
            console.log('VoiceService: 语音识别成功', { transcript: result.transcript, confidence: result.confidence });
            resolve({
              text: result.transcript,
              confidence: result.confidence,
              duration: event.timeStamp
            });
          } catch (err) {
            console.error('VoiceService: 解析语音识别结果失败', err);
            reject(new Error('解析语音识别结果失败'));
          }
        };

        recognition.onerror = (event: { error: string }) => {
          console.error(`VoiceService: 语音识别API错误 - ${event.error}`);
          reject(new Error(`语音识别错误: ${event.error}`));
        };

        recognition.onend = () => {
          // 识别结束
        };

        // 注意：浏览器原生API不能直接处理Blob，需要实时录音
        // 这里我们调用后端API处理
        this.callBackendASR(audioBlob)
          .then(resolve)
          .catch(reject);

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 调用后端语音识别API
   */
  private async callBackendASR(audioBlob: Blob): Promise<ASRResult> {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('language', this.config.language || 'zh-CN');

      const response = await fetch('/api/voice/asr', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`ASR API错误: ${response.status}`);
      }

      const result = await response.json();
      return {
        text: result.text || '语音识别结果为空',
        confidence: result.confidence || 0.8,
        duration: result.duration || 0
      };
    } catch (error) {
      console.error('VoiceService: 后端ASR调用失败:', error);
      // 返回模拟结果
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      return {
        text: `语音识别服务暂时不可用，请检查麦克风权限或使用文字输入。(错误: ${errorMessage})`,
        confidence: 0.5,
        duration: 1000
      };
    }
  }

  /**
   * 语音合成 - 使用浏览器原生API
   */
  async textToSpeech(text: string, options: TTSOptions = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // 检查是否在客户端
        if (typeof window === 'undefined') {
          reject(new Error('语音合成只能在浏览器中使用'));
          return;
        }

        if (!window.speechSynthesis) {
          reject(new Error('浏览器不支持语音合成'));
          return;
        }

        // 停止当前播放
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = this.config.language || 'zh-CN';
        utterance.rate = options.rate || 0.9;
        utterance.pitch = options.pitch || 1;
        utterance.volume = options.volume || 0.8;

        // 设置语音
        if (options.voice) {
          const voices = window.speechSynthesis.getVoices();
          const selectedVoice = voices.find(voice => 
            voice.name.includes(options.voice!) || 
            voice.lang.includes(this.config.language!)
          );
          if (selectedVoice) {
            utterance.voice = selectedVoice;
          }
        }

        utterance.onend = () => resolve();
        utterance.onerror = (event: { error: string }) => {
          console.error(`VoiceService: 语音合成API错误 - ${event.error}`);
          reject(new Error(`语音合成错误: ${event.error}`));
        };

        window.speechSynthesis.speak(utterance);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 获取可用的语音列表
   */
  getAvailableVoices(): SpeechSynthesisVoice[] {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      return [];
    }
    return window.speechSynthesis.getVoices();
  }

  /**
   * 停止语音播放
   */
  stopSpeaking(): void {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  }

  /**
   * 检查是否正在播放
   */
  isSpeaking(): boolean {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      return false;
    }
    return window.speechSynthesis.speaking;
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<VoiceConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * 获取支持状态
   */
  getSupport(): boolean {
    return this.isSupported;
  }
}

// 创建全局实例 - 只在客户端创建
export const voiceService = (() => {
  try {
    if (typeof window !== 'undefined') {
      console.log('VoiceService: 初始化语音服务...');
      return new VoiceService();
    }
    return null as any;
  } catch (error) {
    console.error('VoiceService: 初始化语音服务失败', error);
    return {
      getSupport: () => false,
      speechToText: () => Promise.reject(new Error('语音服务初始化失败')),
      textToSpeech: () => Promise.reject(new Error('语音服务初始化失败')),
      stopSpeaking: () => {},
      isSpeaking: () => false,
      getAvailableVoices: () => [],
      updateConfig: () => {}
    };
  }
})();

// 类型声明
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export default VoiceService; 