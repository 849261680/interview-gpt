/**
 * MiniMax TTS 测试页面
 * 用于测试和验证MiniMax文字转语音功能
 */

import React, { useState, useRef } from 'react';
import { createMinimaxService, type MinimaxConfig } from '../services/MinimaxMCPService';

const TestMinimaxTTS: React.FC = () => {
  const [text, setText] = useState('你好，这是MiniMax TTS测试。欢迎使用AI面试系统！');
  const [voice, setVoice] = useState('female-tianmei');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // 可用的语音选项
  const voiceOptions = [
    { id: 'female-tianmei', name: '甜美女性音色' },
    { id: 'female-shaonv', name: '少女音色' },
    { id: 'female-yujie', name: '御姐音色' },
    { id: 'female-chengshu', name: '成熟女性音色' },
    { id: 'male-qn-qingse', name: '青涩青年音色' },
    { id: 'male-qn-jingying', name: '精英青年音色' },
    { id: 'male-qn-badao', name: '霸道青年音色' },
    { id: 'male-qn-daxuesheng', name: '青年大学生音色' }
  ];

  const handleTTSTest = async () => {
    if (!text.trim()) {
      setError('请输入要转换的文本');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setAudioUrl(null);

    try {
      // 创建MiniMax服务实例
      const config: MinimaxConfig = {
        apiKey: 'test-key', // 测试用，实际会被后端忽略
        groupId: 'test-group'
      };
      const minimaxService = createMinimaxService(config);

      console.log('开始TTS测试...');
      
      // 调用TTS服务
      const ttsResult = await minimaxService.textToSpeech(text, voice, {
        speed: 1.0,
        volume: 1.0,
        pitch: 0,
        audioFormat: 'mp3'
      });

      console.log('TTS结果:', ttsResult);
      
      setResult(ttsResult);
      setAudioUrl(ttsResult.audioUrl);
      
      // 自动播放音频
      if (ttsResult.audioUrl && audioRef.current) {
        audioRef.current.src = ttsResult.audioUrl;
        audioRef.current.load();
      }

    } catch (err) {
      console.error('TTS测试失败:', err);
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlayAudio = () => {
    if (audioRef.current) {
      audioRef.current.play().catch(err => {
        console.error('播放音频失败:', err);
        setError('播放音频失败: ' + err.message);
      });
    }
  };

  const handleDirectAPITest = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/api/minimax-tts/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          voice_id: voice,
          service: 'minimax'
        })
      });

      const result = await response.json();
      console.log('直接API测试结果:', result);
      
      setResult(result);
      
      if (result.success && result.audio_url) {
        setAudioUrl(result.audio_url);
        if (audioRef.current) {
          audioRef.current.src = result.audio_url;
          audioRef.current.load();
        }
      }

    } catch (err) {
      console.error('直接API测试失败:', err);
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetVoices = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/api/minimax-tts/voices?service=minimax');
      const result = await response.json();
      console.log('语音列表:', result);
      setResult(result);
    } catch (err) {
      console.error('获取语音列表失败:', err);
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInterviewStyleTest = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // 模拟面试页面中的逻辑
      console.log('[面试风格测试] 开始测试...');
      
      // 导入配置函数
      const { getMinimaxConfig, validateConfig, getInterviewerVoice, ttsConfig } = await import('../config/minimax.config');
      
      // 获取配置
      const config = getMinimaxConfig();
      console.log('[面试风格测试] 获取配置:', { ...config, apiKey: config.apiKey ? '***已配置***' : '未配置' });
      
      // 验证配置
      if (!validateConfig(config)) {
        throw new Error('MiniMax配置无效，请检查API密钥和Group ID');
      }
      
      console.log('[面试风格测试] 配置验证通过，开始创建服务实例');
      
      // 创建服务实例（使用与面试页面相同的方式）
      const { createMinimaxService } = await import('../services/MinimaxMCPService');
      const service = createMinimaxService(config);
      
      if (!service) {
        throw new Error('服务实例创建失败');
      }
      
      console.log('[面试风格测试] 服务实例创建成功，开始初始化');
      await service.initialize();
      
      const connected = service.isConnectedToMCP();
      console.log('[面试风格测试] 初始化完成，连接状态:', connected);
      
      if (!connected) {
        throw new Error('MiniMax服务未连接');
      }
      
      // 测试不同面试官的语音
      const interviewers = ['coordinator', 'technical', 'hr', 'product', 'behavioral', 'final'];
      const testInterviewer = interviewers[Math.floor(Math.random() * interviewers.length)];
      
      const voiceId = getInterviewerVoice(testInterviewer);
      console.log('[面试风格测试] 当前面试官:', testInterviewer, '使用语音:', voiceId);
      
      // 调用TTS
      const ttsResult = await service.textToSpeech(text, voiceId, ttsConfig);
      
      console.log('[面试风格测试] TTS结果:', ttsResult);
      
      setResult({
        ...ttsResult,
        testType: '面试页面风格测试',
        interviewer: testInterviewer,
        voiceUsed: voiceId
      });
      
      if (ttsResult.audioUrl) {
        setAudioUrl(ttsResult.audioUrl);
        if (audioRef.current) {
          audioRef.current.src = ttsResult.audioUrl;
          audioRef.current.load();
        }
      }

    } catch (err) {
      console.error('[面试风格测试] 测试失败:', err);
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            MiniMax TTS 测试页面
          </h1>

          {/* 输入区域 */}
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                测试文本
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="输入要转换为语音的文本..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                语音选择
              </label>
              <select
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {voiceOptions.map(option => (
                  <option key={option.id} value={option.id}>
                    {option.name} ({option.id})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex flex-wrap gap-4 mb-6">
            <button
              onClick={handleTTSTest}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '处理中...' : '通过服务类测试TTS'}
            </button>

            <button
              onClick={handleDirectAPITest}
              disabled={isLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '处理中...' : '直接API测试'}
            </button>

            <button
              onClick={handleGetVoices}
              disabled={isLoading}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '处理中...' : '获取语音列表'}
            </button>

            <button
              onClick={handleInterviewStyleTest}
              disabled={isLoading}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '处理中...' : '面试页面风格测试'}
            </button>

            {audioUrl && (
              <button
                onClick={handlePlayAudio}
                className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
              >
                播放音频
              </button>
            )}
          </div>

          {/* 音频播放器 */}
          {audioUrl && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                音频播放器
              </label>
              <audio
                ref={audioRef}
                controls
                className="w-full"
                preload="metadata"
              >
                您的浏览器不支持音频播放。
              </audio>
              <p className="text-sm text-gray-500 mt-1">
                音频URL: <a href={audioUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{audioUrl}</a>
              </p>
            </div>
          )}

          {/* 错误显示 */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <h3 className="text-lg font-medium text-red-800 mb-2">错误</h3>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* 结果显示 */}
          {result && (
            <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-md">
              <h3 className="text-lg font-medium text-gray-800 mb-2">测试结果</h3>
              <pre className="text-sm text-gray-600 overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}

          {/* 说明文档 */}
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <h3 className="text-lg font-medium text-blue-800 mb-2">使用说明</h3>
            <ul className="text-blue-700 space-y-1">
              <li>• 输入要转换的文本，选择合适的语音</li>
              <li>• 点击"通过服务类测试TTS"使用封装的服务类</li>
              <li>• 点击"直接API测试"直接调用后端API</li>
              <li>• 点击"获取语音列表"查看所有可用语音</li>
              <li>• 成功后会显示音频播放器，可以直接播放</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestMinimaxTTS; 