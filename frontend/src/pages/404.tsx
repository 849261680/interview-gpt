import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Custom404() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1f2937 0%, #312e81 50%, #1f2937 100%)',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Head>
        <title>页面未找到 - Interview-GPT</title>
      </Head>

      <div style={{ textAlign: 'center', maxWidth: '600px', padding: '2rem' }}>
        <h1 style={{
          fontSize: '4rem',
          fontWeight: 'bold',
          marginBottom: '1rem',
          background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          404
        </h1>
        <h2 style={{
          fontSize: '1.5rem',
          marginBottom: '1rem',
          color: 'rgba(255, 255, 255, 0.9)'
        }}>
          页面未找到
        </h2>
        <p style={{
          fontSize: '1rem',
          marginBottom: '2rem',
          color: 'rgba(255, 255, 255, 0.7)',
          lineHeight: '1.6'
        }}>
          抱歉，您访问的页面不存在。请检查URL是否正确，或返回首页。
        </p>
        <Link href="/">
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
            返回首页
          </button>
        </Link>
      </div>
    </div>
  );
} 