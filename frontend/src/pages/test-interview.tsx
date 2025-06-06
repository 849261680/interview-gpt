import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

/**
 * 面试系统测试页面
 * 用于测试面试创建和WebSocket连接的完整流程
 */
export default function TestInterview() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState<string[]>([]);

  const addTestResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  // 测试面试创建API
  const testCreateInterview = async () => {
    addTestResult('开始测试面试创建API...');
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('position', '测试工程师');
      formData.append('difficulty', 'medium');

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/interviews/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: '创建面试失败' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      addTestResult(`✅ 面试创建成功: ID=${result.id}, 职位=${result.position}`);
      
      return result.id;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      addTestResult(`❌ 面试创建失败: ${errorMessage}`);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // 测试WebSocket连接
  const testWebSocketConnection = async (interviewId: number) => {
    addTestResult(`开始测试WebSocket连接: ID=${interviewId}...`);

    return new Promise<void>((resolve) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const wsUrl = apiUrl.replace(/^http/, 'ws');
      const wsEndpoint = `${wsUrl}/api/interview-process/${interviewId}/ws`;

      addTestResult(`连接WebSocket: ${wsEndpoint}`);

      const socket = new WebSocket(wsEndpoint);

      socket.onopen = () => {
        addTestResult('✅ WebSocket连接成功');
        
        // 发送测试消息
        socket.send(JSON.stringify({
          type: 'message',
          content: '这是一条测试消息'
        }));
        addTestResult('📤 发送测试消息');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          addTestResult(`📥 收到消息: ${data.type} - ${JSON.stringify(data.data).substring(0, 100)}...`);
        } catch (error) {
          addTestResult(`📥 收到原始消息: ${event.data.substring(0, 100)}...`);
        }
      };

      socket.onerror = (error) => {
        addTestResult(`❌ WebSocket错误: ${error}`);
        resolve();
      };

      socket.onclose = (event) => {
        addTestResult(`🔌 WebSocket连接关闭: code=${event.code}, reason=${event.reason}`);
        resolve();
      };

      // 5秒后关闭连接
      setTimeout(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.close();
          addTestResult('⏰ 测试完成，关闭WebSocket连接');
        }
        resolve();
      }, 5000);
    });
  };

  // 测试不存在的面试ID
  const testInvalidInterviewId = async () => {
    const invalidId = 99999;
    addTestResult(`开始测试无效面试ID: ${invalidId}...`);

    return new Promise<void>((resolve) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const wsUrl = apiUrl.replace(/^http/, 'ws');
      const wsEndpoint = `${wsUrl}/api/interview-process/${invalidId}/ws`;

      const socket = new WebSocket(wsEndpoint);

      socket.onopen = () => {
        addTestResult('WebSocket连接已建立，等待错误响应...');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'error' && data.data.code === 'INTERVIEW_NOT_FOUND') {
            addTestResult(`✅ 正确处理无效ID错误: ${data.data.message}`);
          } else {
            addTestResult(`📥 收到消息: ${JSON.stringify(data)}`);
          }
        } catch (error) {
          addTestResult(`📥 收到原始消息: ${event.data}`);
        }
      };

      socket.onerror = (error) => {
        addTestResult(`WebSocket错误: ${error}`);
      };

      socket.onclose = (event) => {
        addTestResult(`✅ WebSocket正确关闭: code=${event.code}`);
        resolve();
      };

      // 10秒后强制关闭
      setTimeout(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.close();
        }
        resolve();
      }, 10000);
    });
  };

  // 运行完整测试
  const runFullTest = async () => {
    setTestResults([]);
    addTestResult('🚀 开始完整测试流程...');

    // 1. 测试面试创建
    const interviewId = await testCreateInterview();
    
    if (interviewId) {
      // 2. 测试WebSocket连接
      await testWebSocketConnection(interviewId);
    }

    // 3. 测试无效面试ID
    await testInvalidInterviewId();

    addTestResult('🎉 测试流程完成!');
  };

  // 跳转到面试页面
  const goToInterview = async () => {
    const interviewId = await testCreateInterview();
    if (interviewId) {
      router.push(`/interview/${interviewId}`);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1f2937 0%, #312e81 50%, #1f2937 100%)',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '2rem'
    }}>
      <Head>
        <title>面试系统测试 | Interview-GPT</title>
        <meta name="description" content="测试面试系统的各项功能" />
      </Head>

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          marginBottom: '2rem',
          textAlign: 'center',
          background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          面试系统测试
        </h1>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          marginBottom: '2rem'
        }}>
          {/* 测试按钮 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '2rem',
            borderRadius: '1rem'
          }}>
            <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>测试功能</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <button
                onClick={testCreateInterview}
                disabled={isLoading}
                style={{
                  background: 'linear-gradient(45deg, #2563eb, #4f46e5)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.5rem',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  opacity: isLoading ? 0.6 : 1
                }}
              >
                {isLoading ? '测试中...' : '测试面试创建API'}
              </button>

              <button
                onClick={testInvalidInterviewId}
                disabled={isLoading}
                style={{
                  background: 'linear-gradient(45deg, #dc2626, #b91c1c)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.5rem',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  opacity: isLoading ? 0.6 : 1
                }}
              >
                测试无效面试ID
              </button>

              <button
                onClick={runFullTest}
                disabled={isLoading}
                style={{
                  background: 'linear-gradient(45deg, #059669, #047857)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.5rem',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  opacity: isLoading ? 0.6 : 1
                }}
              >
                运行完整测试
              </button>

              <button
                onClick={goToInterview}
                disabled={isLoading}
                style={{
                  background: 'linear-gradient(45deg, #7c3aed, #6d28d9)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.5rem',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  opacity: isLoading ? 0.6 : 1
                }}
              >
                创建并进入面试
              </button>
            </div>
          </div>

          {/* 测试结果 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '2rem',
            borderRadius: '1rem'
          }}>
            <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>测试结果</h2>
            
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              padding: '1rem',
              borderRadius: '0.5rem',
              height: '400px',
              overflowY: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              lineHeight: '1.5'
            }}>
              {testResults.length === 0 ? (
                <div style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                  点击测试按钮开始测试...
                </div>
              ) : (
                testResults.map((result, index) => (
                  <div key={index} style={{ marginBottom: '0.5rem' }}>
                    {result}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* 说明信息 */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '2rem',
          borderRadius: '1rem'
        }}>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>测试说明</h2>
          <ul style={{ lineHeight: '1.8', paddingLeft: '1.5rem' }}>
            <li><strong>测试面试创建API:</strong> 验证后端面试创建接口是否正常工作</li>
            <li><strong>测试无效面试ID:</strong> 验证WebSocket对不存在面试ID的错误处理</li>
            <li><strong>运行完整测试:</strong> 执行完整的测试流程，包括创建面试、WebSocket连接和错误处理</li>
            <li><strong>创建并进入面试:</strong> 创建新面试并直接跳转到面试页面</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 