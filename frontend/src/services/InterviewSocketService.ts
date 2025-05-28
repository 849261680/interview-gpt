/**
 * 面试WebSocket服务
 * 管理与后端的实时通信，处理面试消息和状态更新
 */
import { EventEmitter } from 'events';

export interface InterviewMessage {
  id: number;
  content: string;
  sender_type: 'user' | 'interviewer' | 'system';
  interviewer_id?: string;
  timestamp: string;
}

export interface InterviewStatus {
  interview_id: number;
  status: 'active' | 'completed' | 'cancelled';
  position: string;
  difficulty: string;
  active_interviewer?: string;
}

export interface InterviewStageUpdate {
  message: InterviewMessage;
  stage: string;
}

/**
 * 面试WebSocket服务
 * 管理面试过程中的实时通信
 */
class InterviewSocketService extends EventEmitter {
  private socket: WebSocket | null = null;
  private interviewId: number | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private maxReconnectAttempts = 5;
  private reconnectAttempts = 0;
  private reconnectInterval = 3000; // 3秒
  private isConnecting = false;
  private messageQueue: any[] = [];
  
  /**
   * 初始化WebSocket连接
   * @param interviewId 面试ID
   * @returns 是否成功初始化
   */
  public connect(interviewId: number): boolean {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.disconnect();
    }
    
    this.interviewId = interviewId;
    this.isConnecting = true;
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const wsUrl = baseUrl.replace(/^http/, 'ws');
      this.socket = new WebSocket(`${wsUrl}/interview-process/${interviewId}/ws`);
      
      // 连接打开
      this.socket.onopen = () => {
        console.log(`面试WebSocket连接成功: ID=${interviewId}`);
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.emit('connected');
        
        // 发送队列中的消息
        while (this.messageQueue.length > 0) {
          const msg = this.messageQueue.shift();
          this.sendRaw(msg);
        }
      };
      
      // 接收消息
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };
      
      // 连接关闭
      this.socket.onclose = () => {
        console.log(`面试WebSocket连接关闭: ID=${interviewId}`);
        this.socket = null;
        
        if (this.isConnecting) {
          this.tryReconnect();
        } else {
          this.emit('disconnected');
        }
      };
      
      // 连接错误
      this.socket.onerror = (error) => {
        console.error(`面试WebSocket连接错误:`, error);
        this.emit('error', error);
      };
      
      return true;
    } catch (error) {
      console.error('初始化WebSocket连接失败:', error);
      this.isConnecting = false;
      return false;
    }
  }
  
  /**
   * 断开WebSocket连接
   */
  public disconnect(): void {
    this.isConnecting = false;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    this.messageQueue = [];
    this.interviewId = null;
    this.emit('disconnected');
  }
  
  /**
   * 尝试重新连接
   */
  private tryReconnect(): void {
    if (this.reconnectTimer || this.reconnectAttempts >= this.maxReconnectAttempts || !this.interviewId) {
      this.isConnecting = false;
      this.emit('reconnect_failed');
      return;
    }
    
    this.reconnectAttempts++;
    console.log(`尝试重新连接WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.interviewId) {
        this.connect(this.interviewId);
      }
    }, this.reconnectInterval);
    
    this.emit('reconnecting', this.reconnectAttempts);
  }
  
  /**
   * 处理接收到的消息
   * @param data 消息数据
   */
  private handleMessage(data: any): void {
    const { type, data: messageData } = data;
    
    switch (type) {
      case 'history':
        this.emit('history', messageData.messages);
        break;
        
      case 'message':
        this.emit('message', messageData);
        break;
        
      case 'status':
        this.emit('status', messageData);
        break;
        
      case 'new_stage':
        this.emit('new_stage', messageData);
        break;
        
      case 'interview_ended':
        this.emit('interview_ended', messageData);
        break;
        
      case 'error':
        this.emit('socket_error', messageData);
        break;
        
      default:
        console.warn('未知WebSocket消息类型:', type, messageData);
    }
  }
  
  /**
   * 发送用户消息
   * @param content 消息内容
   */
  public sendMessage(content: string): void {
    this.send({
      type: 'message',
      content
    });
  }
  
  /**
   * 请求进入下一个面试阶段
   */
  public requestNextStage(): void {
    this.send({
      type: 'next_stage'
    });
  }
  
  /**
   * 请求结束面试
   */
  public requestEndInterview(): void {
    this.send({
      type: 'end_interview'
    });
  }
  
  /**
   * 发送消息
   * @param data 消息数据
   */
  private send(data: any): void {
    const message = JSON.stringify(data);
    
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.sendRaw(message);
    } else {
      // 存储消息，等待连接建立后发送
      this.messageQueue.push(message);
      
      // 如果没有活跃连接，尝试重新连接
      if (!this.socket && this.interviewId && !this.isConnecting) {
        this.connect(this.interviewId);
      }
    }
  }
  
  /**
   * 直接发送原始消息
   * @param message 原始消息
   */
  private sendRaw(message: string): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(message);
    }
  }
  
  /**
   * 检查连接状态
   * @returns 是否已连接
   */
  public isConnected(): boolean {
    return !!this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

// 导出单例实例
export const interviewSocketService = new InterviewSocketService();
export default interviewSocketService;
