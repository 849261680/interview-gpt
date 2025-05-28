/**
 * 评估报告组件
 * 显示详细的面试评估报告，包含多维度分析和改进建议
 */
import React, { useState, useEffect, useCallback } from 'react';
import { twMerge } from 'tailwind-merge';
import AssessmentChart from './AssessmentChart';

export interface AssessmentReportProps {
  /** 面试ID */
  interviewId: number;
  /** 是否显示详细信息 */
  showDetails?: boolean;
  /** 报告加载完成回调 */
  onReportLoaded?: (report: any) => void;
  /** 自定义类名 */
  className?: string;
}

interface ReportData {
  interview_id: number;
  candidate_name: string;
  position: string;
  interviewer_type: string;
  start_time: string;
  end_time: string;
  overall_assessment: {
    overall_score: number;
    performance_level: string;
    interview_duration: number;
    total_messages: number;
    engagement_level: number;
    coherence_score: number;
    response_quality: number;
    trend_analysis: string;
  };
  dimension_analyses: Array<{
    dimension: string;
    score: number;
    level: string;
    trend: string;
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
    keyword_matches: number;
  }>;
  key_insights: string[];
  improvement_suggestions: string[];
  final_recommendation: string;
  confidence_score: number;
  report_generated_at: string;
}

/**
 * 评估报告组件
 * 提供完整的面试评估报告展示
 */
