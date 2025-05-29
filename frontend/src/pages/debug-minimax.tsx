import React, { useState, useEffect } from 'react';
import { getMinimaxConfig, validateConfig } from '../config/minimax.config';
import { createMinimaxService } from '../services/MinimaxMCPService';

const DebugMinimaxPage: React.FC = () => {
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  useEffect(() => {
    const runDebug = async () => {
      addLog('开始调试MiniMax配置...');
      
      try {
        // 1. 检查环境变量
        const envVars = {
          apiKey: process.env.NEXT_PUBLIC_MINIMAX_API_KEY,
          groupId: process.env.NEXT_PUBLIC_MINIMAX_GROUP_ID,
          baseUrl: process.env.NEXT_PUBLIC_MINIMAX_BASE_URL
        };
        addLog(`环境变量: ${JSON.stringify(envVars)}`);

        // 2. 获取配置
        const config = getMinimaxConfig();
        addLog(`配置获取成功: API Key长度=${config.apiKey.length}, Group ID=${config.groupId}`);

        // 3. 验证配置
        const isValid = validateConfig(config);
        addLog(`配置验证结果: ${isValid}`);

        // 4. 尝试创建服务
        if (isValid) {
          addLog('尝试创建MiniMax服务...');
          const service = createMinimaxService(config);
          
          if (service) {
            addLog('服务创建成功，尝试初始化...');
            await service.initialize();
            addLog('服务初始化完成');
            
            const isConnected = service.isConnectedToMCP();
            addLog(`MCP连接状态: ${isConnected}`);
          } else {
            addLog('服务创建失败');
          }
        }

        setDebugInfo({
          envVars,
          config: {
            apiKeyLength: config.apiKey.length,
            groupId: config.groupId,
            baseUrl: config.baseUrl
          },
          isValid,
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        addLog(`错误: ${errorMessage}`);
        console.error('调试错误:', error);
      }
    };

    runDebug();
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace', background: '#1a1a1a', color: 'white', minHeight: '100vh' }}>
      <h1>MiniMax MCP 调试页面</h1>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>调试信息:</h2>
        <pre style={{ background: '#2a2a2a', padding: '1rem', borderRadius: '4px', overflow: 'auto' }}>
          {JSON.stringify(debugInfo, null, 2)}
        </pre>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h2>调试日志:</h2>
        <div style={{ background: '#2a2a2a', padding: '1rem', borderRadius: '4px', maxHeight: '400px', overflow: 'auto' }}>
          {logs.map((log, index) => (
            <div key={index} style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}>
              {log}
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h2>浏览器信息:</h2>
        <div style={{ background: '#2a2a2a', padding: '1rem', borderRadius: '4px' }}>
          <p>User Agent: {typeof window !== 'undefined' ? navigator.userAgent : 'N/A'}</p>
          <p>支持录音: {typeof window !== 'undefined' && navigator.mediaDevices ? '是' : '否'}</p>
          <p>支持WebSocket: {typeof window !== 'undefined' && window.WebSocket ? '是' : '否'}</p>
        </div>
      </div>
    </div>
  );
};

export default DebugMinimaxPage; 