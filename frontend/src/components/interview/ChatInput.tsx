/**
 * 聊天输入组件
 * 用于用户在面试中输入回答，支持文本和语音输入
 */
import React, { useState, useRef } from 'react';
import { twMerge } from 'tailwind-merge';
import Button from '../common/Button';

export interface ChatInputProps {
  /** 发送消息的回调函数 */
  onSendMessage: (message: string) => void;
  /** 开始录音的回调函数 */
  onStartRecording?: () => void;
  /** 停止录音的回调函数 */
  onStopRecording?: (audioBlob: Blob) => void;
  /** 是否禁用输入 */
  disabled?: boolean;
  /** 占位文本 */
  placeholder?: string;
  /** 自定义类名 */
  className?: string;
  /** 是否显示录音按钮 */
  showVoiceInput?: boolean;
  /** 是否正在录音 */
  isRecording?: boolean;
}

/**
 * 聊天输入组件
 * 支持文本输入和语音输入两种模式
 */
const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onStartRecording,
  onStopRecording,
  disabled = false,
  placeholder = '请输入您的回答...',
  className,
  showVoiceInput = true,
  isRecording = false
}) => {
  // 状态
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 自动调整文本框高度
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  };

  // 处理文本变化
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    adjustTextareaHeight();
  };

  // 处理按键事件
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Shift+Enter 添加换行，Enter 发送消息
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 发送消息
  const handleSendMessage = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      // 重置文本框高度
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  // 处理录音按钮点击
  const handleVoiceButtonClick = () => {
    if (isRecording) {
      // 停止录音
      if (onStopRecording) {
        // 这里假设我们已经有了 audioBlob，实际中需要从录音 API 获取
        const dummyBlob = new Blob(['dummy'], { type: 'audio/webm' });
        onStopRecording(dummyBlob);
      }
    } else {
      // 开始录音
      if (onStartRecording) {
        onStartRecording();
      }
    }
  };

  return (
    <div className={twMerge('bg-white border-t border-gray-200 p-4', className)}>
      <div className="flex items-end space-x-2">
        {/* 文本输入区域 */}
        <div className="flex-grow relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isRecording}
            className={twMerge(
              'w-full border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none',
              'min-h-[40px] max-h-[200px] overflow-y-auto',
              disabled ? 'bg-gray-100 cursor-not-allowed' : '',
              isRecording ? 'bg-gray-100' : ''
            )}
            rows={1}
          />
        </div>

        {/* 录音按钮 */}
        {showVoiceInput && (
          <Button
            type="button"
            variant={isRecording ? 'danger' : 'outline'}
            onClick={handleVoiceButtonClick}
            disabled={disabled}
            aria-label={isRecording ? '停止录音' : '开始录音'}
            className="flex-shrink-0"
          >
            {isRecording ? (
              // 停止图标
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
              </svg>
            ) : (
              // 麦克风图标
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
            )}
          </Button>
        )}

        {/* 发送按钮 */}
        <Button
          type="button"
          onClick={handleSendMessage}
          disabled={disabled || !message.trim() || isRecording}
          aria-label="发送消息"
          className="flex-shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
        </Button>
      </div>

      {/* 录音状态提示 */}
      {isRecording && (
        <div className="mt-2 text-sm text-red-600 flex items-center">
          <span className="relative flex h-3 w-3 mr-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          正在录音中，请对着麦克风说话...
        </div>
      )}

      {/* 辅助提示 */}
      <div className="mt-1 text-xs text-gray-500">
        按 Enter 发送消息，Shift + Enter 换行
      </div>
    </div>
  );
};

export default ChatInput;
