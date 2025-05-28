/**
 * 面试会话Hook
 * 管理面试会话状态、消息和面试官轮换
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/router';
import interviewSocketService, { 
  InterviewMessage, 
  InterviewStatus,
  InterviewStageUpdate
} from '../services/InterviewSocketService';

// 面试阶段类型
export type InterviewStage = 'technical' | 'hr' | 'behavioral' | 'feedback';

// 面试官阶段类型 (不包含feedback)
type InterviewerStage = 'technical' | 'hr' | 'behavioral';

// 面试会话状态
interface InterviewSessionState {
  // 面试状态
  status: 'connecting' | 'active' | 'completed' | 'cancelled' | 'error';
  // 消息列表
  messages: InterviewMessage[];
  // 当前面试阶段
  currentStage: InterviewStage;
  // 当前活跃面试官ID
  activeInterviewerId?: string;
  // 面试进度百分比
  progressPercent: number;
  // 是否正在发送消息
  isSending: boolean;
  // 是否可以进入下一阶段
  canAdvanceStage: boolean;
  // 错误信息
  error?: string;
}

/**
 * 面试会话Hook
 * 管理面试的整个生命周期，包括状态、消息和控制
 * 
 * @param interviewId 面试ID
 */
export function useInterviewSession(interviewId: number) {
  const router = useRouter();
  
  // 面试会话状态
  const [state, setState] = useState<InterviewSessionState>({
    status: 'connecting',
    messages: [],
    currentStage: 'technical',
    progressPercent: 0,
    isSending: false,
    canAdvanceStage: false
  });
  
  // 面试信息
  const [interviewInfo, setInterviewInfo] = useState<InterviewStatus | null>(null);
  
  // 计算阶段消息数量的引用
  const stageMessageCountRef = useRef<Record<InterviewerStage, number>>({
    technical: 0,
    hr: 0,
    behavioral: 0
  });
  
  // 获取面试信息
  const fetchInterviewInfo = useCallback(async () => {
    try {
      const response = await fetch(`/api/interview-process/${interviewId}/status`);
      if (!response.ok) {
        throw new Error(`获取面试状态失败: ${response.statusText}`);
      }
      
      const data = await response.json();
      setInterviewInfo(data);
      
      // 更新状态
      setState(prev => ({
        ...prev,
        status: data.status === 'active' ? 'active' : data.status,
        activeInterviewerId: data.active_interviewer
      }));
      
    } catch (error) {
      console.error('获取面试信息失败:', error);
      setState(prev => ({
        ...prev,
        error: '获取面试信息失败'
      }));
    }
  }, [interviewId]);
  
  // 发送消息
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || state.isSending) return;
    
    setState(prev => ({ ...prev, isSending: true }));
    
    try {
      // 先添加用户消息到本地状态
      const userMessage: InterviewMessage = {
        id: -1, // 临时ID
        content,
        sender_type: 'user',
        timestamp: new Date().toISOString()
      };
      
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage]
      }));
      
      // 通过WebSocket发送消息
      interviewSocketService.sendMessage(content);
      
    } catch (error) {
      console.error('发送消息失败:', error);
      setState(prev => ({
        ...prev,
        error: '发送消息失败'
      }));
    } finally {
      setState(prev => ({ ...prev, isSending: false }));
    }
  }, [state.isSending]);
  
  // 进入下一阶段
  const advanceToNextStage = useCallback(async () => {
    if (!state.canAdvanceStage) return;
    
    try {
      interviewSocketService.requestNextStage();
    } catch (error) {
      console.error('切换面试阶段失败:', error);
      setState(prev => ({
        ...prev,
        error: '切换面试阶段失败'
      }));
    }
  }, [state.canAdvanceStage]);
  
  // 结束面试
  const endInterview = useCallback(async () => {
    try {
      interviewSocketService.requestEndInterview();
    } catch (error) {
      console.error('结束面试失败:', error);
      setState(prev => ({
        ...prev,
        error: '结束面试失败'
      }));
    }
  }, []);
  
  // 计算面试进度
  const calculateProgress = useCallback(() => {
    const { technical, hr, behavioral } = stageMessageCountRef.current;
    const totalStages = 4; // 技术、HR、行为、反馈四个阶段
    
    // 根据当前阶段和消息数量计算进度
    let stageProgress = 0;
    let currentStage: InterviewStage = 'technical';
    
    // 检查是否已经进入反馈阶段
    if (state.status === 'completed') {
      stageProgress = 3; // 已完成所有面试官阶段
      currentStage = 'feedback';
    } else if (behavioral > 0) {
      stageProgress = 2; // 已完成技术和HR阶段
      currentStage = 'behavioral';
    } else if (hr > 0) {
      stageProgress = 1; // 已完成技术阶段
      currentStage = 'hr';
    } else {
      stageProgress = 0;
      currentStage = 'technical';
    }
    
    // 每个阶段的权重
    const stageWeight = 100 / totalStages;
    
    // 计算总进度百分比
    const progressPercent = Math.min(
      Math.round(stageProgress * stageWeight),
      100
    );
    
    return { progressPercent, currentStage };
  }, [state.status]);
  
  // 更新消息统计
  const updateMessageStats = useCallback((messages: InterviewMessage[]) => {
    // 重置计数
    const stageCount: Record<InterviewerStage, number> = {
      technical: 0,
      hr: 0,
      behavioral: 0
    };
    
    // 统计各阶段面试官消息
    messages.forEach(msg => {
      if (msg.sender_type === 'interviewer' && msg.interviewer_id) {
        const interviewerId = msg.interviewer_id as InterviewerStage;
        if (interviewerId in stageCount) {
          stageCount[interviewerId]++;
        }
      }
    });
    
    // 更新引用
    stageMessageCountRef.current = stageCount;
    
    // 计算进度
    const { progressPercent, currentStage } = calculateProgress();
    
    // 更新状态
    setState(prev => {
      const isInterviewerStage = currentStage !== 'feedback';
      let canAdvance = false;
      
      if (isInterviewerStage && state.status === 'active') {
        // 只有在面试官阶段才检查消息数量
        canAdvance = stageCount[currentStage as InterviewerStage] >= 4;
      }
      
      return {
        ...prev,
        progressPercent,
        currentStage,
        canAdvanceStage: canAdvance
      };
    });
  }, [calculateProgress, state.status]);
  
  // 初始化WebSocket连接
  useEffect(() => {
    // 连接WebSocket
    interviewSocketService.connect(interviewId);
    
    // 获取面试信息
    fetchInterviewInfo();
    
    // 监听WebSocket事件
    const handleConnected = () => {
      console.log('面试WebSocket连接已建立');
    };
    
    const handleDisconnected = () => {
      console.log('面试WebSocket连接已断开');
      setState(prev => ({ 
        ...prev, 
        error: '与服务器的连接已断开，请刷新页面重试'
      }));
    };
    
    const handleHistory = (messages: InterviewMessage[]) => {
      setState(prev => ({ ...prev, messages }));
      updateMessageStats(messages);
    };
    
    const handleMessage = (message: InterviewMessage) => {
      setState(prev => {
        const newMessages = [...prev.messages];
        // 检查是否存在临时消息，替换它
        const tempIndex = newMessages.findIndex(m => m.id === -1);
        if (tempIndex >= 0) {
          newMessages.splice(tempIndex, 1);
        }
        
        // 添加新消息
        const updatedMessages = [...newMessages, message];
        
        // 更新统计
        updateMessageStats(updatedMessages);
        
        return {
          ...prev,
          messages: updatedMessages,
          activeInterviewerId: message.interviewer_id || prev.activeInterviewerId
        };
      });
    };
    
    const handleStatus = (status: InterviewStatus) => {
      setInterviewInfo(status);
      setState(prev => ({
        ...prev,
        status: status.status === 'active' ? 'active' : status.status,
        activeInterviewerId: status.active_interviewer
      }));
    };
    
    const handleNewStage = (data: InterviewStageUpdate) => {
      // 添加新消息
      handleMessage(data.message);
      
      // 更新阶段
      setState(prev => ({
        ...prev,
        currentStage: data.stage as InterviewStage,
        canAdvanceStage: false
      }));
    };
    
    const handleInterviewEnded = (data: any) => {
      setState(prev => ({
        ...prev,
        status: 'completed',
        progressPercent: 100,
        canAdvanceStage: false
      }));
      
      // 延时几秒后跳转到反馈页面
      setTimeout(() => {
        router.push(`/feedback/${interviewId}`);
      }, 3000);
    };
    
    const handleError = (error: any) => {
      console.error('面试WebSocket错误:', error);
      setState(prev => ({
        ...prev,
        error: '连接错误: ' + (error.message || '未知错误')
      }));
    };
    
    // 注册事件监听
    interviewSocketService.on('connected', handleConnected);
    interviewSocketService.on('disconnected', handleDisconnected);
    interviewSocketService.on('history', handleHistory);
    interviewSocketService.on('message', handleMessage);
    interviewSocketService.on('status', handleStatus);
    interviewSocketService.on('new_stage', handleNewStage);
    interviewSocketService.on('interview_ended', handleInterviewEnded);
    interviewSocketService.on('socket_error', handleError);
    
    // 清理函数
    return () => {
      interviewSocketService.disconnect();
      interviewSocketService.removeListener('connected', handleConnected);
      interviewSocketService.removeListener('disconnected', handleDisconnected);
      interviewSocketService.removeListener('history', handleHistory);
      interviewSocketService.removeListener('message', handleMessage);
      interviewSocketService.removeListener('status', handleStatus);
      interviewSocketService.removeListener('new_stage', handleNewStage);
      interviewSocketService.removeListener('interview_ended', handleInterviewEnded);
      interviewSocketService.removeListener('socket_error', handleError);
    };
  }, [interviewId, fetchInterviewInfo, updateMessageStats]);
  
  // 返回状态和方法
  return {
    // 状态
    status: state.status,
    messages: state.messages,
    currentStage: state.currentStage,
    activeInterviewerId: state.activeInterviewerId,
    progressPercent: state.progressPercent,
    isSending: state.isSending,
    canAdvanceStage: state.canAdvanceStage,
    error: state.error,
    interviewInfo,
    
    // 方法
    sendMessage,
    advanceToNextStage,
    endInterview
  };
}

export default useInterviewSession;
