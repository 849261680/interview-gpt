/**
 * 聊天消息组件
 * 用于展示面试过程中的对话消息
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

export interface ChatMessageProps {
  /** 消息内容 */
  content: string;
  /** 发送者类型: user, interviewer, system */
  senderType: 'user' | 'interviewer' | 'system';
  /** 面试官ID (仅当senderType为interviewer时) */
  interviewerId?: string;
  /** 面试官姓名 (仅当senderType为interviewer时) */
  interviewerName?: string;
  /** 消息发送时间 */
  timestamp: Date;
  /** 是否显示发送时间 */
  showTime?: boolean;
  /** 自定义类名 */
  className?: string;
  /** 音频播放功能 */
  onPlayAudio?: () => void;
  /** 音频URL */
  audioUrl?: string;
}

/**
 * 聊天消息组件
 * 根据发送者类型显示不同样式的消息气泡
 */
const ChatMessage: React.FC<ChatMessageProps> = ({
  content,
  senderType,
  interviewerId,
  interviewerName,
  timestamp,
  showTime = true,
  className,
  onPlayAudio,
  audioUrl
}) => {
  // 根据发送者类型设置不同的样式
  const isUser = senderType === 'user';
  const isSystem = senderType === 'system';
  
  // 获取面试官名称和头像
  const getInterviewerInfo = () => {
    if (interviewerName) return { name: interviewerName, avatar: '/images/interviewers/default.png' };
    
    // 默认面试官信息
    switch (interviewerId) {
      case 'technical':
        return { name: '张工', avatar: '/images/interviewers/technical.png' };
      case 'hr':
        return { name: '李经理', avatar: '/images/interviewers/hr.png' };
      case 'behavioral':
        return { name: '王总', avatar: '/images/interviewers/behavioral.png' };
      default:
        return { name: '面试官', avatar: '/images/interviewers/default.png' };
    }
  };
  
  // 系统消息样式
  if (isSystem) {
    return (
      <div className={twMerge('flex justify-center my-4', className)}>
        <div className="bg-gray-100 text-gray-600 rounded-lg px-4 py-2 max-w-md text-sm">
          <p>{content}</p>
          {showTime && (
            <p className="text-xs text-gray-500 mt-1">
              {formatDistanceToNow(timestamp, { addSuffix: true, locale: zhCN })}
            </p>
          )}
        </div>
      </div>
    );
  }
  
  // 获取面试官信息
  const { name, avatar } = isUser ? { name: '您', avatar: '/images/user-avatar.png' } : getInterviewerInfo();
  
  return (
    <div className={twMerge(
      'flex mb-4',
      isUser ? 'justify-end' : 'justify-start',
      className
    )}>
      {/* 非用户消息显示头像 */}
      {!isUser && (
        <div className="flex-shrink-0 mr-3">
          <img
            className="h-10 w-10 rounded-full bg-gray-200"
            src={avatar}
            alt={`${name}头像`}
          />
        </div>
      )}
      
      <div className={twMerge(
        'flex flex-col',
        isUser ? 'items-end' : 'items-start'
      )}>
        {/* 发送者名称 */}
        <div className="mb-1 text-sm font-medium text-gray-700">
          {name}
        </div>
        
        {/* 消息气泡 */}
        <div className={twMerge(
          'px-4 py-2 rounded-lg max-w-md',
          isUser 
            ? 'bg-blue-500 text-white rounded-br-none' 
            : 'bg-gray-100 text-gray-800 rounded-bl-none'
        )}>
          <p className="whitespace-pre-wrap break-words">{content}</p>
          
          {/* 音频播放按钮 */}
          {!isUser && audioUrl && (
            <div className="mt-2">
              <button
                onClick={onPlayAudio}
                className="flex items-center text-xs text-blue-600 hover:text-blue-800"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                收听回答
              </button>
              <audio src={audioUrl} className="hidden" />
            </div>
          )}
        </div>
        
        {/* 时间戳 */}
        {showTime && (
          <div className="mt-1 text-xs text-gray-500">
            {formatDistanceToNow(timestamp, { addSuffix: true, locale: zhCN })}
          </div>
        )}
      </div>
      
      {/* 用户消息显示头像 */}
      {isUser && (
        <div className="flex-shrink-0 ml-3">
          <img
            className="h-10 w-10 rounded-full bg-gray-200"
            src={avatar}
            alt="用户头像"
          />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
