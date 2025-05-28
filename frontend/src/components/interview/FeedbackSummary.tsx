/**
 * 面试反馈摘要组件
 * 用于展示面试结束后的总体评价和评分
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';
import Card from '../common/Card';

export interface FeedbackSummaryProps {
  /** 总体评分 */
  overallScore: number;
  /** 总体评价 */
  summary: string;
  /** 优势列表 */
  strengths: string[];
  /** 改进建议列表 */
  improvements: string[];
  /** 自定义类名 */
  className?: string;
}

/**
 * 面试反馈摘要组件
 * 展示面试的总体评分、评价和关键建议
 */
const FeedbackSummary: React.FC<FeedbackSummaryProps> = ({
  overallScore,
  summary,
  strengths,
  improvements,
  className
}) => {
  // 根据分数确定评分等级和颜色
  const getScoreLevel = (score: number) => {
    if (score >= 90) return { level: '优秀', color: 'bg-green-500' };
    if (score >= 80) return { level: '良好', color: 'bg-blue-500' };
    if (score >= 70) return { level: '一般', color: 'bg-yellow-500' };
    if (score >= 60) return { level: '待提高', color: 'bg-orange-500' };
    return { level: '不及格', color: 'bg-red-500' };
  };

  const { level, color } = getScoreLevel(overallScore);

  return (
    <Card 
      title="面试评估摘要" 
      className={twMerge('mb-6', className)}
    >
      <div className="space-y-6">
        {/* 总体评分 */}
        <div className="flex items-center">
          <div className="mr-4">
            <div className="relative h-28 w-28 flex items-center justify-center">
              {/* 环形进度条 */}
              <svg className="absolute inset-0" width="112" height="112" viewBox="0 0 112 112">
                <circle
                  className="text-gray-200"
                  strokeWidth="8"
                  stroke="currentColor"
                  fill="transparent"
                  r="48"
                  cx="56"
                  cy="56"
                />
                <circle
                  className={twMerge('text-blue-600', color.replace('bg-', 'text-'))}
                  strokeWidth="8"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="transparent"
                  r="48"
                  cx="56"
                  cy="56"
                  strokeDasharray={`${overallScore * 3}, 300`}
                  transform="rotate(-90 56 56)"
                />
              </svg>
              {/* 分数 */}
              <div className="text-center">
                <div className="text-3xl font-bold">{overallScore}</div>
                <div className="text-sm text-gray-500">总分</div>
              </div>
            </div>
          </div>
          
          <div className="flex-grow">
            <div className="mb-1">
              <span className={twMerge(
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                color.replace('bg-', 'bg-') + ' text-white'
              )}>
                {level}
              </span>
            </div>
            <p className="text-gray-700 whitespace-pre-wrap">{summary}</p>
          </div>
        </div>

        {/* 优势与改进 */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* 优势 */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
              <svg className="h-5 w-5 text-green-500 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              优势
            </h4>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="flex">
                  <span className="text-green-500 mr-2">•</span>
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 改进建议 */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
              <svg className="h-5 w-5 text-blue-500 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v2a1 1 0 102 0V5zm-1 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
              改进建议
            </h4>
            <ul className="space-y-2">
              {improvements.map((improvement, index) => (
                <li key={index} className="flex">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>{improvement}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default FeedbackSummary;
