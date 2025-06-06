import React, { useState } from 'react';
import Head from 'next/head';

/**
 * API调试页面
 * 用于调试面试创建API的具体问题
 */
export default function DebugAPI() {
  const [result, setResult] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const testAPI = async () => {
    setIsLoading(true);
    setResult('开始测试...\n');

    try {
      // 1. 测试健康检查
      setResult(prev => prev + '1. 测试健康检查端点...\n');
      const healthResponse = await fetch('http://localhost:8000/health');
      setResult(prev => prev + `健康检查状态: ${healthResponse.status} ${healthResponse.statusText}\n`);
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setResult(prev => prev + `健康检查响应: ${JSON.stringify(healthData)}\n\n`);
      }

      // 2. 测试API根路径
      setResult(prev => prev + '2. 测试API根路径...\n');
      const rootResponse = await fetch('http://localhost:8000/api/');
      setResult(prev => prev + `API根路径状态: ${rootResponse.status} ${rootResponse.statusText}\n`);
      
      if (rootResponse.ok) {
        const rootData = await rootResponse.text();
        setResult(prev => prev + `API根路径响应: ${rootData.substring(0, 200)}...\n\n`);
      }

      // 3. 测试面试端点 - GET方法（应该返回405）
      setResult(prev => prev + '3. 测试面试端点 GET方法...\n');
      const getResponse = await fetch('http://localhost:8000/api/interviews/');
      setResult(prev => prev + `GET /api/interviews/ 状态: ${getResponse.status} ${getResponse.statusText}\n`);
      
      if (!getResponse.ok) {
        const getError = await getResponse.json();
        setResult(prev => prev + `GET错误响应: ${JSON.stringify(getError)}\n\n`);
      }

      // 4. 测试面试端点 - POST方法
      setResult(prev => prev + '4. 测试面试端点 POST方法...\n');
      const formData = new FormData();
      formData.append('position', '调试测试工程师');
      formData.append('difficulty', 'medium');

      const postResponse = await fetch('http://localhost:8000/api/interviews/', {
        method: 'POST',
        body: formData,
      });

      setResult(prev => prev + `POST /api/interviews/ 状态: ${postResponse.status} ${postResponse.statusText}\n`);
      
      if (postResponse.ok) {
        const postData = await postResponse.json();
        setResult(prev => prev + `POST成功响应: ${JSON.stringify(postData, null, 2)}\n\n`);
        setResult(prev => prev + '✅ 面试创建成功！\n');
      } else {
        const postError = await postResponse.text();
        setResult(prev => prev + `POST错误响应: ${postError}\n\n`);
        setResult(prev => prev + '❌ 面试创建失败！\n');
      }

    } catch (error) {
      setResult(prev => prev + `\n❌ 网络错误: ${error instanceof Error ? error.message : String(error)}\n`);
      
      // 检查是否是CORS错误
      if (error instanceof TypeError && error.message.includes('fetch')) {
        setResult(prev => prev + '\n可能的原因:\n');
        setResult(prev => prev + '1. CORS策略阻止了请求\n');
        setResult(prev => prev + '2. 后端服务未运行或端口不正确\n');
        setResult(prev => prev + '3. 网络连接问题\n');
        setResult(prev => prev + '\n建议:\n');
        setResult(prev => prev + '1. 检查后端服务是否在 http://localhost:8000 运行\n');
        setResult(prev => prev + '2. 检查浏览器控制台的详细错误信息\n');
        setResult(prev => prev + '3. 尝试在浏览器中直接访问 http://localhost:8000/health\n');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const testCORS = async () => {
    setResult('测试CORS配置...\n');
    
    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'OPTIONS',
        headers: {
          'Origin': 'http://localhost:3000',
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type',
        },
      });
      
      setResult(prev => prev + `OPTIONS请求状态: ${response.status}\n`);
      
      // 检查CORS头
      const corsHeaders = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
      };
      
      setResult(prev => prev + `CORS头信息: ${JSON.stringify(corsHeaders, null, 2)}\n`);
      
    } catch (error) {
      setResult(prev => prev + `CORS测试失败: ${error}\n`);
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
        <title>API调试 | Interview-GPT</title>
        <meta name="description" content="调试面试API的具体问题" />
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
          API调试工具
        </h1>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 2fr',
          gap: '2rem'
        }}>
          {/* 控制面板 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '2rem',
            borderRadius: '1rem'
          }}>
            <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>调试工具</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <button
                onClick={testAPI}
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
                {isLoading ? '测试中...' : '完整API测试'}
              </button>

              <button
                onClick={testCORS}
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
                测试CORS配置
              </button>

              <button
                onClick={() => setResult('')}
                style={{
                  background: 'linear-gradient(45deg, #6b7280, #4b5563)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  fontSize: '1rem'
                }}
              >
                清空结果
              </button>
            </div>

            <div style={{ marginTop: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>快速检查</h3>
              <div style={{ fontSize: '0.875rem', lineHeight: '1.6' }}>
                <p>1. 后端健康检查: <a href="http://localhost:8000/health" target="_blank" style={{ color: '#60a5fa' }}>http://localhost:8000/health</a></p>
                <p>2. API文档: <a href="http://localhost:8000/docs" target="_blank" style={{ color: '#60a5fa' }}>http://localhost:8000/docs</a></p>
                <p>3. 前端地址: <a href="http://localhost:3000" target="_blank" style={{ color: '#60a5fa' }}>http://localhost:3000</a></p>
              </div>
            </div>
          </div>

          {/* 结果显示 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '2rem',
            borderRadius: '1rem'
          }}>
            <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>调试结果</h2>
            
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              padding: '1rem',
              borderRadius: '0.5rem',
              height: '500px',
              overflowY: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              lineHeight: '1.5',
              whiteSpace: 'pre-wrap'
            }}>
              {result || '点击调试按钮开始测试...'}
            </div>
          </div>
        </div>

        {/* 说明信息 */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '2rem',
          borderRadius: '1rem',
          marginTop: '2rem'
        }}>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>常见问题</h2>
          <div style={{ lineHeight: '1.8' }}>
            <h3 style={{ marginBottom: '0.5rem', color: '#f59e0b' }}>404 Not Found</h3>
            <ul style={{ paddingLeft: '1.5rem', marginBottom: '1rem' }}>
              <li>检查后端服务是否运行在正确的端口（8000）</li>
              <li>确认API路由配置是否正确</li>
              <li>验证请求URL是否正确</li>
            </ul>

            <h3 style={{ marginBottom: '0.5rem', color: '#ef4444' }}>CORS错误</h3>
            <ul style={{ paddingLeft: '1.5rem', marginBottom: '1rem' }}>
              <li>检查后端CORS配置是否允许前端域名</li>
              <li>确认预检请求（OPTIONS）是否正确处理</li>
              <li>验证请求头是否被允许</li>
            </ul>

            <h3 style={{ marginBottom: '0.5rem', color: '#8b5cf6' }}>网络错误</h3>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li>检查防火墙或代理设置</li>
              <li>确认服务器地址和端口是否可达</li>
              <li>查看浏览器开发者工具的网络标签</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 