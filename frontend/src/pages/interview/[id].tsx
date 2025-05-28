import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Link from 'next/link';

// MiniMax MCP 服务导入
import MinimaxMCPService, { 
  createMinimaxService, 
  getMinimaxService,
  ChatMessage,
  ASRResult,
  TTSResult 
} from '../../services/MinimaxMCPService';
import { 
  getMinimaxConfig, 
  validateConfig,
  getInterviewerVoice,
  getInterviewerPrompt,
  asrConfig,
  ttsConfig,
  chatConfig
} from '../../config/minimax.config';

// 面试服务导入
import interviewService, { Message as InterviewMessage } from '../../services/InterviewService';

/**
 * 面试进行页面 - 集成MiniMax MCP实时AI语音面试
 * 支持语音识别、语音合成和实时AI对话
 */
export default function InterviewSession() {
  const router = useRouter();
  const { id } = router.query;
  const interviewId = id ? parseInt(id as string) : 0;
  
  // 面试官类型定义
  type InterviewerType = 'technical' | 'hr' | 'product' | 'final';

  // 基础状态管理
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [currentInterviewer, setCurrentInterviewer] = useState<InterviewerType>('technical');
  const [isLoading, setIsLoading] = useState(false);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewEnded, setInterviewEnded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // MiniMax MCP 状态
  const [minimaxService, setMinimaxService] = useState<MinimaxMCPService | null>(null);
  const [mcpConnected, setMcpConnected] = useState(false);
  const [mcpError, setMcpError] = useState<string | null>(null);
  
  // 语音功能状态
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [streamingResponse, setStreamingResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  
  // 语音相关引用
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const conversationHistoryRef = useRef<ChatMessage[]>([]);

  // 面试官数据
  const interviewers = {
    technical: {
      id: 'technical',
      name: '李工',
      role: '技术面试官',
      avatar: '👨‍💻',
      description: '资深技术专家，关注技术深度和解决问题能力',
      color: '#3b82f6',
      voice: 'male-qingsong'
    },
    hr: {
      id: 'hr',
      name: '王经理',
      role: 'HR面试官',
      avatar: '👩‍💼',
      description: '人力资源总监，关注职业规划和公司文化匹配度',
      color: '#10b981',
      voice: 'female-zhiyu'
    },
    product: {
      id: 'product',
      name: '陈经理',
      role: '产品经理',
      avatar: '👨‍💼',
      description: '资深产品总监，关注产品思维和用户视角',
      color: '#8b5cf6',
      voice: 'male-chunhou'
    },
    final: {
      id: 'final',
      name: '张总',
      role: '总面试官',
      avatar: '👔',
      description: '高级总监，负责最终评估和决策',
      color: '#f59e0b',
      voice: 'male-chunhou'
    }
  };

  // 初始化MiniMax MCP服务
  useEffect(() => {
    initializeMinimaxMCP();
    initializeVoiceFeatures();
    
    return () => {
      cleanup();
    };
  }, []);

  // 初始化MiniMax MCP
  const initializeMinimaxMCP = async () => {
    try {
      // 只在客户端运行
      if (typeof window === 'undefined') {
        setVoiceEnabled(false);
        return;
      }

      // 获取配置
      const config = getMinimaxConfig();
      
      // 验证配置
      if (!validateConfig(config)) {
        setMcpError('MiniMax配置无效，请检查API密钥和Group ID');
        console.warn('MiniMax配置无效，将使用模拟模式');
        return;
      }

      // 创建服务实例
      const service = createMinimaxService(config);
      
      if (service) {
        await service.initialize();
        setMinimaxService(service);
        setMcpConnected(service.isConnectedToMCP());
        console.log('MiniMax MCP服务初始化成功');
      }
    } catch (error) {
      console.error('MiniMax MCP初始化失败:', error);
      setMcpError(`初始化失败: ${error.message}`);
    }
  };

  // 初始化语音功能
  const initializeVoiceFeatures = async () => {
    try {
      // 只在客户端运行
      if (typeof window === 'undefined') {
        setVoiceEnabled(false);
        return;
      }

      // 检查浏览器支持
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('浏览器不支持录音功能');
        setVoiceEnabled(false);
        return;
      }

      // 请求麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: asrConfig.sampleRate
        } 
      });
      
      // 创建音频上下文用于音量检测
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      // 停止初始流
      stream.getTracks().forEach(track => track.stop());
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知原因';
      console.error(`语音功能初始化失败: ${errorMessage}`, error);
      setVoiceEnabled(false);
      
      // 尝试重新初始化，但不请求麦克风权限
      try {
        if (typeof window !== 'undefined' && window.AudioContext) {
          audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
          console.log('仅初始化音频上下文成功');
        }
      } catch (contextError) {
        console.error('初始化音频上下文失败:', contextError);
      }
    }
  };

  // 清理资源
  const cleanup = () => {
    // 停止任何正在进行的录音
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
    
    // 取消任何计时器
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
    }
    
    // 关闭音频上下文
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    
    // 停止任何正在播放的音频
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
  };

  // 语音合成 - 使用MiniMax TTS或浏览器内置TTS
  const speakText = async (text: string) => {
    if (!voiceEnabled || !text) return;
    
    try {
      setIsPlaying(true);
      
      // 停止当前播放
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }
      
      if (minimaxService && mcpConnected) {
        // 使用MiniMax TTS
        const voice = getInterviewerVoice(currentInterviewer);
        const ttsResult = await minimaxService.textToSpeech(text, voice, ttsConfig);
        
        // 播放音频
        await minimaxService.playTTSAudio(ttsResult.audioUrl);
      } else {
        // 降级到浏览器TTS
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.lang = 'zh-CN';
        
        // 尝试匹配声音
        const voices = window.speechSynthesis.getVoices();
        const chineseVoice = voices.find(voice => voice.lang.includes('zh'));
        if (chineseVoice) {
          utterance.voice = chineseVoice;
        }
        
        // 设置事件处理器
        utterance.onend = () => {
          setIsPlaying(false);
        };
        
        utterance.onerror = () => {
          console.error('语音合成出错');
          setIsPlaying(false);
        };
        
        window.speechSynthesis.speak(utterance);
      }
    } catch (error) {
      console.error('语音合成失败:', error);
      setIsPlaying(false);
    }
  };

  // 停止语音播放
  const stopSpeaking = () => {
    if (minimaxService && currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    } else {
      window.speechSynthesis.cancel();
    }
    
    setIsPlaying(false);
  };

  // 开始录音
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: asrConfig.sampleRate
        } 
      });
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        processAudioRecording(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // 开始计时
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      // 开始音量检测
      startAudioLevelDetection(stream);
      
    } catch (error) {
      console.error('开始录音失败:', error);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  // 停止录音
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    setAudioLevel(0);
    
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
  };

  // 音量检测
  const startAudioLevelDetection = (stream: MediaStream) => {
    if (!audioContextRef.current || !analyserRef.current) return;
    
    const source = audioContextRef.current.createMediaStreamSource(stream);
    source.connect(analyserRef.current);
    
    analyserRef.current.fftSize = 256;
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const detectLevel = () => {
      if (!isRecording) return;
      
      analyserRef.current!.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / bufferLength;
      setAudioLevel(average / 255);
      
      requestAnimationFrame(detectLevel);
    };
    
    detectLevel();
  };

  // 处理录音 - 使用MiniMax ASR
  const processAudioRecording = async (audioBlob: Blob) => {
    try {
      setIsLoading(true);
      
      let asrResult: ASRResult;
      
      // 使用后端实现的语音识别服务
      try {
        // 尝试使用MiniMax ASR服务
        if (minimaxService) {
          asrResult = await minimaxService.speechToText(audioBlob, asrConfig);
        } else {
          // 使用后端实现的语音识别 API
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.wav');
          
          const response = await fetch('/api/real-mcp-speech/speech-to-text/file', {
            method: 'POST',
            body: formData
          });
          
          if (!response.ok) {
            throw new Error(`语音识别请求失败: ${response.status} ${response.statusText}`);
          }
          
          const result = await response.json();
          
          if (result.success && result.text) {
            asrResult = {
              text: result.text,
              confidence: result.confidence || 0.9,
              duration: 2000 // 估计值
            };
          } else {
            throw new Error('语音识别失败或结果为空');
          }
        }
      } catch (error) {
        console.error('语音识别失败:', error);
        
        // 显示错误消息
        setMessages(prev => [...prev, {
          id: Date.now(),
          content: `语音识别失败: ${error instanceof Error ? error.message : '未知错误'}`,
          sender: 'system',
          timestamp: new Date().toISOString(),
          isError: true
        }]);
        
        setIsLoading(false);
        return; // 如果语音识别失败，直接返回
      }
      
      // 添加用户语音转换的消息到对话界面
      const userMessage = {
        id: Date.now(),
        content: asrResult.text,
        sender: 'user',
        timestamp: new Date().toISOString(),
        isVoice: true,
        confidence: asrResult.confidence
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      try {
        // 更新对话历史
        const newUserMessage: InterviewMessage = {
          role: 'user',
          content: asrResult.text
        };
        
        // 如果是对话开始，添加系统提示
        if (conversationHistoryRef.current.length === 0) {
          const systemMessage: InterviewMessage = {
            role: 'system',
            content: getInterviewerPrompt(currentInterviewer)
          };
          conversationHistoryRef.current.push(systemMessage);
        }
        
        // 添加用户消息到对话历史
        conversationHistoryRef.current.push(newUserMessage);
        
        // 使用面试服务获取AI回复
        const response = await interviewService.getAIResponse(
          conversationHistoryRef.current as InterviewMessage[],
          minimaxService
        );
        
        if (response.success) {
          // 添加AI回复到对话历史
          conversationHistoryRef.current.push({
            role: 'assistant',
            content: response.content
          });
          
          // 添加AI回复到UI显示
          setMessages(prev => [...prev, {
            id: Date.now(),
            content: response.content,
            sender: currentInterviewer,
            timestamp: new Date().toISOString()
          }]);
          
          // 如果语音功能启用，用语音读出回复
          if (voiceEnabled && !isPlaying) {
            await speakText(response.content);
          }
        } else {
          // 处理错误情况
          setMessages(prev => [...prev, {
            id: Date.now(),
            content: '抱歉，面试系统暂时无法响应。请稍后再试。',
            sender: currentInterviewer,
            timestamp: new Date().toISOString(),
            isError: true
          }]);
          console.error('获取AI回复失败:', response.error);
        }
      } catch (error) {
        console.error('处理语音识别结果时出错:', error);
        setMessages(prev => [...prev, {
          id: Date.now(),
          content: '抱歉，处理您的消息时出现了错误。',
          sender: currentInterviewer,
          timestamp: new Date().toISOString(),
          isError: true
        }]);
      } finally {
        setIsLoading(false);
      }
    } catch (error) {
      console.error('处理录音失败:', error);
      setIsLoading(false);
      
      // 显示通用错误消息
      setMessages(prev => [...prev, {
        id: Date.now(),
        content: '处理录音遇到问题，请重新尝试。',
        sender: 'system',
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    }
  };



  // 格式化录音时间
  const formatRecordingTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 滚动到底部
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, streamingResponse]);

  // 开始面试
  const startInterview = () => {
    setInterviewStarted(true);
    const interviewerPrompt = getInterviewerPrompt(currentInterviewer);
    
    const welcomeMessage = {
      id: Date.now(),
      content: interviewerPrompt.welcomeMessage,
      sender: 'interviewer',
      interviewer: currentInterviewer,
      timestamp: new Date().toISOString()
    };
    
    setMessages([welcomeMessage]);
    
    // 初始化对话历史
    conversationHistoryRef.current = [
      {
        role: 'system',
        content: interviewerPrompt.systemPrompt
      },
      {
        role: 'assistant',
        content: interviewerPrompt.welcomeMessage,
        timestamp: new Date().toISOString()
      }
    ];
    
    // 延迟发送第一个问题
    setTimeout(async () => {
      const firstQuestion = "请先简单介绍一下你自己，包括你的技术背景和工作经验。";
      
      const questionMessage = {
        id: Date.now() + 1,
        content: firstQuestion,
        sender: 'interviewer',
        interviewer: currentInterviewer,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, questionMessage]);
      
      // 更新对话历史
      conversationHistoryRef.current.push({
        role: 'assistant',
        content: firstQuestion,
        timestamp: new Date().toISOString()
      });
      
      // 语音播放第一个问题
      if (voiceEnabled) {
        await speakText(firstQuestion);
      }
    }, 1500);
  };

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage = {
      id: Date.now(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // 更新对话历史
      const newUserMessage: InterviewMessage = {
        role: 'user',
        content: inputValue
      };
      
      // 如果是对话开始，添加系统提示
      if (conversationHistoryRef.current.length === 0) {
        const systemMessage: InterviewMessage = {
          role: 'system',
          content: getInterviewerPrompt(currentInterviewer)
        };
        conversationHistoryRef.current.push(systemMessage);
      }
      
      // 添加用户消息到对话历史
      conversationHistoryRef.current.push(newUserMessage);
      
      // 使用面试服务获取AI回复 - 默认使用DeepSeek，如果需要MiniMax则将其传入
      const response = await interviewService.getAIResponse(
        conversationHistoryRef.current as InterviewMessage[], 
        minimaxService
      );
      
      if (response.success) {
        // 添加AI回复到对话历史
        conversationHistoryRef.current.push({
          role: 'assistant',
          content: response.content
        });
        
        // 添加AI回复到UI显示
        setMessages(prev => [...prev, {
          id: Date.now(),
          content: response.content,
          sender: currentInterviewer,
          timestamp: new Date().toISOString()
        }]);
        
        // 如果语音功能启用，用语音读出回复
        if (voiceEnabled && !isPlaying) {
          await speakText(response.content);
        }
      } else {
        // 处理错误情况
        setMessages(prev => [...prev, {
          id: Date.now(),
          content: '抱歉，面试系统暂时无法响应。请稍后再试。',
          sender: currentInterviewer,
          timestamp: new Date().toISOString(),
          isError: true
        }]);
        console.error('获取AI回复失败:', response.error);
      }
    } catch (error) {
      console.error('处理消息时出错:', error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        content: '抱歉，处理您的消息时出现了错误。',
        sender: currentInterviewer,
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
      
      // 滚动到最新消息
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  // 切换面试官
  const switchInterviewer = () => {
    const stages = ['technical', 'hr', 'product', 'final'];
    const currentIndex = stages.indexOf(currentInterviewer);
    const nextIndex = (currentIndex + 1) % stages.length;
    const nextStage = stages[nextIndex];
    
    setCurrentInterviewer(nextStage);
    
    const transitionMessage = {
      id: Date.now(),
      content: `感谢你的回答！现在让我们进入下一个环节。`,
      sender: 'system',
      timestamp: new Date().toISOString()
    };
    
    const newInterviewerPrompt = getInterviewerPrompt(nextStage);
    const newInterviewerMessage = {
      id: Date.now() + 1,
      content: newInterviewerPrompt.welcomeMessage,
      sender: 'interviewer',
      interviewer: nextStage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, transitionMessage, newInterviewerMessage]);
    
    // 重置对话历史为新面试官
    conversationHistoryRef.current = [
      {
        role: 'system',
        content: newInterviewerPrompt.systemPrompt
      },
      {
        role: 'assistant',
        content: newInterviewerPrompt.welcomeMessage,
        timestamp: new Date().toISOString()
      }
    ];
  };

  // 结束面试
  const endInterview = () => {
    setInterviewEnded(true);
    const endMessage = {
      id: Date.now(),
      content: "感谢你参加今天的面试！我们会在3-5个工作日内给你反馈。祝你好运！",
      sender: 'system',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, endMessage]);
  };

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1f2937 0%, #312e81 50%, #1f2937 100%)',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <Head>
        <title>MiniMax AI语音面试 - Interview-GPT</title>
        <meta name="description" content="基于MiniMax MCP的实时AI语音面试" />
      </Head>

      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse {
            0%, 100% {
              opacity: 0.4;
              transform: scale(1);
            }
            50% {
              opacity: 1;
              transform: scale(1.1);
            }
          }
          
          @keyframes wave {
            0%, 100% {
              transform: scaleY(1);
            }
            50% {
              transform: scaleY(1.5);
            }
          }
          
          @keyframes glow {
            0%, 100% {
              box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
            }
            50% {
              box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
            }
          }
          
          @keyframes typing {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
          }
          
          .recording-button {
            animation: glow 2s ease-in-out infinite;
          }
          
          .audio-wave {
            animation: wave 0.5s ease-in-out infinite;
          }
          
          .pulse-dot {
            animation: pulse 1.5s ease-in-out infinite;
          }
          
          .typing-indicator {
            animation: typing 1s ease-in-out infinite;
          }
          
          /* 滚动条样式 */
          ::-webkit-scrollbar {
            width: 6px;
          }
          
          ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
          }
          
          ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 3px;
          }
          
          ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.5);
          }
        `
      }} />

      {/* 顶部导航栏 */}
      <nav style={{
        background: 'rgba(0, 0, 0, 0.3)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        padding: '1rem 0',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <span style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                cursor: 'pointer'
              }}>
                Interview-GPT
              </span>
            </Link>
            <span style={{
              marginLeft: '1rem',
              fontSize: '0.875rem',
              color: 'rgba(255, 255, 255, 0.7)',
              background: 'rgba(16, 185, 129, 0.2)',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.25rem',
              border: '1px solid rgba(16, 185, 129, 0.3)'
            }}>
              MiniMax MCP
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {/* MCP连接状态 */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.75rem',
              color: mcpConnected ? '#10b981' : '#ef4444'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: mcpConnected ? '#10b981' : '#ef4444'
              }}></div>
              <span>{mcpConnected ? 'MCP已连接' : 'MCP未连接'}</span>
            </div>
            <span style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
              面试ID: {interviewId}
            </span>
            <Link href="/">
              <button style={{
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}>
                返回首页
              </button>
            </Link>
          </div>
        </div>
      </nav>

      {/* MCP错误提示 */}
      {mcpError && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#fca5a5',
          padding: '1rem',
          margin: '1rem',
          borderRadius: '0.5rem',
          fontSize: '0.875rem'
        }}>
          <strong>MiniMax MCP 错误:</strong> {mcpError}
          <br />
          <small>系统将使用模拟模式继续运行，部分功能可能受限。</small>
        </div>
      )}

      <div style={{ display: 'flex', height: 'calc(100vh - 80px)' }}>
        {/* 左侧面试官信息 */}
        <div style={{
          width: '300px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRight: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem'
        }}>
          {/* 面试进度 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '1rem',
            padding: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' }}>面试进度</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {Object.entries(interviewers).map(([key, interviewer]) => (
                <div key={key} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem',
                  borderRadius: '0.375rem',
                  background: currentInterviewer === key ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: currentInterviewer === key ? interviewer.color : 'rgba(255, 255, 255, 0.3)'
                  }}></div>
                  <span style={{
                    fontSize: '0.875rem',
                    color: currentInterviewer === key ? 'white' : 'rgba(255, 255, 255, 0.7)'
                  }}>
                    {interviewer.role}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* 面试控制 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '1rem',
            padding: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' }}>面试控制</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {!interviewStarted ? (
                <button
                  onClick={startInterview}
                  style={{
                    background: 'linear-gradient(45deg, #10b981, #059669)',
                    color: 'white',
                    border: 'none',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  开始AI面试
                </button>
              ) : (
                <>
                  <button
                    onClick={switchInterviewer}
                    disabled={interviewEnded}
                    style={{
                      background: interviewEnded ? 'rgba(107, 114, 128, 0.5)' : 'linear-gradient(45deg, #3b82f6, #1d4ed8)',
                      color: 'white',
                      border: 'none',
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      cursor: interviewEnded ? 'not-allowed' : 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      opacity: interviewEnded ? 0.6 : 1
                    }}
                  >
                    下一位面试官
                  </button>
                  <button
                    onClick={endInterview}
                    disabled={interviewEnded}
                    style={{
                      background: interviewEnded ? 'rgba(107, 114, 128, 0.5)' : 'linear-gradient(45deg, #ef4444, #dc2626)',
                      color: 'white',
                      border: 'none',
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      cursor: interviewEnded ? 'not-allowed' : 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      opacity: interviewEnded ? 0.6 : 1
                    }}
                  >
                    结束面试
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* 右侧聊天区域 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* 消息列表 */}
          <div style={{
            flex: 1,
            padding: '2rem',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem'
          }}>
            {!interviewStarted ? (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                textAlign: 'center'
              }}>
                <div>
                  <div style={{
                    width: '100px',
                    height: '100px',
                    background: 'linear-gradient(45deg, #3b82f6, #8b5cf6)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 1.5rem',
                    fontSize: '3rem'
                  }}>
                    🤖
                  </div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem' }}>
                    MiniMax AI语音面试
                  </h2>
                  <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
                    基于MiniMax MCP技术栈的实时AI语音面试系统
                    <br />
                    支持语音识别、语音合成和智能对话
                  </p>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    gap: '1rem',
                    fontSize: '0.875rem',
                    color: 'rgba(255, 255, 255, 0.6)'
                  }}>
                    <span>🎤 语音识别</span>
                    <span>🔊 语音合成</span>
                    <span>🤖 智能对话</span>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <div key={message.id} style={{
                    display: 'flex',
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      maxWidth: '70%',
                      padding: '1rem 1.5rem',
                      borderRadius: '1rem',
                      background: message.sender === 'user' 
                        ? 'linear-gradient(45deg, #3b82f6, #1d4ed8)'
                        : message.sender === 'system'
                        ? 'rgba(245, 158, 11, 0.2)'
                        : 'rgba(255, 255, 255, 0.1)',
                      border: message.sender === 'system' ? '1px solid rgba(245, 158, 11, 0.3)' : 'none',
                      position: 'relative'
                    }}>
                      {/* 面试官信息 */}
                      {message.sender === 'interviewer' && (
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          marginBottom: '0.5rem'
                        }}>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            fontSize: '0.875rem',
                            color: 'rgba(255, 255, 255, 0.8)'
                          }}>
                            <span>{interviewers[message.interviewer]?.avatar}</span>
                            <span>{interviewers[message.interviewer]?.name}</span>
                            <span style={{
                              fontSize: '0.625rem',
                              background: 'rgba(16, 185, 129, 0.2)',
                              color: '#10b981',
                              padding: '0.125rem 0.25rem',
                              borderRadius: '0.125rem'
                            }}>
                              MiniMax
                            </span>
                          </div>
                          {/* 语音播放按钮 */}
                          {voiceEnabled && (
                            <button
                              onClick={() => speakText(message.content)}
                              disabled={isPlaying}
                              style={{
                                background: 'rgba(255, 255, 255, 0.1)',
                                color: 'rgba(255, 255, 255, 0.7)',
                                border: '1px solid rgba(255, 255, 255, 0.2)',
                                padding: '0.25rem 0.5rem',
                                borderRadius: '0.25rem',
                                cursor: isPlaying ? 'not-allowed' : 'pointer',
                                fontSize: '0.75rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.25rem'
                              }}
                              title="播放语音"
                            >
                              🔊
                            </button>
                          )}
                        </div>
                      )}

                      {/* 用户语音消息标识 */}
                      {message.sender === 'user' && message.isVoice && (
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          marginBottom: '0.5rem',
                          fontSize: '0.75rem',
                          color: 'rgba(255, 255, 255, 0.8)'
                        }}>
                          <span>🎤</span>
                          <span>语音输入</span>
                          {message.confidence && (
                            <span style={{
                              background: 'rgba(255, 255, 255, 0.2)',
                              padding: '0.125rem 0.25rem',
                              borderRadius: '0.125rem'
                            }}>
                              {Math.round(message.confidence * 100)}%
                            </span>
                          )}
                        </div>
                      )}

                      {/* 消息内容 */}
                      <p style={{ margin: 0, lineHeight: '1.5' }}>{message.content}</p>

                      {/* 消息时间 */}
                      <div style={{
                        fontSize: '0.625rem',
                        color: 'rgba(255, 255, 255, 0.5)',
                        marginTop: '0.5rem',
                        textAlign: message.sender === 'user' ? 'right' : 'left'
                      }}>
                        {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                ))}

                {/* 流式响应显示 */}
                {isStreaming && streamingResponse && (
                  <div style={{
                    display: 'flex',
                    justifyContent: 'flex-start',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      maxWidth: '70%',
                      padding: '1rem 1.5rem',
                      borderRadius: '1rem',
                      background: 'rgba(255, 255, 255, 0.1)',
                      border: '1px solid rgba(16, 185, 129, 0.3)'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginBottom: '0.5rem',
                        fontSize: '0.875rem',
                        color: 'rgba(255, 255, 255, 0.8)'
                      }}>
                        <span>{interviewers[currentInterviewer]?.avatar}</span>
                        <span>{interviewers[currentInterviewer]?.name}</span>
                        <span className="typing-indicator" style={{
                          fontSize: '0.625rem',
                          background: 'rgba(16, 185, 129, 0.2)',
                          color: '#10b981',
                          padding: '0.125rem 0.25rem',
                          borderRadius: '0.125rem'
                        }}>
                          正在回复...
                        </span>
                      </div>
                      <p style={{ margin: 0, lineHeight: '1.5' }}>
                        {streamingResponse}
                        <span className="typing-indicator" style={{ marginLeft: '0.25rem' }}>|</span>
                      </p>
                    </div>
                  </div>
                )}

                {isLoading && !isStreaming && (
                  <div style={{
                    display: 'flex',
                    justifyContent: 'flex-start',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      padding: '1rem 1.5rem',
                      borderRadius: '1rem',
                      background: 'rgba(255, 255, 255, 0.1)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <div 
                        className="pulse-dot"
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: '#ef4444'
                        }}
                      ></div>
                      <div 
                        className="pulse-dot"
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: '#ef4444',
                          animationDelay: '0.2s'
                        }}
                      ></div>
                      <div 
                        className="pulse-dot"
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: '#ef4444',
                          animationDelay: '0.4s'
                        }}
                      ></div>
                      <span style={{ marginLeft: '0.5rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                        AI正在思考...
                      </span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* 输入区域 */}
          {interviewStarted && !interviewEnded && (
            <div style={{
              padding: '1.5rem 2rem',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              background: 'rgba(255, 255, 255, 0.02)'
            }}>
              {/* 输入区域 */}
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                {/*语音控制 */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.5rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '0.5rem',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  alignSelf: 'center',
                  height: '60px',
                  boxSizing: 'border-box'
                }}>
                  {/* Content of voice controls: toggle button, recording status, audio level */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <button
                      onClick={() => setVoiceEnabled(!voiceEnabled)}
                      style={{
                        background: voiceEnabled ? 'rgba(22, 163, 74, 0.2)' : 'rgba(107, 114, 128, 0.5)',
                        color: 'white',
                        border: 'none',
                        padding: '0.5rem',
                        borderRadius: '0.375rem',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem'
                      }}
                    >
                      {voiceEnabled ? '🔊' : '🔇'}
                    </button>
                    <span style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                      语音{voiceEnabled ? '开启' : '关闭'}
                    </span>
                  </div>

                  {/* 录音状态 */}
                  {isRecording && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '1rem' }}> 
                      <div 
                        className="pulse-dot"
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: '#ef4444'
                        }}
                      ></div>
                      <span style={{ fontSize: '0.75rem', color: '#ef4444' }}>
                        录音中 {formatRecordingTime(recordingTime)}
                      </span>
                    </div>
                  )}

                  {/* 音量指示器 */}
                  {isRecording && (
                    <div style={{
                      width: '60px',
                      height: '4px',
                      background: 'rgba(255, 255, 255, 0.2)',
                      borderRadius: '2px',
                      overflow: 'hidden',
                      marginLeft: '1rem' 
                    }}>
                      <div style={{
                        width: `${audioLevel * 100}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, #10b981, #3b82f6)',
                        transition: 'width 0.1s ease'
                      }}></div>
                    </div>
                  )}
                </div>

                {/* Textarea and its wrapper */}
                <div style={{ flex: 1, height: '60px', boxSizing: 'border-box' }}>
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={isRecording ? "正在录音中..." : "输入你的回答或使用语音回答..."}
                    disabled={isLoading || isRecording || isStreaming}
                    style={{
                      width: '100%',
                      height: '100%',
                      background: 'rgba(255, 255, 255, 0.1)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '0.75rem',
                      padding: '1rem',
                      color: 'white',
                      fontSize: '1rem',
                      resize: 'none',
                      outline: 'none',
                      fontFamily: 'inherit',
                      opacity: (isLoading || isRecording || isStreaming) ? 0.6 : 1
                    }}
                  />
                </div>

                {/* 语音录制按钮 */}
                {voiceEnabled && (
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isLoading || isStreaming}
                    className={isRecording ? 'recording-button' : ''}
                    style={{
                      background: isRecording 
                        ? 'linear-gradient(45deg, #ef4444, #dc2626)'
                        : 'linear-gradient(45deg, #10b981, #059669)',
                      color: 'white',
                      border: 'none',
                      padding: '1rem',
                      borderRadius: '0.75rem',
                      cursor: (isLoading || isStreaming) ? 'not-allowed' : 'pointer',
                      fontSize: '1.25rem',
                      minWidth: '60px',
                      height: '60px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      opacity: (isLoading || isStreaming) ? 0.6 : 1,
                      transform: isRecording ? 'scale(1.1)' : 'scale(1)',
                      transition: 'all 0.2s ease'
                    }}
                    title={isRecording ? "停止录音" : "开始录音"}
                  >
                    {isRecording ? '⏹️' : '🎤'}
                  </button>
                )}

                {/* 文字发送按钮 */}
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading || isRecording || isStreaming}
                  style={{
                    background: (!inputValue.trim() || isLoading || isRecording || isStreaming) 
                      ? 'rgba(107, 114, 128, 0.5)' 
                      : 'linear-gradient(45deg, #3b82f6, #1d4ed8)',
                    color: 'white',
                    border: 'none',
                    padding: '1rem 1.5rem',
                    borderRadius: '0.75rem',
                    cursor: (!inputValue.trim() || isLoading || isRecording || isStreaming) ? 'not-allowed' : 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    opacity: (!inputValue.trim() || isLoading || isRecording || isStreaming) ? 0.6 : 1,
                    minWidth: '80px',
                    height: '60px'
                  }}
                >
                  {isLoading || isStreaming ? '发送中...' : '发送'}
                </button>
              </div>

              {/* 提示信息 */}
              <div style={{
                display: 'flex',
                justifyContent: 'flex-end', 
                alignItems: 'center',
                marginTop: '0.5rem'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  fontSize: '0.75rem',
                  color: 'rgba(255, 255, 255, 0.5)'
                }}>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
