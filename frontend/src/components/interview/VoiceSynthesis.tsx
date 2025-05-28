/**
 * 语音合成组件
 * 支持将文本转换为语音并播放
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { twMerge } from 'tailwind-merge';

export interface VoiceSynthesisProps {
  /** 要播放的文本 */
  text: string;
  /** 是否自动播放 */
  autoPlay?: boolean;
  /** 语音语言 */
  language?: string;
  /** 语音速度 (0.1-10) */
  rate?: number;
  /** 语音音调 (0-2) */
  pitch?: number;
  /** 语音音量 (0-1) */
  volume?: number;
  /** 播放开始回调 */
  onPlayStart?: () => void;
  /** 播放结束回调 */
  onPlayEnd?: () => void;
  /** 播放错误回调 */
  onPlayError?: (error: string) => void;
  /** 自定义类名 */
  className?: string;
  /** 是否显示控制按钮 */
  showControls?: boolean;
}

/**
 * 语音合成组件
 * 提供文本转语音功能
 */
const VoiceSynthesis: React.FC<VoiceSynthesisProps> = ({
  text,
  autoPlay = false,
  language = 'zh-CN',
  rate = 1,
  pitch = 1,
  volume = 1,
  onPlayStart,
  onPlayEnd,
  onPlayError,
  className,
  showControls = true
}) => {
  // 状态管理
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [isSupported, setIsSupported] = useState(false);

  // Refs
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const progressTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 检查浏览器支持
  const checkBrowserSupport = useCallback(() => {
    if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
      setError('您的浏览器不支持语音合成功能');
      setIsSupported(false);
      return false;
    }
    setIsSupported(true);
    return true;
  }, []);

  // 获取可用语音
  const loadVoices = useCallback(() => {
    if (!window.speechSynthesis) return;

    const availableVoices = window.speechSynthesis.getVoices();
    setVoices(availableVoices);

    // 选择默认语音
    const preferredVoice = availableVoices.find(voice => 
      voice.lang.startsWith(language.split('-')[0]) && voice.localService
    ) || availableVoices.find(voice => 
      voice.lang.startsWith(language.split('-')[0])
    ) || availableVoices[0];

    setSelectedVoice(preferredVoice || null);
  }, [language]);

  // 创建语音合成实例
  const createUtterance = useCallback((textToSpeak: string) => {
    if (!window.SpeechSynthesisUtterance) return null;

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    
    // 设置语音参数
    utterance.lang = language;
    utterance.rate = Math.max(0.1, Math.min(10, rate));
    utterance.pitch = Math.max(0, Math.min(2, pitch));
    utterance.volume = Math.max(0, Math.min(1, volume));
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    // 设置事件监听器
    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
      setError(null);
      setCurrentTime(0);
      
      // 估算播放时长（基于文本长度和语速）
      const estimatedDuration = (textToSpeak.length / 10) / rate;
      setDuration(estimatedDuration);
      
      // 开始进度更新
      startProgressTracking(estimatedDuration);
      
      if (onPlayStart) {
        onPlayStart();
      }
    };

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
      setProgress(100);
      setCurrentTime(duration);
      stopProgressTracking();
      
      if (onPlayEnd) {
        onPlayEnd();
      }
    };

    utterance.onerror = (event) => {
      const errorMessage = `语音播放失败: ${event.error}`;
      setError(errorMessage);
      setIsPlaying(false);
      setIsPaused(false);
      stopProgressTracking();
      
      if (onPlayError) {
        onPlayError(errorMessage);
      }
    };

    utterance.onpause = () => {
      setIsPaused(true);
      stopProgressTracking();
    };

    utterance.onresume = () => {
      setIsPaused(false);
      startProgressTracking(duration - currentTime);
    };

    return utterance;
  }, [language, rate, pitch, volume, selectedVoice, duration, currentTime, onPlayStart, onPlayEnd, onPlayError]);

  // 开始进度跟踪
  const startProgressTracking = useCallback((totalDuration: number) => {
    stopProgressTracking();
    
    const startTime = Date.now();
    const updateInterval = 100; // 100ms更新一次
    
    progressTimerRef.current = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      const progressPercent = Math.min((elapsed / totalDuration) * 100, 100);
      
      setProgress(progressPercent);
      setCurrentTime(elapsed);
      
      if (progressPercent >= 100) {
        stopProgressTracking();
      }
    }, updateInterval);
  }, []);

  // 停止进度跟踪
  const stopProgressTracking = useCallback(() => {
    if (progressTimerRef.current) {
      clearInterval(progressTimerRef.current);
      progressTimerRef.current = null;
    }
  }, []);

  // 播放语音
  const playText = useCallback(async (textToSpeak?: string) => {
    if (!isSupported) {
      setError('语音合成功能不可用');
      return;
    }

    const content = textToSpeak || text;
    if (!content.trim()) {
      setError('没有可播放的文本内容');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // 停止当前播放
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
      }

      // 创建新的语音合成实例
      const utterance = createUtterance(content);
      if (!utterance) {
        throw new Error('无法创建语音合成实例');
      }

      utteranceRef.current = utterance;
      
      // 开始播放
      window.speechSynthesis.speak(utterance);
      
    } catch (err) {
      const errorMessage = `播放失败: ${err instanceof Error ? err.message : '未知错误'}`;
      setError(errorMessage);
      if (onPlayError) {
        onPlayError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  }, [isSupported, text, createUtterance, onPlayError]);

  // 暂停播放
  const pausePlayback = useCallback(() => {
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
    }
  }, []);

  // 恢复播放
  const resumePlayback = useCallback(() => {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
  }, []);

  // 停止播放
  const stopPlayback = useCallback(() => {
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }
    setIsPlaying(false);
    setIsPaused(false);
    setProgress(0);
    setCurrentTime(0);
    stopProgressTracking();
  }, [stopProgressTracking]);

  // 格式化时间显示
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 组件挂载时初始化
  useEffect(() => {
    checkBrowserSupport();
    loadVoices();

    // 监听语音列表变化
    const handleVoicesChanged = () => {
      loadVoices();
    };

    if (window.speechSynthesis) {
      window.speechSynthesis.addEventListener('voiceschanged', handleVoicesChanged);
      
      return () => {
        window.speechSynthesis.removeEventListener('voiceschanged', handleVoicesChanged);
      };
    }
  }, [checkBrowserSupport, loadVoices]);

  // 自动播放
  useEffect(() => {
    if (autoPlay && text && isSupported && !isPlaying) {
      playText();
    }
  }, [autoPlay, text, isSupported, isPlaying, playText]);

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      stopPlayback();
    };
  }, [stopPlayback]);

  if (!isSupported) {
    return (
      <div className={twMerge('bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-2 rounded-lg text-sm', className)}>
        您的浏览器不支持语音合成功能
      </div>
    );
  }

  return (
    <div className={twMerge('flex flex-col space-y-3', className)}>
      {/* 错误提示 */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* 控制按钮 */}
      {showControls && (
        <div className="flex items-center space-x-3">
          {/* 播放/暂停按钮 */}
          <button
            onClick={() => {
              if (isPlaying) {
                if (isPaused) {
                  resumePlayback();
                } else {
                  pausePlayback();
                }
              } else {
                playText();
              }
            }}
            disabled={isLoading || !text.trim()}
            className={twMerge(
              'flex items-center justify-center w-10 h-10 rounded-full transition-colors duration-200',
              isPlaying && !isPaused
                ? 'bg-orange-500 text-white hover:bg-orange-600'
                : 'bg-green-500 text-white hover:bg-green-600',
              (isLoading || !text.trim()) && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : isPlaying && !isPaused ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
            )}
          </button>

          {/* 停止按钮 */}
          <button
            onClick={stopPlayback}
            disabled={!isPlaying}
            className={twMerge(
              'flex items-center justify-center w-10 h-10 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors duration-200',
              !isPlaying && 'opacity-50 cursor-not-allowed'
            )}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
            </svg>
          </button>

          {/* 播放状态指示 */}
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            {isPlaying && (
              <>
                <span className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-1"></div>
                  {isPaused ? '已暂停' : '播放中'}
                </span>
                <span>
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              </>
            )}
          </div>
        </div>
      )}

      {/* 进度条 */}
      {isPlaying && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-200"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}

      {/* 语音设置 */}
      {showControls && voices.length > 0 && (
        <div className="flex flex-wrap items-center gap-4 text-sm">
          {/* 语音选择 */}
          <div className="flex items-center space-x-2">
            <label className="text-gray-600">语音:</label>
            <select
              value={selectedVoice?.name || ''}
              onChange={(e) => {
                const voice = voices.find(v => v.name === e.target.value);
                setSelectedVoice(voice || null);
              }}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              {voices
                .filter(voice => voice.lang.startsWith(language.split('-')[0]))
                .map(voice => (
                  <option key={voice.name} value={voice.name}>
                    {voice.name} ({voice.lang})
                  </option>
                ))}
            </select>
          </div>

          {/* 语速控制 */}
          <div className="flex items-center space-x-2">
            <label className="text-gray-600">语速:</label>
            <span className="text-xs text-gray-500">{rate.toFixed(1)}x</span>
          </div>
        </div>
      )}

      {/* 文本预览 */}
      {text && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700 max-h-32 overflow-y-auto">
          <div className="font-medium text-gray-800 mb-1">播放内容:</div>
          <div className="whitespace-pre-wrap">{text}</div>
        </div>
      )}
    </div>
  );
};

export default VoiceSynthesis; 