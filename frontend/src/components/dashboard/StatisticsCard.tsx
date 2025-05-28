/**
 * 统计数据卡片组件
 * 用于在用户仪表板展示面试统计数据和图表
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';
import Card from '../common/Card';

export interface StatisticsData {
  /** 总面试次数 */
  totalInterviews: number;
  /** 完成的面试次数 */
  completedInterviews: number;
  /** 平均得分 */
  averageScore: number;
  /** 最高得分 */
  highestScore: number;
  /** 各技能平均得分 */
  skillScores: {
    /** 技能名称 */
    name: string;
    /** 技能平均得分 */
    score: number;
  }[];
}

export interface StatisticsCardProps {
  /** 统计数据 */
  data: StatisticsData;
  /** 自定义类名 */
  className?: string;
}

/**
 * 统计数据卡片组件
 * 展示用户的面试统计数据，包括总体表现和各项技能评分
 */
const StatisticsCard: React.FC<StatisticsCardProps> = ({
  data,
  className
}) => {
  // 根据分数获取颜色
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  // 根据分数获取进度条颜色
  const getProgressColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <Card
      title="面试统计"
      className={twMerge('mb-6', className)}
    >
      {/* 总体统计 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-500 mb-1">总面试次数</div>
          <div className="text-2xl font-bold">{data.totalInterviews}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-500 mb-1">完成率</div>
          <div className="text-2xl font-bold">
            {data.totalInterviews > 0 
              ? `${Math.round((data.completedInterviews / data.totalInterviews) * 100)}%` 
              : '0%'}
          </div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-500 mb-1">平均得分</div>
          <div className={twMerge('text-2xl font-bold', getScoreColor(data.averageScore))}>
            {data.averageScore}
          </div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-500 mb-1">最高得分</div>
          <div className={twMerge('text-2xl font-bold', getScoreColor(data.highestScore))}>
            {data.highestScore}
          </div>
        </div>
      </div>

      {/* 技能评分 */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">技能评分</h3>
        <div className="space-y-4">
          {data.skillScores.map((skill, index) => (
            <div key={index}>
              <div className="flex justify-between mb-1">
                <div className="text-sm font-medium text-gray-700">{skill.name}</div>
                <div className={twMerge('text-sm font-medium', getScoreColor(skill.score))}>
                  {skill.score}
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className={twMerge('h-2.5 rounded-full', getProgressColor(skill.score))}
                  style={{ width: `${skill.score}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 建议和提示 */}
      {data.completedInterviews > 0 && (
        <div className="mt-6 bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-700 mb-2">提升建议</h4>
          <p className="text-sm text-blue-600">
            基于您的面试表现，建议重点提升
            {data.skillScores
              .sort((a, b) => a.score - b.score)
              .slice(0, 2)
              .map(skill => skill.name)
              .join('和')}
            方面的能力。继续参加模拟面试，针对性练习这些方面，将有助于提高您的整体表现。
          </p>
        </div>
      )}
    </Card>
  );
};

export default StatisticsCard;
