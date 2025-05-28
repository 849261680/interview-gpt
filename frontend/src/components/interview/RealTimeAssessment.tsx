/**
 * 实时评估组件
 * 在面试过程中显示实时评分、趋势和反馈
 */
import React, { useState, useEffect, useCallback } from 'react';
import { twMerge } from 'tailwind-merge';

export interface RealTimeAssessmentProps {
  /** 面试ID */
  interviewId: number;
  /** 是否启用实时评估 */
  enabled?: boolean;
  /** 评估更新回调 */
  onAssessmentUpdate?: (assessment: any) => void;
  /** 反馈接收回调 */
  onFeedbackReceived?: (feedback: any) => void;
  /** 自定义类名 */
  className?: string;
}

interface AssessmentData {
  overall_score: number;
  current_scores: Record<string, number>;
  engagement_level: number;
  assessment_trend?: string;
  performance_level?: string;
  feedback?: {
    content: string;
    timestamp: string;
    trend: string;
  };
}

/**
 * 实时评估组件
 * 提供面试过程中的实时评分显示和反馈
 */
const RealTimeAssessment: React.FC<RealTimeAssessmentProps> = ({
  interviewId,
  enabled = true,
  onAssessmentUpdate,
  onFeedbackReceived,
  className
}) => {
  // 状态管理
  const [assessmentData, setAssessmentData] = useState<AssessmentData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [recentFeedback, setRecentFeedback] = useState<string | null>(null);
  const [assessmentHistory, setAssessmentHistory] = useState<any[]>([]);

  // 获取评估数据
  const fetchAssessmentData = useCallback(async () => {
    if (!enabled || !interviewId) return;

    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`/api/real-time-assessment/session/${interviewId}`);
      
      if (!response.ok) {
        throw new Error('获取评估数据失败');
      }

      const result = await response.json();
      
      if (result.success && result.data) {
        const newData: AssessmentData = {
          overall_score: result.data.overall_score || 0,
          current_scores: result.data.final_scores || {},
          engagement_level: result.data.engagement_level || 0,
          assessment_trend: result.data.performance_trend,
          performance_level: getPerformanceLevel(result.data.overall_score || 0)
        };

        setAssessmentData(newData);
        
        if (onAssessmentUpdate) {
          onAssessmentUpdate(newData);
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取评估数据失败';
      setError(errorMsg);
      console.error('获取评估数据失败:', err);
    } finally {
      setIsLoading(false);
    }
  }, [interviewId, enabled, onAssessmentUpdate]);

  // 获取详细指标
  const fetchDetailedMetrics = useCallback(async () => {
    if (!enabled || !interviewId) return;

    try {
      const response = await fetch(`/api/real-time-assessment/metrics/${interviewId}`);
      
      if (response.ok) {
        const result = await response.json();
        
        if (result.success && result.data) {
          setAssessmentHistory(result.data.assessment_history || []);
          
          // 检查是否有新反馈
          const feedbackHistory = result.data.feedback_history || [];
          if (feedbackHistory.length > 0) {
            const latestFeedback = feedbackHistory[feedbackHistory.length - 1];
            setRecentFeedback(latestFeedback.content);
            
            if (onFeedbackReceived) {
              onFeedbackReceived(latestFeedback);
            }
          }
        }
      }
    } catch (err) {
      console.error('获取详细指标失败:', err);
    }
  }, [interviewId, enabled, onFeedbackReceived]);

  // 定期更新评估数据
  useEffect(() => {
    if (!enabled) return;

    // 立即获取一次数据
    fetchAssessmentData();
    fetchDetailedMetrics();

    // 设置定期更新
    const assessmentInterval = setInterval(fetchAssessmentData, 30000); // 30秒更新一次
    const metricsInterval = setInterval(fetchDetailedMetrics, 60000); // 60秒更新一次

    return () => {
      clearInterval(assessmentInterval);
      clearInterval(metricsInterval);
    };
  }, [enabled, fetchAssessmentData, fetchDetailedMetrics]);

  // 获取表现等级
  const getPerformanceLevel = (score: number): string => {
    if (score >= 90) return 'excellent';
    if (score >= 80) return 'good';
    if (score >= 70) return 'average';
    if (score >= 60) return 'below_average';
    return 'poor';
  };

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
  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'improving':
        return (
          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'declining':
        return (
          <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
          </svg>
        );
    }
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

  if (!enabled) {
    return null;
  }

  return (
    <div className={twMerge('bg-white rounded-lg shadow-sm border border-gray-200 p-4', className)}>
      {/* 头部 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <h3 className="text-lg font-medium text-gray-900">实时评估</h3>
        </div>
        
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-blue-600 hover:text-blue-800 transition-colors duration-200"
        >
          {showDetails ? '收起详情' : '查看详情'}
        </button>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-md text-sm mb-4">
          {error}
        </div>
      )}

      {/* 加载状态 */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-600">更新评估数据...</span>
        </div>
      )}

      {/* 评估数据 */}
      {assessmentData && !isLoading && (
        <div className="space-y-4">
          {/* 总体评分 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative w-16 h-16">
                <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-gray-200"
                    stroke="currentColor"
                    strokeWidth="3"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className={getProgressColor(assessmentData.overall_score).replace('bg-', 'text-')}
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    fill="none"
                    strokeDasharray={`${assessmentData.overall_score}, 100`}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={twMerge('text-lg font-bold', getScoreColor(assessmentData.overall_score))}>
                    {Math.round(assessmentData.overall_score)}
                  </span>
                </div>
              </div>
              
              <div>
                <div className="text-sm text-gray-500">总体评分</div>
                <div className="flex items-center space-x-1">
                  <span className="text-lg font-medium text-gray-900">
                    {assessmentData.performance_level === 'excellent' && '优秀'}
                    {assessmentData.performance_level === 'good' && '良好'}
                    {assessmentData.performance_level === 'average' && '一般'}
                    {assessmentData.performance_level === 'below_average' && '待提高'}
                    {assessmentData.performance_level === 'poor' && '需改进'}
                  </span>
                  {getTrendIcon(assessmentData.assessment_trend)}
                </div>
              </div>
            </div>

            {/* 参与度 */}
            <div className="text-right">
              <div className="text-sm text-gray-500">参与度</div>
              <div className={twMerge('text-lg font-medium', getScoreColor(assessmentData.engagement_level))}>
                {Math.round(assessmentData.engagement_level)}%
              </div>
            </div>
          </div>

          {/* 维度评分 */}
          {Object.keys(assessmentData.current_scores).length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">各维度评分</h4>
              <div className="space-y-2">
                {Object.entries(assessmentData.current_scores).map(([dimension, score]) => (
                  <div key={dimension} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{formatDimensionName(dimension)}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className={twMerge('h-2 rounded-full', getProgressColor(score))}
                          style={{ width: `${score}%` }}
                        ></div>
                      </div>
                      <span className={twMerge('text-sm font-medium w-8 text-right', getScoreColor(score))}>
                        {Math.round(score)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 实时反馈 */}
          {recentFeedback && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="text-sm font-medium text-blue-800">实时反馈</div>
                  <div className="text-sm text-blue-700 mt-1">{recentFeedback}</div>
                </div>
              </div>
            </div>
          )}

          {/* 详细信息 */}
          {showDetails && assessmentHistory.length > 0 && (
            <div className="border-t border-gray-200 pt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">评估历史</h4>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {assessmentHistory.slice(-5).map((record, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">
                      {new Date(record.timestamp).toLocaleTimeString('zh-CN', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                    <div className="flex items-center space-x-2">
                      <span className={twMerge('font-medium', getScoreColor(record.overall_score))}>
                        {Math.round(record.overall_score)}
                      </span>
                      <span className="text-gray-400">|</span>
                      <span className="text-gray-600">{record.message_count} 消息</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 提示信息 */}
          <div className="text-xs text-gray-500 text-center">
            评估数据每30秒自动更新
          </div>
        </div>
      )}

      {/* 无数据状态 */}
      {!assessmentData && !isLoading && !error && (
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-500">暂无评估数据</p>
          <p className="text-xs text-gray-400 mt-1">开始面试后将显示实时评估</p>
        </div>
      )}
    </div>
  );
};

export default RealTimeAssessment; 