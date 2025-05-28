/**
 * 技能评分卡片组件
 * 用于展示面试中各项技能的评分和反馈
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';
import Card from '../common/Card';

export interface SkillScore {
  /** 技能名称 */
  name: string;
  /** 技能评分 */
  score: number;
  /** 评价反馈 */
  feedback: string;
}

export interface SkillScoreCardProps {
  /** 技能评分列表 */
  skillScores: SkillScore[];
  /** 卡片标题 */
  title?: string;
  /** 自定义类名 */
  className?: string;
}

/**
 * 技能评分卡片组件
 * 展示面试中对各项技能的评估和反馈
 */
const SkillScoreCard: React.FC<SkillScoreCardProps> = ({
  skillScores,
  title = '技能评估',
  className
}) => {
  // 根据分数获取颜色
  const getColorByScore = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <Card 
      title={title}
      className={twMerge('mb-6', className)}
    >
      <div className="space-y-6">
        {skillScores.map((skill, index) => (
          <div key={index} className="border-b border-gray-200 pb-5 last:border-b-0 last:pb-0">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-lg font-medium text-gray-900">{skill.name}</h4>
              <div className="flex items-center">
                <div className={twMerge(
                  'h-7 w-14 rounded-full flex items-center justify-center text-white text-sm font-medium',
                  getColorByScore(skill.score)
                )}>
                  {skill.score}
                </div>
              </div>
            </div>
            
            {/* 评分进度条 */}
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-3">
              <div
                className={twMerge(
                  'h-2.5 rounded-full',
                  getColorByScore(skill.score)
                )}
                style={{ width: `${skill.score}%` }}
              ></div>
            </div>
            
            {/* 评价反馈 */}
            <p className="text-gray-700">{skill.feedback}</p>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default SkillScoreCard;
