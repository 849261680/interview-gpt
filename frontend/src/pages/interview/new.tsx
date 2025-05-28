import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Link from 'next/link';

/**
 * 面试创建页面
 * 允许用户选择职位、上传简历并设置面试参数
 */
export default function NewInterview() {
  const router = useRouter();
  const [position, setPosition] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // 预设职位列表
  const positions = [
    { id: 'ai_engineer', name: 'AI应用工程师' },
    { id: 'ai_product', name: 'AI产品经理' },
    { id: 'marketing', name: '市场营销专员' },
    { id: 'data_scientist', name: '数据科学家' },
    { id: 'backend_dev', name: '后端开发工程师' },
    { id: 'frontend_dev', name: '前端开发工程师' },
    { id: 'full_stack', name: '全栈开发工程师' },
    { id: 'custom', name: '自定义...' }
  ];

  // 处理简历上传
  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setResumeFile(e.target.files[0]);
    }
  };

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // 在没有完整后端的情况下，模拟面试创建
      const formData = new FormData();
      formData.append('position', position);
      formData.append('difficulty', difficulty);
      if (resumeFile) formData.append('resume', resumeFile);
      
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模拟面试ID
      const mockInterviewId = Math.floor(Math.random() * 10000).toString();
      router.push(`/interview/${mockInterviewId}`);
    } catch (error) {
      console.error('创建面试失败:', error);
      alert('创建面试失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1f2937 0%, #312e81 50%, #1f2937 100%)',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <Head>
        <title>创建面试 | Interview-GPT</title>
        <meta name="description" content="创建一个新的AI模拟面试" />
      </Head>

      {/* 顶部导航栏 */}
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
            <Link href="/" style={{ textDecoration: 'none' }}>
              <span style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                cursor: 'pointer'
              }}>
                Interview-GPT
              </span>
            </Link>
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

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '4rem 1rem' }}>
        <div style={{ maxWidth: '768px', margin: '0 auto', position: 'relative' }}>
          {/* 装饰元素 */}
          <div style={{
            position: 'absolute',
            top: '-5rem',
            left: '-5rem',
            width: '16rem',
            height: '16rem',
            background: 'rgba(59, 130, 246, 0.1)',
            borderRadius: '50%',
            filter: 'blur(3rem)',
            zIndex: -1
          }}></div>
          <div style={{
            position: 'absolute',
            bottom: '-5rem',
            right: '-5rem',
            width: '16rem',
            height: '16rem',
            background: 'rgba(168, 85, 247, 0.1)',
            borderRadius: '50%',
            filter: 'blur(3rem)',
            zIndex: -1
          }}></div>
          
          {/* 返回链接 */}
          <div style={{ marginBottom: '0.5rem' }}>
            <Link href="/" style={{
              display: 'inline-flex',
              alignItems: 'center',
              color: 'rgba(255, 255, 255, 0.8)',
              textDecoration: 'none',
              transition: 'color 0.2s'
            }}>
              <svg style={{ width: '1.25rem', height: '1.25rem', marginRight: '0.5rem' }} viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
              返回首页
            </Link>
          </div>

          {/* 页面标题 */}
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: 'bold',
              marginBottom: '1rem',
              background: 'linear-gradient(45deg, #60a5fa, #a855f7)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              创建模拟面试
            </h1>
            <p style={{
              color: 'rgba(255, 255, 255, 0.7)',
              maxWidth: '36rem',
              margin: '0 auto'
            }}>
              设置面试参数，开始你的专业化面试体验
            </p>
          </div>

          {/* 表单卡片 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '2rem',
            borderRadius: '1rem',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            <form onSubmit={handleSubmit}>
              {/* 职位选择 */}
              <div style={{ marginBottom: '2rem' }}>
                <label style={{
                  display: 'block',
                  fontSize: '1.125rem',
                  fontWeight: '500',
                  marginBottom: '0.5rem',
                  color: 'rgba(255, 255, 255, 0.9)'
                }}>
                  选择面试职位
                </label>
                <select 
                  style={{
                    width: '100%',
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '0.5rem',
                    padding: '0.75rem 1rem',
                    color: 'white',
                    fontSize: '1rem',
                    outline: 'none',
                    transition: 'all 0.2s'
                  }}
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  required
                  onFocus={(e) => {
                    e.target.style.borderColor = 'rgba(59, 130, 246, 0.5)';
                    e.target.style.boxShadow = '0 0 0 2px rgba(59, 130, 246, 0.2)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                    e.target.style.boxShadow = 'none';
                  }}
                >
                  <option value="" style={{ background: '#1f2937', color: 'white' }}>请选择职位...</option>
                  {positions.map(pos => (
                    <option key={pos.id} value={pos.id} style={{ background: '#1f2937', color: 'white' }}>
                      {pos.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* 自定义职位输入 */}
              {position === 'custom' && (
                <div style={{ marginBottom: '2rem' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '1.125rem',
                    fontWeight: '500',
                    marginBottom: '0.5rem',
                    color: 'rgba(255, 255, 255, 0.9)'
                  }}>
                    自定义职位名称
                  </label>
                  <input 
                    type="text" 
                    style={{
                      width: '100%',
                      background: 'rgba(255, 255, 255, 0.1)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '0.5rem',
                      padding: '0.75rem 1rem',
                      color: 'white',
                      fontSize: '1rem',
                      outline: 'none',
                      transition: 'all 0.2s'
                    }}
                    placeholder="输入职位名称"
                    required
                    onFocus={(e) => {
                      e.target.style.borderColor = 'rgba(59, 130, 246, 0.5)';
                      e.target.style.boxShadow = '0 0 0 2px rgba(59, 130, 246, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                </div>
              )}

              {/* 难度选择 */}
              <div style={{ marginBottom: '2rem' }}>
                <label style={{
                  display: 'block',
                  fontSize: '1.125rem',
                  fontWeight: '500',
                  marginBottom: '0.5rem',
                  color: 'rgba(255, 255, 255, 0.9)'
                }}>
                  面试难度
                </label>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  {[
                    { value: 'easy', label: '初级', color: '#10b981' },
                    { value: 'medium', label: '中级', color: '#f59e0b' },
                    { value: 'hard', label: '高级', color: '#ef4444' }
                  ].map(diff => (
                    <label key={diff.value} style={{
                      display: 'flex',
                      alignItems: 'center',
                      cursor: 'pointer',
                      padding: '0.75rem 1rem',
                      borderRadius: '0.5rem',
                      border: `2px solid ${difficulty === diff.value ? diff.color : 'rgba(255, 255, 255, 0.2)'}`,
                      background: difficulty === diff.value ? `${diff.color}20` : 'rgba(255, 255, 255, 0.05)',
                      transition: 'all 0.2s'
                    }}>
                      <input
                        type="radio"
                        name="difficulty"
                        value={diff.value}
                        checked={difficulty === diff.value}
                        onChange={(e) => setDifficulty(e.target.value)}
                        style={{ display: 'none' }}
                      />
                      <span style={{ color: 'white', fontWeight: '500' }}>{diff.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* 简历上传 */}
              <div style={{ marginBottom: '2rem' }}>
                <label style={{
                  display: 'block',
                  fontSize: '1.125rem',
                  fontWeight: '500',
                  marginBottom: '0.5rem',
                  color: 'rgba(255, 255, 255, 0.9)'
                }}>
                  上传简历 (可选)
                </label>
                <div style={{
                  border: '2px dashed rgba(255, 255, 255, 0.2)',
                  borderRadius: '0.5rem',
                  padding: '2rem',
                  textAlign: 'center',
                  transition: 'border-color 0.2s'
                }}>
                  {resumeFile ? (
                    <div>
                      <p style={{ color: '#10b981', marginBottom: '0.5rem' }}>
                        已选择文件: {resumeFile.name}
                      </p>
                      <button 
                        type="button"
                        onClick={() => setResumeFile(null)}
                        style={{
                          background: 'transparent',
                          border: '1px solid rgba(239, 68, 68, 0.5)',
                          color: '#ef4444',
                          padding: '0.5rem 1rem',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.875rem',
                          marginTop: '0.5rem'
                        }}
                      >
                        移除文件
                      </button>
                    </div>
                  ) : (
                    <>
                      <div style={{
                        width: '4rem',
                        height: '4rem',
                        margin: '0 auto 1rem',
                        background: 'rgba(255, 255, 255, 0.1)',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <svg style={{ width: '2rem', height: '2rem', color: 'rgba(255, 255, 255, 0.7)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                      </div>
                      <p style={{ marginBottom: '1rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                        拖放文件到此处或点击选择文件
                      </p>
                      <input
                        id="resume-upload"
                        type="file"
                        accept=".pdf,.doc,.docx"
                        style={{ display: 'none' }}
                        onChange={handleResumeChange}
                      />
                      <label htmlFor="resume-upload">
                        <button type="button" style={{
                          background: 'transparent',
                          border: '1px solid rgba(59, 130, 246, 0.3)',
                          color: 'white',
                          padding: '0.5rem 1rem',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}>
                          选择文件
                        </button>
                      </label>
                    </>
                  )}
                </div>
                <p style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)', marginTop: '0.5rem' }}>
                  支持 PDF、DOC、DOCX 格式，最大 10MB
                </p>
              </div>

              {/* 提交按钮 */}
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <Link href="/">
                  <button type="button" style={{
                    background: 'transparent',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    color: 'white',
                    padding: '0.75rem 1.5rem',
                    borderRadius: '0.5rem',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: '500'
                  }}>
                    取消
                  </button>
                </Link>
                <button 
                  type="submit" 
                  disabled={isLoading || !position}
                  style={{
                    background: isLoading || !position 
                      ? 'rgba(107, 114, 128, 0.5)' 
                      : 'linear-gradient(45deg, #2563eb, #4f46e5)',
                    color: 'white',
                    border: 'none',
                    padding: '0.75rem 1.5rem',
                    borderRadius: '0.5rem',
                    cursor: isLoading || !position ? 'not-allowed' : 'pointer',
                    fontSize: '1rem',
                    fontWeight: '500',
                    boxShadow: isLoading || !position ? 'none' : '0 10px 25px rgba(79, 70, 229, 0.2)',
                    opacity: isLoading || !position ? 0.6 : 1
                  }}
                >
                  {isLoading ? '创建中...' : '开始面试'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
