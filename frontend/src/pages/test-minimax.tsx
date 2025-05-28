import React, { useEffect, useState } from 'react';

const TestMinimaxPage: React.FC = () => {
  const [config, setConfig] = useState<any>({});

  useEffect(() => {
    // 检查环境变量
    const minimaxConfig = {
      apiKey: process.env.NEXT_PUBLIC_MINIMAX_API_KEY,
      groupId: process.env.NEXT_PUBLIC_MINIMAX_GROUP_ID,
      baseUrl: process.env.NEXT_PUBLIC_MINIMAX_BASE_URL,
      hasApiKey: !!process.env.NEXT_PUBLIC_MINIMAX_API_KEY,
      hasGroupId: !!process.env.NEXT_PUBLIC_MINIMAX_GROUP_ID,
      apiKeyLength: process.env.NEXT_PUBLIC_MINIMAX_API_KEY?.length || 0,
      groupIdValue: process.env.NEXT_PUBLIC_MINIMAX_GROUP_ID
    };
    
    setConfig(minimaxConfig);
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace' }}>
      <h1>MiniMax 配置测试</h1>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>环境变量状态:</h2>
        <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
          {JSON.stringify(config, null, 2)}
        </pre>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h2>配置验证:</h2>
        <ul>
          <li>API Key: {config.hasApiKey ? '✅ 已配置' : '❌ 未配置'}</li>
          <li>Group ID: {config.hasGroupId ? '✅ 已配置' : '❌ 未配置'}</li>
          <li>Base URL: {config.baseUrl ? '✅ 已配置' : '❌ 未配置'}</li>
        </ul>
      </div>

      {config.hasApiKey && config.hasGroupId && (
        <div style={{ marginTop: '2rem' }}>
          <h2>API Key 信息:</h2>
          <p>长度: {config.apiKeyLength} 字符</p>
          <p>前20字符: {config.apiKey?.substring(0, 20)}...</p>
          <p>Group ID: {config.groupIdValue}</p>
        </div>
      )}
    </div>
  );
};

export default TestMinimaxPage; 