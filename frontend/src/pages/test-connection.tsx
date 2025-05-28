import React, { useState, useEffect } from 'react';

interface ConnectionStatus {
  frontend: string;
  backend?: any;
  environment?: any;
  error?: string;
}

export default function TestConnection() {
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    setLoading(true);
    try {
      // 直接从客户端测试后端连接
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log('Testing connection to:', backendUrl);
      
      const response = await fetch(`${backendUrl}/health`);
      const data = await response.json();
      
      setStatus({
        frontend: 'connected',
        backend: data,
        environment: {
          API_URL: process.env.NEXT_PUBLIC_API_URL,
          WS_URL: process.env.NEXT_PUBLIC_WS_URL,
          MINIMAX_CONFIGURED: !!process.env.NEXT_PUBLIC_MINIMAX_API_KEY
        }
      });
    } catch (error) {
      console.error('Connection failed:', error);
      setStatus({
        frontend: 'connected',
        error: error instanceof Error ? error.message : 'Unknown error',
        environment: {
          API_URL: process.env.NEXT_PUBLIC_API_URL,
          WS_URL: process.env.NEXT_PUBLIC_WS_URL,
          MINIMAX_CONFIGURED: !!process.env.NEXT_PUBLIC_MINIMAX_API_KEY
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const testApiEndpoint = async () => {
    try {
      const response = await fetch('/api/real-time-assessment/health');
      const data = await response.json();
      console.log('API endpoint test:', data);
      alert('API endpoint test: ' + JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('API endpoint test failed:', error);
      alert('API endpoint test failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace' }}>
      <h1>前后端连接测试</h1>
      
      <div style={{ marginBottom: '2rem' }}>
        <button onClick={testConnection} disabled={loading}>
          {loading ? '测试中...' : '重新测试连接'}
        </button>
        <button onClick={testApiEndpoint} style={{ marginLeft: '1rem' }}>
          测试API端点
        </button>
      </div>

      {status && (
        <div>
          <h2>连接状态</h2>
          <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
            {JSON.stringify(status, null, 2)}
          </pre>
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <h2>环境信息</h2>
        <ul>
          <li>前端地址: http://localhost:3011</li>
          <li>后端地址: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</li>
          <li>WebSocket地址: {process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}</li>
          <li>MiniMax配置: {process.env.NEXT_PUBLIC_MINIMAX_API_KEY ? '已配置' : '未配置'}</li>
        </ul>
      </div>
    </div>
  );
} 