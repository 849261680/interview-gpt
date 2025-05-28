/**
 * 面试评估系统测试页面
 * 用于测试实时评估和评估报告功能
 */
import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

const TestAssessment: React.FC = () => {
  const [currentView, setCurrentView] = useState<'interview' | 'report' | 'charts' | 'monitor'>('interview');
  const [testInterviewId] = useState(12345); // 测试用的面试ID
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewEnded, setInterviewEnded] = useState(false);

  // 模拟评估数据
  const mockDimensionScores = {
    'technical_knowledge': 85,
    'problem_solving': 78,
    'code_quality': 82,
    'system_design': 75,
    'communication': 88,
    'professionalism': 90
  };

  const mockAssessmentHistory = [
    { timestamp: '2024-01-01T10:00:00Z', overall_score: 70, dimension_scores: mockDimensionScores },
    { timestamp: '2024-01-01T10:05:00Z', overall_score: 75, dimension_scores: mockDimensionScores },
    { timestamp: '2024-01-01T10:10:00Z', overall_score: 80, dimension_scores: mockDimensionScores },
    { timestamp: '2024-01-01T10:15:00Z', overall_score: 83, dimension_scores: mockDimensionScores },
  ];

  const handleInterviewStart = () => {
    setInterviewStarted(true);
    console.log('面试开始');
  };

  const handleInterviewEnd = (result: any) => {
    setInterviewEnded(true);
    console.log('面试结束:', result);
  };

  const handleError = (error: string) => {
    console.error('面试错误:', error);
  };

  const views = [
    { key: 'interview', label: '面试界面', icon: '🎤' },
    { key: 'report', label: '评估报告', icon: '📊' },
    { key: 'charts', label: '数据可视化', icon: '📈' },
    { key: 'monitor', label: '系统监控', icon: '🔍' }
  ];

  // 简单的雷达图组件
  const SimpleRadarChart = ({ scores }: { scores: Record<string, number> }) => {
    const dimensions = Object.keys(scores);
    const values = Object.values(scores);
    const maxValue = 100;
    
    // 计算雷达图的点
    const centerX = 150;
    const centerY = 150;
    const radius = 100;
    
    const points = dimensions.map((_, index) => {
      const angle = (index * 2 * Math.PI) / dimensions.length - Math.PI / 2;
      const value = values[index];
      const r = (value / maxValue) * radius;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      return { x, y, value, label: _ };
    });

    return (
      <div style={{
        background: 'white',
        borderRadius: '0.5rem',
        padding: '1.5rem',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        border: '1px solid rgba(229, 231, 235, 1)'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
          能力雷达图
        </h3>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <svg width="300" height="300" style={{ overflow: 'visible' }}>
            {/* 背景网格 */}
            {[20, 40, 60, 80, 100].map(percent => {
              const r = (percent / 100) * radius;
              const gridPoints = dimensions.map((_, index) => {
                const angle = (index * 2 * Math.PI) / dimensions.length - Math.PI / 2;
                const x = centerX + r * Math.cos(angle);
                const y = centerY + r * Math.sin(angle);
                return `${x},${y}`;
              }).join(' ');
              
              return (
                <polygon
                  key={percent}
                  points={gridPoints}
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
              );
            })}
            
            {/* 轴线 */}
            {dimensions.map((_, index) => {
              const angle = (index * 2 * Math.PI) / dimensions.length - Math.PI / 2;
              const x = centerX + radius * Math.cos(angle);
              const y = centerY + radius * Math.sin(angle);
              return (
                <line
                  key={index}
                  x1={centerX}
                  y1={centerY}
                  x2={x}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
              );
            })}
            
            {/* 数据多边形 */}
            <polygon
              points={points.map(p => `${p.x},${p.y}`).join(' ')}
              fill="rgba(59, 130, 246, 0.2)"
              stroke="#3b82f6"
              strokeWidth="2"
            />
            
            {/* 数据点 */}
            {points.map((point, index) => (
              <circle
                key={index}
                cx={point.x}
                cy={point.y}
                r="4"
                fill="#3b82f6"
              />
            ))}
            
            {/* 标签 */}
            {points.map((point, index) => {
              const angle = (index * 2 * Math.PI) / dimensions.length - Math.PI / 2;
              const labelRadius = radius + 20;
              const labelX = centerX + labelRadius * Math.cos(angle);
              const labelY = centerY + labelRadius * Math.sin(angle);
              
              return (
                <text
                  key={index}
                  x={labelX}
                  y={labelY}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize="12"
                  fill="#374151"
                >
                  {point.label.replace('_', ' ')}
                </text>
              );
            })}
          </svg>
        </div>
      </div>
    );
  };

  // 简单的柱状图组件
  const SimpleBarChart = ({ scores }: { scores: Record<string, number> }) => {
    const dimensions = Object.keys(scores);
    const values = Object.values(scores);
    const maxValue = Math.max(...values);

    return (
      <div style={{
        background: 'white',
        borderRadius: '0.5rem',
        padding: '1.5rem',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        border: '1px solid rgba(229, 231, 235, 1)'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
          能力评分
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {dimensions.map((dim, index) => (
            <div key={dim} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '120px', fontSize: '0.875rem', color: '#374151' }}>
                {dim.replace('_', ' ')}
              </div>
              <div style={{ flex: 1, background: '#f3f4f6', borderRadius: '0.25rem', height: '20px', position: 'relative' }}>
                <div style={{
                  background: 'linear-gradient(90deg, #3b82f6, #1d4ed8)',
                  height: '100%',
                  borderRadius: '0.25rem',
                  width: `${(values[index] / 100) * 100}%`,
                  transition: 'width 0.3s ease'
                }}></div>
              </div>
              <div style={{ width: '40px', fontSize: '0.875rem', fontWeight: '600', color: '#1f2937' }}>
                {values[index]}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1f2937 0%, #312e81 50%, #1f2937 100%)',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <Head>
        <title>测试评估系统 | Interview-GPT</title>
        <meta name="description" content="测试面试评估系统的各项功能" />
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

      {/* 头部信息 */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '2rem 1rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                面试评估系统测试
              </h1>
              <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                测试实时评估、报告生成、数据可视化和系统监控功能
              </p>
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {views.map((view) => (
                <button
                  key={view.key}
                  onClick={() => setCurrentView(view.key as any)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s',
                    background: currentView === view.key
                      ? 'linear-gradient(45deg, #2563eb, #4f46e5)'
                      : 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    border: currentView === view.key
                      ? 'none'
                      : '1px solid rgba(255, 255, 255, 0.2)',
                    cursor: 'pointer'
                  }}
                >
                  <span>{view.icon}</span>
                  <span>{view.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 状态指示器 */}
      <div style={{
        background: 'rgba(59, 130, 246, 0.1)',
        borderBottom: '1px solid rgba(59, 130, 246, 0.2)'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0.75rem 1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                background: interviewStarted ? '#10b981' : '#6b7280'
              }}></div>
              <span style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.8)' }}>面试已开始</span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                background: interviewEnded ? '#3b82f6' : '#6b7280'
              }}></div>
              <span style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.8)' }}>面试已结束</span>
            </div>
            
            <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
              测试面试ID: {testInterviewId}
            </div>
            
            <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
              当前视图: {views.find(v => v.key === currentView)?.label}
            </div>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '2rem 1rem'
      }}>
        {/* 面试界面 */}
        {currentView === 'interview' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '0.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '1rem',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <h2 style={{ fontSize: '1.125rem', fontWeight: '500', color: 'white' }}>面试界面测试</h2>
              <p style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)', marginTop: '0.25rem' }}>
                测试实时评估功能，包括语音交互、消息处理和评分更新
              </p>
            </div>
            
            <div style={{ height: '600px', padding: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(45deg, #3b82f6, #8b5cf6)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1rem',
                  fontSize: '2rem'
                }}>
                  🎤
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>面试界面组件</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '1.5rem' }}>
                  这里将显示完整的面试界面，包含实时评估功能
                </p>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                  <button
                    onClick={handleInterviewStart}
                    disabled={interviewStarted}
                    style={{
                      background: interviewStarted ? 'rgba(107, 114, 128, 0.5)' : 'linear-gradient(45deg, #10b981, #059669)',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '0.375rem',
                      cursor: interviewStarted ? 'not-allowed' : 'pointer',
                      fontSize: '0.875rem',
                      opacity: interviewStarted ? 0.6 : 1
                    }}
                  >
                    {interviewStarted ? '面试已开始' : '开始面试'}
                  </button>
                  <button
                    onClick={() => handleInterviewEnd({})}
                    disabled={!interviewStarted || interviewEnded}
                    style={{
                      background: (!interviewStarted || interviewEnded) ? 'rgba(107, 114, 128, 0.5)' : 'linear-gradient(45deg, #ef4444, #dc2626)',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '0.375rem',
                      cursor: (!interviewStarted || interviewEnded) ? 'not-allowed' : 'pointer',
                      fontSize: '0.875rem',
                      opacity: (!interviewStarted || interviewEnded) ? 0.6 : 1
                    }}
                  >
                    {interviewEnded ? '面试已结束' : '结束面试'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 评估报告 */}
        {currentView === 'report' && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem' }}>评估报告测试</h2>
              <p style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                查看详细的面试评估报告，包含多维度分析和改进建议
              </p>
            </div>
            
            <div style={{
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '0.5rem',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              padding: '2rem'
            }}>
              <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(45deg, #8b5cf6, #ec4899)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1rem',
                  fontSize: '2rem'
                }}>
                  📊
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>评估报告组件</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  这里将显示详细的面试评估报告和分析结果
                </p>
              </div>

              {/* 模拟报告数据 */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {Object.entries(mockDimensionScores).map(([key, value]) => (
                  <div key={key} style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    padding: '1rem',
                    borderRadius: '0.375rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem' }}>
                      {key.replace('_', ' ').toUpperCase()}
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: value >= 80 ? '#10b981' : value >= 60 ? '#f59e0b' : '#ef4444' }}>
                      {value}分
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 数据可视化 */}
        {currentView === 'charts' && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem' }}>数据可视化测试</h2>
              <p style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                测试各种图表组件的数据展示效果
              </p>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
              <SimpleRadarChart scores={mockDimensionScores} />
              <SimpleBarChart scores={mockDimensionScores} />
            </div>
          </div>
        )}

        {/* 系统监控 */}
        {currentView === 'monitor' && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem' }}>系统监控测试</h2>
              <p style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                监控系统运行状态和性能指标
              </p>
            </div>
            
            <div style={{
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '0.5rem',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              padding: '2rem'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(45deg, #10b981, #06b6d4)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1rem',
                  fontSize: '2rem'
                }}>
                  🔍
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>系统监控组件</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
                  这里将显示系统运行状态、性能指标和监控数据
                </p>

                {/* 模拟监控数据 */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', textAlign: 'left' }}>
                  <div style={{
                    background: 'rgba(16, 185, 129, 0.1)',
                    padding: '1rem',
                    borderRadius: '0.375rem',
                    border: '1px solid rgba(16, 185, 129, 0.2)'
                  }}>
                    <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>API状态</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#10b981' }}>正常</div>
                  </div>
                  <div style={{
                    background: 'rgba(245, 158, 11, 0.1)',
                    padding: '1rem',
                    borderRadius: '0.375rem',
                    border: '1px solid rgba(245, 158, 11, 0.2)'
                  }}>
                    <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>响应时间</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#f59e0b' }}>120ms</div>
                  </div>
                  <div style={{
                    background: 'rgba(59, 130, 246, 0.1)',
                    padding: '1rem',
                    borderRadius: '0.375rem',
                    border: '1px solid rgba(59, 130, 246, 0.2)'
                  }}>
                    <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>活跃连接</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#3b82f6' }}>42</div>
                  </div>
                  <div style={{
                    background: 'rgba(168, 85, 247, 0.1)',
                    padding: '1rem',
                    borderRadius: '0.375rem',
                    border: '1px solid rgba(168, 85, 247, 0.2)'
                  }}>
                    <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>内存使用</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#a855f7' }}>68%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestAssessment; 