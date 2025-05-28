/**
 * 语音录制组件
 * 支持录音、播放、语音识别和语音合成功能
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { twMerge } from 'tailwind-merge';
import { realMCPService } from '../../services/RealMCPService';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

export interface VoiceRecorderProps {
  /** 是否启用语音功能 */
  enabled?: boolean;
  /** 是否禁用录音 */
  disabled?: boolean;
  /** 录音完成回调 */
  onRecordingComplete?: (audioBlob: Blob, transcript?: string) => void;
  /** 录音开始回调 */
  onRecordingStart?: () => void;
  /** 录音停止回调 */
  onRecordingStop?: () => void;
  /** 语音识别结果回调 */
  onTranscriptReceived?: (transcript: string, confidence: number) => void;
  /** 最大录音时长（秒） */
  maxDuration?: number;
  /** 自定义类名 */
  className?: string;
  /** 语音识别结果回调 */
  onTranscription: (text: string) => void;
  /** 音频响应回调 */
  onAudioResponse: (audioUrl: string) => void;
  /** 是否面试活动 */
  isInterviewActive: boolean;
  /** 当前面试官 */
  currentInterviewer: string;
}

/**
 * 语音录制组件
 * 提供完整的语音交互功能
 */
const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  enabled = true,
  disabled = false,
  onRecordingComplete,
  onRecordingStart,
  onRecordingStop,
  onTranscriptReceived,
  maxDuration = 120, // 默认2分钟
  className,
  onTranscription,
  onAudioResponse,
  isInterviewActive,
  currentInterviewer
}) => {
  // 状态管理
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>('');
  const [confidence, setConfidence] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const animationRef = useRef<number | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // 检查浏览器支持
  const checkBrowserSupport = useCallback(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError('您的浏览器不支持录音功能');
      return false;
    }
    if (!window.MediaRecorder) {
      setError('您的浏览器不支持MediaRecorder');
      return false;
    }
    return true;
  }, []);

  // 请求麦克风权限
  const requestPermission = useCallback(async () => {
    if (!checkBrowserSupport()) return false;

    try {
      console.log('尝试请求麦克风权限...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        } 
      });
      
      console.log('麦克风权限已获取，测试音频流');
      
      // 测试成功后关闭流
      stream.getTracks().forEach(track => track.stop());
      setHasPermission(true);
      setError(null);
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误';
      console.error(`麦克风权限请求失败: ${errorMessage}`, err);
      setHasPermission(false);
      setError(`无法访问麦克风: ${errorMessage}`);
      return false;
    }
  }, [checkBrowserSupport]);

  // 初始化音频分析器
  const initializeAudioAnalyser = useCallback((stream: MediaStream) => {
    try {
      console.log('初始化音频分析器...');
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      
      analyser.fftSize = 256;
      microphone.connect(analyser);
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      
      // 开始音频级别监测
      const updateAudioLevel = () => {
        if (!analyserRef.current) return;
        
        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteFrequencyData(dataArray);
        
        // 计算平均音量
        const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
        const normalizedLevel = Math.min(average / 128, 1);
        setAudioLevel(normalizedLevel);
        
        if (isRecording) {
          animationRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };
      
      updateAudioLevel();
      console.log('音频分析器初始化成功');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误';
      console.error(`音频分析器初始化失败: ${errorMessage}`, err);
    }
  }, [isRecording]);

  // 开始录音
  const startRecording = useCallback(async () => {
    if (!enabled || disabled || isRecording) return;
    
    try {
      // 检查权限
      if (hasPermission === null) {
        console.log('VoiceRecorder: 请求麦克风权限...');
        const granted = await requestPermission();
        if (!granted) {
          console.error('VoiceRecorder: 麦克风权限被拒绝');
          return;
        }
      } else if (hasPermission === false) {
        console.error('VoiceRecorder: 麦克风权限已被拒绝');
        setError('需要麦克风权限才能录音');
        return;
      }
      
      console.log('VoiceRecorder: 麦克风权限已获取，开始录音准备...');

      // 获取音频流
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        } 
      });

      audioStreamRef.current = stream;
      
      // 初始化音频分析器
      initializeAudioAnalyser(stream);

      // 创建MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      // 设置事件监听器
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      // 录制停止事件
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        console.log(`VoiceRecorder: 录音完成，音频大小: ${Math.round(audioBlob.size / 1024)} KB`);
        
        // 处理录音完成
        if (onRecordingComplete) {
          setIsProcessing(true);
          
          try {
            // 使用真实的 MiniMax MCP 进行语音识别
            console.log('开始使用真实 MCP 进行语音识别...');
            const result = await realMCPService.speechToText(audioBlob);
            
            console.log('真实 MCP 语音识别结果:', result);
            
            if (result.success && result.text) {
              setTranscript(result.text);
              setConfidence(result.confidence);
              
              if (onTranscriptReceived) {
                onTranscriptReceived(result.text, result.confidence);
              }
              
              onRecordingComplete(audioBlob, result.text);
            } else {
              throw new Error('语音识别失败或结果为空');
            }
          } catch (err) {
            console.error('真实 MCP 语音识别失败:', err);
            setError(`语音识别失败: ${err instanceof Error ? err.message : '未知错误'}`);
            // 仍然返回音频，但没有转录
            onRecordingComplete(audioBlob);
          } finally {
            setIsProcessing(false);
          }
        }
      };

      // 开始录音
      mediaRecorder.start(1000);
      setIsRecording(true);
      setRecordingTime(0);
      setError(null);

      // 开始计时
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          // 检查是否达到最大时长
          if (newTime >= maxDuration) {
            stopRecording();
          }
          return newTime;
        });
      }, 1000);

      if (onRecordingStart) {
        onRecordingStart();
      }

    } catch (err) {
      console.error('VoiceRecorder: 开始录音失败:', err);
      setError(`录音启动失败: ${err instanceof Error ? err.message : '未知错误'}`);
    }
  }, [enabled, disabled, isRecording, hasPermission, requestPermission, initializeAudioAnalyser, maxDuration, onRecordingStart, onRecordingComplete, onTranscriptReceived]);

  // 停止录音
  const stopRecording = useCallback(() => {
    if (!isRecording) return;

    try {
      // 停止MediaRecorder
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }

      // 停止音频流
      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop());
        audioStreamRef.current = null;
      }

      // 清理音频上下文
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }

      // 清理定时器和动画
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }

      setIsRecording(false);
      setAudioLevel(0);

      if (onRecordingStop) {
        onRecordingStop();
      }

    } catch (err) {
      console.error('停止录音失败:', err);
      setError('停止录音时出现错误');
    }
  }, [isRecording, onRecordingStop]);

  // 格式化时间显示
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 组件挂载时检查权限
  useEffect(() => {
    if (enabled) {
      checkBrowserSupport();
    }
  }, [enabled, checkBrowserSupport]);

  // 组件卸载时清理资源
  useEffect(() => {
    return () => {
      if (isRecording) {
        stopRecording();
      }
    };
  }, [isRecording, stopRecording]);

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      // 将音频转换为Base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      let binaryString = '';
      for (let i = 0; i < uint8Array.length; i++) {
        binaryString += String.fromCharCode(uint8Array[i]);
      }
      const base64Audio = btoa(binaryString);
      console.log('VoiceRecorder: 音频转换为Base64完成，长度:', base64Audio.length);
      
      console.log('开始真实MCP语音识别...');
      
      // 调用真实的MCP语音识别API
      const response = await fetch('/api/true-mcp-speech/speech-to-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio_data: base64Audio,
          format: 'webm'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '语音识别失败');
      }

      const result = await response.json();
      
      if (result.success && result.text) {
        console.log('真实MCP语音识别成功:', result.text);
        onTranscription(result.text);
        
        // 生成AI回应的语音
        await generateAIResponse(result.text);
      } else {
        throw new Error(result.error || '语音识别失败');
      }
      
    } catch (err) {
      console.error('语音处理失败:', err);
      setError(err instanceof Error ? err.message : '语音处理失败');
    } finally {
      setIsProcessing(false);
    }
  };

  const generateAIResponse = async (userText: string) => {
    try {
      console.log('生成AI回应...');
      
      // 这里应该调用AI服务生成回应文本
      // 暂时使用模拟回应
      const aiResponseText = "感谢您的回答。让我们继续下一个问题...";
      
      // 调用真实的MCP文字转语音API
      const response = await fetch('/api/true-mcp-speech/text-to-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: aiResponseText,
          interviewer_type: currentInterviewer
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '语音合成失败');
      }

      const result = await response.json();
      
      if (result.success && result.audio_url) {
        console.log('真实MCP语音合成成功:', result.audio_url);
        onAudioResponse(result.audio_url);
        await playAudio(result.audio_url);
      } else {
        throw new Error(result.error || '语音合成失败');
      }
      
    } catch (err) {
      console.error('AI回应生成失败:', err);
      setError(err instanceof Error ? err.message : 'AI回应生成失败');
    }
  };

  const playAudio = async (audioUrl: string) => {
    try {
      setIsPlaying(true);
      
      if (audioRef.current) {
        audioRef.current.pause();
      }
      
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      audio.onended = () => {
        setIsPlaying(false);
      };
      
      audio.onerror = () => {
        setIsPlaying(false);
        setError('音频播放失败');
      };
      
      await audio.play();
      
    } catch (err) {
      console.error('音频播放失败:', err);
      setIsPlaying(false);
      setError('音频播放失败');
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const getStatusText = () => {
    if (isProcessing) return '正在处理语音...';
    if (isRecording) return '正在录音中...';
    if (isPlaying) return '正在播放回应...';
    if (!isInterviewActive) return '面试未开始';
    return '点击开始录音';
  };

  const getStatusColor = () => {
    if (error) return 'text-red-500';
    if (isProcessing) return 'text-yellow-500';
    if (isRecording) return 'text-red-500';
    if (isPlaying) return 'text-blue-500';
    if (!isInterviewActive) return 'text-gray-500';
    return 'text-green-500';
  };

  if (!enabled) {
    return null;
  }

  return (
    <div className={twMerge('flex flex-col items-center space-y-4', className)}>
      {/* 错误提示 */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* 权限请求 */}
      {hasPermission === false && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-2 rounded-lg text-sm">
          <p className="mb-2">需要麦克风权限才能使用语音功能</p>
          <button
            onClick={requestPermission}
            className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600"
          >
            授权麦克风
          </button>
        </div>
      )}

      {/* 录音控制区域 */}
      {hasPermission !== false && (
        <div className="flex flex-col items-center space-y-4">
          {/* 音频可视化 */}
          <div className="relative">
            <div 
              className={twMerge(
                'w-20 h-20 rounded-full border-4 flex items-center justify-center transition-all duration-200',
                isRecording 
                  ? 'border-red-500 bg-red-50 animate-pulse' 
                  : 'border-blue-500 bg-blue-50 hover:bg-blue-100'
              )}
              style={{
                transform: isRecording ? `scale(${1 + audioLevel * 0.3})` : 'scale(1)'
              }}
            >
              {isProcessing ? (
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              ) : (
                <svg 
                  className={twMerge(
                    'w-8 h-8',
                    isRecording ? 'text-red-500' : 'text-blue-500'
                  )} 
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path 
                    fillRule="evenodd" 
                    d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" 
                    clipRule="evenodd" 
                  />
                </svg>
              )}
            </div>

            {/* 音频级别指示器 */}
            {isRecording && (
              <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                <div className="flex space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={twMerge(
                        'w-1 bg-red-500 rounded-full transition-all duration-100',
                        audioLevel > (i * 0.2) ? 'h-4' : 'h-1'
                      )}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 录音按钮 */}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={disabled || isProcessing || isPlaying}
            className={twMerge(
              'px-6 py-2 rounded-lg font-medium transition-colors duration-200',
              isRecording
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'bg-blue-500 text-white hover:bg-blue-600',
              (disabled || isProcessing || isPlaying) && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isProcessing ? '使用真实MCP识别中...' : isRecording ? '停止录音' : '开始录音'}
          </button>

          {/* 录音时间显示 */}
          {isRecording && (
            <div className="text-center">
              <div className="text-lg font-mono text-gray-700">
                {formatTime(recordingTime)}
              </div>
              <div className="text-sm text-gray-500">
                最长 {formatTime(maxDuration)}
              </div>
            </div>
          )}

          {/* 语音识别结果 */}
          {transcript && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded-lg text-sm max-w-md">
              <div className="font-medium mb-1">真实MCP识别结果:</div>
              <div>{transcript}</div>
              {confidence > 0 && (
                <div className="text-xs mt-1 text-green-600">
                  置信度: {Math.round(confidence * 100)}%
                </div>
              )}
            </div>
          )}

          {/* 使用提示 */}
          {!isRecording && !transcript && (
            <div className="text-center text-gray-500 text-sm max-w-md">
              <p>点击开始录音，系统会使用真实的MiniMax MCP进行语音识别</p>
              <p className="mt-1">支持中文和英文识别</p>
            </div>
          )}
        </div>
      )}

      {/* 音频控制区域 */}
      {hasPermission !== false && (
        <div className="flex items-center space-x-4">
          {/* 音频控制按钮 */}
          <button
            onClick={isPlaying ? stopAudio : undefined}
            disabled={!isPlaying}
            className={twMerge(
              'p-4 rounded-full transition-all duration-200',
              isPlaying 
                ? 'bg-orange-500 hover:bg-orange-600 text-white shadow-lg' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            )}
          >
            {isPlaying ? (
              <VolumeX className="w-6 h-6" />
            ) : (
              <Volume2 className="w-6 h-6" />
            )}
          </button>
        </div>
      )}

      {/* 状态显示 */}
      <div className="text-center">
        <p className={`text-sm font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </p>
        {error && (
          <p className="text-xs text-red-500 mt-1">
            {error}
          </p>
        )}
        <p className="text-xs text-gray-500 mt-2">
          使用真实MCP识别 • 当前面试官: {currentInterviewer}
        </p>
      </div>
    </div>
  );
};

export default VoiceRecorder; 