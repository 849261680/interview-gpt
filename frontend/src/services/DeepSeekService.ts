/**
 * DeepSeek服务
 * 提供与DeepSeek API交互的方法
 */
import axios from 'axios';
import { API_BASE_URL } from '../config/constants';

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponseChoice {
  index: number;
  message: {
    role: string;
    content: string;
  };
  finish_reason: string;
}

export interface ChatResponseUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatResponseData {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: ChatResponseChoice[];
  usage: ChatResponseUsage;
}

export interface ChatResponse {
  success: boolean;
  data?: ChatResponseData;
  error?: string;
}

/**
 * DeepSeek服务类
 */
class DeepSeekService {
  private readonly baseUrl: string;

  constructor() {
    // 注意: API_BASE_URL 中已经包含 /api 前缀
    this.baseUrl = API_BASE_URL + '/deepseek';
    console.log('DeepSeek服务初始化，API地址:', this.baseUrl);
  }

  /**
   * 发送聊天请求到DeepSeek API
   * @param messages 聊天消息列表
   * @param temperature 温度参数，控制回答的随机性
   * @param max_tokens 生成回答的最大token数
   * @returns 聊天响应
   */
  async chat(messages: ChatMessage[], temperature: number = 0.7, max_tokens: number = 2000): Promise<ChatResponse> {
    try {
      console.log('发送请求到DeepSeek API:', messages);
      
      const response = await axios.post<ChatResponse>(`${this.baseUrl}/chat`, {
        messages,
        temperature,
        max_tokens
      });
      
      console.log('DeepSeek API响应:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('DeepSeek API调用失败:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || '服务器连接失败'
      };
    }
  }

  /**
   * 获取服务状态
   * @returns 服务状态
   */
  async getStatus(): Promise<any> {
    try {
      const response = await axios.get(`${this.baseUrl}/status`);
      return response.data;
    } catch (error: any) {
      console.error('获取DeepSeek服务状态失败:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || '服务器连接失败'
      };
    }
  }
}

// 创建单例实例
const deepseekService = new DeepSeekService();
export default deepseekService;
