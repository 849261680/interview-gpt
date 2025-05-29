/**
 * 面试界面组件
 * 提供完整的AI面试体验，包括语音交互、实时通信、进度跟踪等
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { twMerge } from 'tailwind-merge';
import VoiceRecorder from './VoiceRecorder';
import VoiceSynthesis from './VoiceSynthesis';
import RealTimeAssessment from './RealTimeAssessment';
import { interviewSocketService, InterviewMessage, InterviewStatus } from '../../services/InterviewSocketService';

export interface InterviewInterfaceProps {
  /** 面试ID */
  interviewId: number;
  /** 面试配置 */
  config?: {
    enableVoice?: boolean;
    autoPlayResponse?: boolean;
    showProgress?: boolean;
    maxMessageLength?: number;
    enableRealTimeAssessment?: boolean;
  };
  /** 面试开始回调 */
  onInterviewStart?: () => void;
  /** 面试结束回调 */
  onInterviewEnd?: (result: any) => void;
  /** 错误回调 */
  onError?: (error: string) => void;
}

/**
 * 面试界面组件
 * 提供完整的AI面试体验
 */
const InterviewInterface: React.FC<InterviewInterfaceProps> = ({
  interviewId,
  config = {},
  onInterviewStart,
  onInterviewEnd,
  onError
}) => {
  const {
    enableVoice = true,
    autoPlayResponse = true,
    showProgress = true,
    maxMessageLength = 1000,
    enableRealTimeAssessment = true
  } = config;

  // 状态管理
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<InterviewMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [interviewStatus, setInterviewStatus] = useState<InterviewStatus | null>(null);
  // 不再硬编码初始面试官类型，而是从后端动态获取
  const [currentInterviewer, setCurrentInterviewer] = useState<string>('');
  const [interviewProgress, setInterviewProgress] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlayingResponse, setIsPlayingResponse] = useState(false);
  const [showVoiceControls, setShowVoiceControls] = useState(enableVoice);
  const [assessmentStarted, setAssessmentStarted] = useState(false);
  const [showAssessmentPanel, setShowAssessmentPanel] = useState(false);

  // Refs
  const socketServiceRef = useRef<typeof interviewSocketService | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // 启动实时评估
  const startRealTimeAssessment = useCallback(async () => {
    if (!enableRealTimeAssessment || assessmentStarted) return;

    try {
      const response = await fetch('/api/real-time-assessment/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interview_id: interviewId,
          position: '软件工程师', // 实际应用中应从面试配置获取
          difficulty: 'medium',
          interviewer_type: currentInterviewer
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setAssessmentStarted(true);
          console.log('实时评估已启动:', result.data);
        }
      }
    } catch (err) {
      console.error('启动实时评估失败:', err);
    }
  }, [interviewId, currentInterviewer, enableRealTimeAssessment, assessmentStarted]);

  // 处理消息并更新实时评估
  const updateRealTimeAssessment = useCallback(async (message: InterviewMessage) => {
    if (!enableRealTimeAssessment || !assessmentStarted) return;

    try {
      await fetch('/api/real-time-assessment/process-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interview_id: interviewId,
          message: {
            content: message.content,
            sender_type: message.sender_type,
            timestamp: message.timestamp
          },
          interviewer_type: currentInterviewer
        })
      });
    } catch (err) {
      console.error('更新实时评估失败:', err);
    }
  }, [interviewId, currentInterviewer, enableRealTimeAssessment, assessmentStarted]);

  // 初始化WebSocket连接
  const initializeConnection = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // 创建WebSocket服务实例
      const socketService = interviewSocketService;
      socketServiceRef.current = socketService;

      // 设置事件监听器
      socketService.on('connected', () => {
        console.log('面试WebSocket连接成功');
        setIsConnected(true);
        setIsLoading(false);
        
        // 连接成功后立即请求当前面试状态和活跃面试官信息
        socketService.requestCurrentStatus();
        
        // 启动实时评估
        startRealTimeAssessment();
        
        if (onInterviewStart) {
          onInterviewStart();
        }
      });

      socketService.on('disconnected', () => {
        console.log('面试WebSocket连接断开');
        setIsConnected(false);
      });

      socketService.on('message', (message: InterviewMessage) => {
        console.log('收到面试消息:', message);
        setMessages(prev => [...prev, message]);
        
        // 更新实时评估
        updateRealTimeAssessment(message);
        
        // 如果是面试官消息且启用了自动播放
        if (message.sender_type === 'interviewer' && autoPlayResponse) {
          // 延迟播放，确保消息已渲染
          setTimeout(() => {
            setIsPlayingResponse(true);
          }, 500);
        }
      });

      socketService.on('status', (status: InterviewStatus) => {
        console.log('面试状态更新:', status);
        setInterviewStatus(status);
      });

      socketService.on('interviewer_change', (data: any) => {
        console.log('面试官切换:', data);
        setCurrentInterviewer(data.interviewer_id);
        
        // 添加系统消息
        const systemMessage: InterviewMessage = {
          id: Date.now(),
          content: `现在由${data.interviewer_name}继续面试`,
          sender_type: 'system',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, systemMessage]);
      });

      socketService.on('interview_progress', (progress: any) => {
        console.log('面试进度更新:', progress);
        setInterviewProgress(progress);
      });

      socketService.on('interview_end', (result: any) => {
        console.log('面试结束:', result);
        setIsConnected(false);
        
        if (onInterviewEnd) {
          onInterviewEnd(result);
        }
      });

      socketService.on('error', (errorMsg: string) => {
        console.error('面试WebSocket错误:', errorMsg);
        setError(errorMsg);
        
        if (onError) {
          onError(errorMsg);
        }
      });

      // 连接WebSocket
      const connected = socketService.connect(interviewId);
      if (!connected) {
        throw new Error('无法建立WebSocket连接');
      }

    } catch (err) {
      const errorMsg = `连接失败: ${err instanceof Error ? err.message : '未知错误'}`;
      console.error(errorMsg);
      setError(errorMsg);
      setIsLoading(false);
      
      if (onError) {
        onError(errorMsg);
      }
    }
  }, [interviewId, autoPlayResponse, onInterviewStart, onInterviewEnd, onError, startRealTimeAssessment, updateRealTimeAssessment]);

  // 发送消息
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || !socketServiceRef.current || !isConnected) {
      return;
    }

    try {
      setIsLoading(true);
      
      // 创建用户消息对象
      const userMessage: InterviewMessage = {
        id: Date.now(),
        content: content,
        sender_type: 'user',
        timestamp: new Date().toISOString()
      };
      
      // 发送用户消息
      await socketServiceRef.current.sendMessage(content);
      
      // 更新实时评估
      updateRealTimeAssessment(userMessage);
      
      // 清空输入框
      setCurrentMessage('');
      
      // 聚焦到输入框
      if (inputRef.current) {
        inputRef.current.focus();
      }
      
    } catch (err) {
      const errorMsg = `发送消息失败: ${err instanceof Error ? err.message : '未知错误'}`;
      console.error(errorMsg);
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [isConnected, updateRealTimeAssessment]);

  // 处理语音录制完成
  const handleRecordingComplete = useCallback(async (audioBlob: Blob, transcript?: string) => {
    try {
      if (transcript) {
        // 如果有转录文本，直接发送
        await sendMessage(transcript);
      } else {
        // 否则上传音频文件进行处理
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('interview_id', interviewId.toString());

        const response = await fetch('/api/speech/transcribe', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          const result = await response.json();
          if (result.transcript) {
            await sendMessage(result.transcript);
          }
        } else {
          throw new Error('语音转录失败');
        }
      }
    } catch (err) {
      const errorMsg = `处理语音失败: ${err instanceof Error ? err.message : '未知错误'}`;
      console.error(errorMsg);
      setError(errorMsg);
    }
  }, [sendMessage, interviewId]);

  // 处理键盘事件
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(currentMessage);
    }
  }, [currentMessage, sendMessage]);

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // 组件挂载时初始化连接
  useEffect(() => {
    initializeConnection();

    // 清理函数
    return () => {
      if (socketServiceRef.current) {
        socketServiceRef.current.disconnect();
      }
    };
  }, [initializeConnection]);

  // 消息更新时滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // 获取面试官信息
  const getInterviewerInfo = (type: string) => {
    const interviewers = {
      coordinator: { name: '面试协调员', avatar: '🧑‍💼', color: 'bg-teal-500' },
      technical: { name: '技术面试官', avatar: '👨‍💻', color: 'bg-blue-500' },
      hr: { name: 'HR面试官', avatar: '👩‍💼', color: 'bg-green-500' },
      behavioral: { name: '行为面试官', avatar: '👨‍🏫', color: 'bg-purple-500' },
      product_manager: { name: '产品面试官', avatar: '🧩', color: 'bg-orange-500' },
      final: { name: '终面官', avatar: '👔', color: 'bg-gray-700' }
    };
    console.log(`[DEBUG] 获取面试官信息，类型: ${type}`);
    const interviewer = interviewers[type as keyof typeof interviewers] || interviewers.coordinator;
    console.log(`[DEBUG] 返回面试官信息:`, interviewer);
    return interviewer;
  };

  // 格式化消息时间
  const formatMessageTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 主面试区域 */}
      <div className="flex-1 flex flex-col">
        {/* 头部状态栏 */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* 连接状态 */}
              <div className="flex items-center space-x-2">
                <div className={twMerge(
                  'w-3 h-3 rounded-full',
                  isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                )}></div>
                <span className="text-sm text-gray-600">
                  {isConnected ? '已连接' : '未连接'}
                </span>
              </div>

              {/* 当前面试官 */}
              {isConnected && (
                <div className="flex items-center space-x-2">
                  <div className={twMerge(
                    'w-8 h-8 rounded-full flex items-center justify-center text-white text-sm',
                    getInterviewerInfo(currentInterviewer).color
                  )}>
                    {getInterviewerInfo(currentInterviewer).avatar}
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {getInterviewerInfo(currentInterviewer).name}
                  </span>
                </div>
              )}

              {/* 面试进度 */}
              {showProgress && interviewProgress && (
                <div className="flex items-center space-x-2">
                  <div className="text-sm text-gray-500">
                    进度: {interviewProgress.current_stage}/{interviewProgress.total_stages}
                  </div>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${(interviewProgress.current_stage / interviewProgress.total_stages) * 100}%` 
                      }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            {/* 控制按钮 */}
            <div className="flex items-center space-x-2">
              {/* 实时评估切换 */}
              {enableRealTimeAssessment && (
                <button
                  onClick={() => setShowAssessmentPanel(!showAssessmentPanel)}
                  className={twMerge(
                    'px-3 py-1 rounded-md text-sm font-medium transition-colors duration-200',
                    showAssessmentPanel
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  📊 实时评估
                </button>
              )}

              {/* 语音控制切换 */}
              {enableVoice && (
                <button
                  onClick={() => setShowVoiceControls(!showVoiceControls)}
                  className={twMerge(
                    'px-3 py-1 rounded-md text-sm font-medium transition-colors duration-200',
                    showVoiceControls
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  🎤 语音
                </button>
              )}
            </div>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-6 mt-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError(null)}
                  className="text-red-400 hover:text-red-600"
                >
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.length === 0 && isConnected && (
            <div className="text-center py-12">
              <div className="text-gray-400 text-lg mb-2">👋</div>
              <p className="text-gray-500">面试即将开始，请等待面试官提问...</p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={twMerge(
                'flex',
                message.sender_type === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={twMerge(
                  'max-w-xs lg:max-w-md px-4 py-2 rounded-lg',
                  message.sender_type === 'user'
                    ? 'bg-blue-500 text-white'
                    : message.sender_type === 'system'
                    ? 'bg-gray-100 text-gray-700 text-center'
                    : 'bg-white border border-gray-200 text-gray-900'
                )}
              >
                {message.sender_type !== 'user' && message.sender_type !== 'system' && (
                  <div className="flex items-center space-x-2 mb-1">
                    <div className={twMerge(
                      'w-6 h-6 rounded-full flex items-center justify-center text-white text-xs',
                      getInterviewerInfo(currentInterviewer).color
                    )}>
                      {getInterviewerInfo(currentInterviewer).avatar}
                    </div>
                    <span className="text-xs text-gray-500">
                      {getInterviewerInfo(currentInterviewer).name}
                    </span>
                  </div>
                )}
                
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                
                <div className={twMerge(
                  'text-xs mt-1',
                  message.sender_type === 'user' 
                    ? 'text-blue-100' 
                    : 'text-gray-400'
                )}>
                  {formatMessageTime(message.timestamp)}
                </div>
              </div>
            </div>
          ))}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          {/* 语音控制 */}
          {showVoiceControls && enableVoice && (
            <div className="mb-4 flex items-center justify-center space-x-4">
              <VoiceRecorder
                onRecordingComplete={handleRecordingComplete}
                onRecordingStart={() => setIsRecording(true)}
                onRecordingStop={() => setIsRecording(false)}
                disabled={!isConnected || isLoading}
                className="flex-shrink-0"
                onTranscription={(text: string) => {
                  // 处理语音识别结果
                  setCurrentMessage(text);
                }}
                onAudioResponse={(audioUrl: string) => {
                  // 处理音频响应
                  console.log('收到音频响应:', audioUrl);
                }}
                isInterviewActive={isConnected && !isLoading}
                currentInterviewer={currentInterviewer}
              />
              
              {messages.length > 0 && messages[messages.length - 1].sender_type === 'interviewer' && (
                <VoiceSynthesis
                  text={messages[messages.length - 1].content}
                  onPlayStart={() => setIsPlayingResponse(true)}
                  onPlayEnd={() => setIsPlayingResponse(false)}
                  autoPlay={autoPlayResponse}
                  className="flex-shrink-0"
                />
              )}
            </div>
          )}

          {/* 文本输入 */}
          <div className="flex space-x-4">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={isRecording ? "正在录音..." : "输入您的回答..."}
                disabled={!isConnected || isLoading || isRecording}
                maxLength={maxMessageLength}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <div className="flex justify-between items-center mt-1">
                <span className="text-xs text-gray-500">
                  {currentMessage.length}/{maxMessageLength}
                </span>
                {/* 提示文本已移除 */}
              </div>
            </div>
            
            <button
              onClick={() => sendMessage(currentMessage)}
              disabled={!isConnected || isLoading || !currentMessage.trim() || isRecording}
              className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                '发送'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 实时评估侧边栏 */}
      {enableRealTimeAssessment && showAssessmentPanel && (
        <div className="w-80 bg-white border-l border-gray-200 flex-shrink-0">
          <RealTimeAssessment
            interviewId={interviewId}
            enabled={assessmentStarted}
            className="h-full"
          />
        </div>
      )}
    </div>
  );
};

export default InterviewInterface; 