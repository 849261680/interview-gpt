/**
 * 音频录制组件
 * 用于在面试过程中录制用户语音回答
 */
import React, { useState, useEffect, useRef } from 'react';
import { twMerge } from 'tailwind-merge';
import Button from '../common/Button';

export interface AudioRecorderProps {
  /** 录音完成后的回调函数 */
  onRecordingComplete: (audioBlob: Blob) => void;
  /** 取消录音的回调函数 */
  onCancel?: () => void;
  /** 自定义类名 */
  className?: string;
  /** 最大录音时长（秒） */
  maxDuration?: number;
  /** 是否自动开始录音 */
  autoStart?: boolean;
}

/**
 * 音频录制组件
 * 提供录音、暂停、继续和取消功能
 */
const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  onCancel,
  className,
  maxDuration = 120, // 默认最大录音时长2分钟
  autoStart = false
}) => {
  // 状态
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  
  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // 格式化时间
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };
  
  // 开始录音
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      
      mediaRecorderRef.current.addEventListener('dataavailable', (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      });
      
      mediaRecorderRef.current.addEventListener('stop', () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
        
        // 回调函数
        onRecordingComplete(audioBlob);
        
        // 释放媒体流
        stream.getTracks().forEach(track => track.stop());
      });
      
      // 开始录音
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setIsPaused(false);
      audioChunksRef.current = [];
      
      // 计时器
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          if (prev >= maxDuration) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (error) {
      console.error('无法访问麦克风:', error);
      alert('无法访问麦克风，请检查浏览器权限设置。');
    }
  };
  
  // 暂停录音
  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      
      // 暂停计时器
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };
  
  // 继续录音
  const resumeRecording = () => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      
      // 继续计时器
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          if (prev >= maxDuration) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    }
  };
  
  // 停止录音
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      
      // 停止计时器
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };
  
  // 取消录音
  const cancelRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      
      // 清理资源
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
      
      // 重置状态
      setIsRecording(false);
      setIsPaused(false);
      setDuration(0);
      setAudioURL(null);
      audioChunksRef.current = [];
      
      // 停止计时器
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      // 回调函数
      if (onCancel) {
        onCancel();
      }
    }
  };
  
  // 自动开始录音
  useEffect(() => {
    if (autoStart) {
      startRecording();
    }
    
    // 组件卸载时清理资源
    return () => {
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
        
        if (mediaRecorderRef.current.stream) {
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
      }
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      
      if (audioURL) {
        URL.revokeObjectURL(audioURL);
      }
    };
  }, [autoStart]);
  
  return (
    <div className={twMerge('bg-white p-4 rounded-lg border border-gray-200', className)}>
      {/* 录音状态和计时器 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          {isRecording && (
            <span className="relative flex h-3 w-3 mr-2">
              {!isPaused && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              )}
              <span className={twMerge(
                'relative inline-flex rounded-full h-3 w-3',
                isPaused ? 'bg-yellow-500' : 'bg-red-500'
              )}></span>
            </span>
          )}
          <span className="text-sm font-medium">
            {isRecording 
              ? (isPaused ? '录音已暂停' : '正在录音...') 
              : (audioURL ? '录音完成' : '准备录音')}
          </span>
        </div>
        
        <div className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
          {formatTime(duration)} / {formatTime(maxDuration)}
        </div>
      </div>
      
      {/* 进度条 */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div 
          className={twMerge(
            'h-2 rounded-full',
            isPaused ? 'bg-yellow-500' : 'bg-red-500'
          )}
          style={{ width: `${(duration / maxDuration) * 100}%` }}
        ></div>
      </div>
      
      {/* 控制按钮 */}
      <div className="flex space-x-2">
        {!isRecording && !audioURL && (
          <Button 
            onClick={startRecording}
            variant="primary"
            fullWidth
            leftIcon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
            }
          >
            开始录音
          </Button>
        )}
        
        {isRecording && !isPaused && (
          <>
            <Button 
              onClick={pauseRecording}
              variant="outline"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              }
            >
              暂停
            </Button>
            
            <Button 
              onClick={stopRecording}
              variant="primary"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                </svg>
              }
            >
              完成
            </Button>
            
            <Button 
              onClick={cancelRecording}
              variant="danger"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              }
            >
              取消
            </Button>
          </>
        )}
        
        {isRecording && isPaused && (
          <>
            <Button 
              onClick={resumeRecording}
              variant="primary"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
              }
            >
              继续
            </Button>
            
            <Button 
              onClick={stopRecording}
              variant="primary"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                </svg>
              }
            >
              完成
            </Button>
            
            <Button 
              onClick={cancelRecording}
              variant="danger"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              }
            >
              取消
            </Button>
          </>
        )}
        
        {audioURL && (
          <>
            <Button 
              onClick={() => setAudioURL(null)}
              variant="outline"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              }
            >
              清除录音
            </Button>
            
            <Button 
              onClick={startRecording}
              variant="primary"
              leftIcon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
              }
            >
              重新录音
            </Button>
          </>
        )}
      </div>
      
      {/* 音频预览 */}
      {audioURL && (
        <div className="mt-4">
          <audio src={audioURL} controls className="w-full" />
        </div>
      )}
    </div>
  );
};

export default AudioRecorder;
