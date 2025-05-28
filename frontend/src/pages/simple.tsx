import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function SimplePage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1f2937 0%, #312e81 50%, #1f2937 100%)',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <Head>
        <title>Interview-GPT - AI模拟面试平台</title>
        <meta name="description" content="由多位AI AGENT轮流对用户进行面试的模拟面试平台" />
      </Head>

      {/* 导航栏 */}
      <nav style={{
        background: 'rgba(0, 0, 0, 0.3)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        padding: '1rem 0',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Interview-GPT
            </span>
          </div>
          <div style={{ display: 'flex', gap: '2rem' }}>
            <Link href="/" style={{ color: 'rgba(255, 255, 255, 0.9)', textDecoration: 'none' }}>
              首页
            </Link>
            <Link href="/interview/new" style={{ color: 'rgba(255, 255, 255, 0.9)', textDecoration: 'none' }}>
              开始面试
            </Link>
            <Link href="/TestAssessment" style={{ color: 'rgba(255, 255, 255, 0.9)', textDecoration: 'none' }}>
              测试评估
            </Link>
          </div>
          <div>
            <Link href="/interview/new">
              <button style={{
                background: 'linear-gradient(45deg, #2563eb, #4f46e5)',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}>
                创建面试
              </button>
            </Link>
          </div>
        </div>
      </nav>

      {/* 主要内容 */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '4rem 1rem' }}>
        {/* 英雄区域 */}
        <div style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto', position: 'relative' }}>
          <h1 style={{
            fontSize: '3.5rem',
            fontWeight: 'bold',
            marginBottom: '1.5rem',
            lineHeight: '1.1'
          }}>
            <span style={{
              background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Interview-GPT
            </span>
          </h1>
          <p style={{
            fontSize: '1.25rem',
            marginBottom: '2.5rem',
            color: 'rgba(255, 255, 255, 0.8)',
            lineHeight: '1.6'
          }}>
            多AI AGENT面试系统，由不同角色的AI面试官轮流提问，帮助你准备下一次重要面试
          </p>
          
          <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/interview/new">
              <button style={{
                background: 'linear-gradient(45deg, #2563eb, #4f46e5)',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '500',
                boxShadow: '0 10px 25px rgba(79, 70, 229, 0.2)'
              }}>
                开始模拟面试
              </button>
            </Link>
            <Link href="/TestAssessment">
              <button style={{
                background: 'transparent',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '500'
              }}>
                测试评估系统
              </button>
            </Link>
          </div>
        </div>

        {/* 特性展示 */}
        <div style={{ marginTop: '8rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            padding: '2rem',
            borderRadius: '1rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              background: 'linear-gradient(45deg, #3b82f6, #4f46e5)',
              borderRadius: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1.5rem'
            }}>
              👥
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>多角色面试官</h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>
              技术面试官、HR面试官和行为面试官轮流提问，全方位评估你的表现，提供真实面试体验
            </p>
          </div>
          
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            padding: '2rem',
            borderRadius: '1rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              background: 'linear-gradient(45deg, #8b5cf6, #ec4899)',
              borderRadius: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1.5rem'
            }}>
              🎤
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>语音交互</h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>
              支持语音输入和输出，模拟真实面试场景，提升沟通表达能力，锻炼应变思维
            </p>
          </div>
          
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            padding: '2rem',
            borderRadius: '1rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              background: 'linear-gradient(45deg, #10b981, #06b6d4)',
              borderRadius: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1.5rem'
            }}>
              📊
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.75rem' }}>个性化反馈</h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>
              面试结束后获得详细评估报告，了解优势和需要改进的地方，持续提升面试表现
            </p>
          </div>
        </div>

        {/* CTA部分 */}
        <div style={{ marginTop: '8rem', textAlign: 'center' }}>
          <div style={{
            maxWidth: '600px',
            margin: '0 auto',
            background: 'linear-gradient(45deg, rgba(37, 99, 235, 0.2), rgba(168, 85, 247, 0.2))',
            backdropFilter: 'blur(10px)',
            padding: '3rem',
            borderRadius: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem' }}>准备好接受挑战了吗？</h2>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
              开始你的模拟面试，获取专业反馈，让你在下一次真实面试中脱颖而出
            </p>
            <Link href="/interview/new">
              <button style={{
                background: 'linear-gradient(45deg, #2563eb, #4f46e5)',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '500',
                boxShadow: '0 10px 25px rgba(79, 70, 229, 0.2)'
              }}>
                立即开始面试
              </button>
            </Link>
          </div>
        </div>
      </main>

      {/* 页脚 */}
      <footer style={{
        marginTop: '8rem',
        padding: '3rem 0',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        background: 'rgba(0, 0, 0, 0.3)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem', textAlign: 'center' }}>
          <h3 style={{
            fontSize: '1.25rem',
            fontWeight: 'bold',
            marginBottom: '1rem',
            background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Interview-GPT
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', marginBottom: '2rem' }}>
            提升面试能力的AI助手，帮助你准备下一次重要面试
          </p>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
            © 2025 Interview-GPT. 提升面试能力的AI助手。保留所有权利。
          </p>
        </div>
      </footer>
    </div>
  );
} 