const AssessmentReport: React.FC<AssessmentReportProps> = ({
  interviewId,
  showDetails = true,
  onReportLoaded,
  className
}) => {
  // 状态管理
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'dimensions' | 'insights'>('overview');
  const [expandedDimensions, setExpandedDimensions] = useState<Set<string>>(new Set());

  // 获取报告数据
  const fetchReportData = useCallback(async () => {
    if (!interviewId) return;

    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`/api/assessment-report/view/${interviewId}`);
      
      if (!response.ok) {
        throw new Error('获取评估报告失败');
      }

      const result = await response.json();
      
      if (result.success && result.data) {
        setReportData(result.data);
        
        if (onReportLoaded) {
          onReportLoaded(result.data);
        }
      } else {
        throw new Error('报告数据格式错误');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取报告失败';
      setError(errorMsg);
      console.error('获取评估报告失败:', err);
    } finally {
      setIsLoading(false);
    }
  }, [interviewId, onReportLoaded]);

  // 导出报告
  const exportReport = useCallback(async (format: 'json') => {
    try {
      const response = await fetch(`/api/assessment-report/export/${interviewId}/${format}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `interview_report_${interviewId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        throw new Error('导出失败');
      }
    } catch (err) {
      console.error('导出报告失败:', err);
      setError('导出报告失败');
    }
  }, [interviewId]);

  // 切换维度展开状态
  const toggleDimensionExpanded = useCallback((dimension: string) => {
    setExpandedDimensions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(dimension)) {
        newSet.delete(dimension);
      } else {
        newSet.add(dimension);
      }
      return newSet;
    });
  }, []);

  // 组件挂载时获取数据
  useEffect(() => {
    fetchReportData();
  }, [fetchReportData]);

  // 获取分数颜色
  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  // 获取进度条颜色
  const getProgressColor = (score: number): string => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  // 获取趋势图标
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <span className="text-green-500">📈</span>;
      case 'declining':
        return <span className="text-red-500">📉</span>;
      default:
        return <span className="text-gray-500">➡️</span>;
    }
  };

  // 格式化时间
  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}分${remainingSeconds}秒`;
  };

  // 格式化维度名称
  const formatDimensionName = (dimension: string): string => {
    const nameMap: Record<string, string> = {
      'technical_knowledge': '技术知识',
      'problem_solving': '问题解决',
      'code_quality': '代码质量',
      'system_design': '系统设计',
      'communication': '沟通能力',
      'professionalism': '职业素养',
      'culture_fit': '文化匹配',
      'career_planning': '职业规划',
      'teamwork': '团队协作',
      'leadership': '领导力',
      'adaptability': '适应能力',
      'stress_handling': '压力处理'
    };
    return nameMap[dimension] || dimension;
  };

  if (isLoading) {
    return (
      <div className={twMerge('bg-white rounded-lg shadow-sm border border-gray-200 p-8', className)}>
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">正在生成评估报告...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={twMerge('bg-white rounded-lg shadow-sm border border-gray-200 p-8', className)}>
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">报告加载失败</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchReportData}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors duration-200"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className={twMerge('bg-white rounded-lg shadow-sm border border-gray-200 p-8', className)}>
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">📄</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">暂无报告数据</h3>
          <p className="text-gray-600">请先完成面试以生成评估报告</p>
        </div>
      </div>
    );
  }

  return (
    <div className={twMerge('bg-white rounded-lg shadow-sm border border-gray-200', className)}>
      {/* 报告头部 */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">面试评估报告</h2>
            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
              <span>候选人: {reportData.candidate_name}</span>
              <span>职位: {reportData.position}</span>
              <span>面试ID: {reportData.interview_id}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => exportReport('json')}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors duration-200"
            >
              📥 导出JSON
            </button>
            <button
              onClick={fetchReportData}
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors duration-200"
            >
              🔄 刷新
            </button>
          </div>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="px-6 py-3 border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { key: 'overview', label: '总体概览', icon: '📊' },
            { key: 'dimensions', label: '维度分析', icon: '📈' },
            { key: 'insights', label: '关键洞察', icon: '💡' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={twMerge(
                'flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* 标签页内容 */}
      <div className="p-6">
        {/* 总体概览 */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* 核心指标卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-600">总体评分</p>
                    <p className={twMerge('text-2xl font-bold', getScoreColor(reportData.overall_assessment.overall_score))}>
                      {Math.round(reportData.overall_assessment.overall_score)}
                    </p>
                  </div>
                  <div className="text-3xl">🎯</div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-600">表现等级</p>
                    <p className="text-lg font-semibold text-green-800">
                      {reportData.overall_assessment.performance_level}
                    </p>
                  </div>
                  <div className="text-3xl">⭐</div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-600">面试时长</p>
                    <p className="text-lg font-semibold text-purple-800">
                      {formatDuration(reportData.overall_assessment.interview_duration)}
                    </p>
                  </div>
                  <div className="text-3xl">⏱️</div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-600">置信度</p>
                    <p className="text-lg font-semibold text-orange-800">
                      {Math.round(reportData.confidence_score * 100)}%
                    </p>
                  </div>
                  <div className="text-3xl">🎲</div>
                </div>
              </div>
            </div>

            {/* 详细指标 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-900">参与度指标</h4>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>参与度</span>
                      <span className={getScoreColor(reportData.overall_assessment.engagement_level)}>
                        {Math.round(reportData.overall_assessment.engagement_level)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className={twMerge('h-2 rounded-full', getProgressColor(reportData.overall_assessment.engagement_level))}
                        style={{ width: `${reportData.overall_assessment.engagement_level}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm">
                      <span>连贯性</span>
                      <span className={getScoreColor(reportData.overall_assessment.coherence_score)}>
                        {Math.round(reportData.overall_assessment.coherence_score)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className={twMerge('h-2 rounded-full', getProgressColor(reportData.overall_assessment.coherence_score))}
                        style={{ width: `${reportData.overall_assessment.coherence_score}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm">
                      <span>回答质量</span>
                      <span className={getScoreColor(reportData.overall_assessment.response_quality)}>
                        {Math.round(reportData.overall_assessment.response_quality)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className={twMerge('h-2 rounded-full', getProgressColor(reportData.overall_assessment.response_quality))}
                        style={{ width: `${reportData.overall_assessment.response_quality}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-900">面试统计</h4>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">总消息数</span>
                    <span className="text-sm font-medium">{reportData.overall_assessment.total_messages}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">面试官类型</span>
                    <span className="text-sm font-medium">{reportData.interviewer_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">开始时间</span>
                    <span className="text-sm font-medium">
                      {new Date(reportData.start_time).toLocaleString('zh-CN')}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">结束时间</span>
                    <span className="text-sm font-medium">
                      {new Date(reportData.end_time).toLocaleString('zh-CN')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-900">趋势分析</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-700">
                    {reportData.overall_assessment.trend_analysis}
                  </p>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h5 className="text-sm font-medium text-blue-800 mb-2">最终推荐</h5>
                  <p className="text-sm text-blue-700">
                    {reportData.final_recommendation}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 维度分析 */}
        {activeTab === 'dimensions' && (
          <div className="space-y-6">
            {/* 可视化图表 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AssessmentChart
                dimensionScores={reportData.dimension_analyses.reduce((acc, dim) => {
                  acc[dim.dimension] = dim.score;
                  return acc;
                }, {} as Record<string, number>)}
                chartType="radar"
              />
              
              <AssessmentChart
                dimensionScores={reportData.dimension_analyses.reduce((acc, dim) => {
                  acc[dim.dimension] = dim.score;
                  return acc;
                }, {} as Record<string, number>)}
                chartType="bar"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reportData.dimension_analyses.map((dimension) => (
                <div key={dimension.dimension} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-lg font-medium text-gray-900">
                      {formatDimensionName(dimension.dimension)}
                    </h4>
                    <div className="flex items-center space-x-2">
                      {getTrendIcon(dimension.trend)}
                      <span className={twMerge('text-xl font-bold', getScoreColor(dimension.score))}>
                        {Math.round(dimension.score)}
                      </span>
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={twMerge('h-2 rounded-full', getProgressColor(dimension.score))}
                        style={{ width: `${dimension.score}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{dimension.level}</span>
                      <span>{dimension.keyword_matches} 关键词</span>
                    </div>
                  </div>

                  <button
                    onClick={() => toggleDimensionExpanded(dimension.dimension)}
                    className="w-full text-left text-sm text-blue-600 hover:text-blue-800 transition-colors duration-200"
                  >
                    {expandedDimensions.has(dimension.dimension) ? '收起详情 ▲' : '查看详情 ▼'}
                  </button>

                  {expandedDimensions.has(dimension.dimension) && (
                    <div className="mt-4 space-y-3">
                      {dimension.strengths.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium text-green-700 mb-1">优势</h5>
                          <ul className="text-xs text-green-600 space-y-1">
                            {dimension.strengths.map((strength, index) => (
                              <li key={index}>• {strength}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {dimension.weaknesses.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium text-red-700 mb-1">待改进</h5>
                          <ul className="text-xs text-red-600 space-y-1">
                            {dimension.weaknesses.map((weakness, index) => (
                              <li key={index}>• {weakness}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {dimension.recommendations.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium text-blue-700 mb-1">建议</h5>
                          <ul className="text-xs text-blue-600 space-y-1">
                            {dimension.recommendations.map((recommendation, index) => (
                              <li key={index}>• {recommendation}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 关键洞察 */}
        {activeTab === 'insights' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 关键洞察 */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-900">关键洞察</h4>
                <div className="space-y-3">
                  {reportData.key_insights.map((insight, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <div className="text-blue-500 text-lg">💡</div>
                      <p className="text-sm text-blue-800">{insight}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 改进建议 */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-900">改进建议</h4>
                <div className="space-y-3">
                  {reportData.improvement_suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                      <div className="text-yellow-500 text-lg">📝</div>
                      <p className="text-sm text-yellow-800">{suggestion}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 最终推荐详情 */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 rounded-lg">
              <h4 className="text-lg font-medium text-gray-900 mb-4">最终评估</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">推荐结果</h5>
                  <p className="text-lg font-semibold text-gray-900">{reportData.final_recommendation}</p>
                </div>
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">评估置信度</h5>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-blue-500 h-3 rounded-full"
                        style={{ width: `${reportData.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {Math.round(reportData.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 报告底部信息 */}
      <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>报告生成时间: {new Date(reportData.report_generated_at).toLocaleString('zh-CN')}</span>
          <span>Interview-GPT 评估系统 v1.0</span>
        </div>
      </div>
    </div>
  );
};

export default AssessmentReport; 