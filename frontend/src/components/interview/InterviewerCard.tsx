/**
 * 面试官卡片组件
 * 用于展示当前活跃的面试官信息和状态
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';
import Card from '../common/Card';

export interface Interviewer {
  /** 面试官ID */
  id: string;
  /** 面试官姓名 */
  name: string;
  /** 面试官角色 */
  role: string;
  /** 面试官头像URL */
  avatarUrl?: string;
  /** 面试官描述 */
  description?: string;
}

export interface InterviewerCardProps {
  /** 面试官信息 */
  interviewer: Interviewer;
  /** 是否为当前活跃的面试官 */
  isActive?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 面试官卡片组件
 * 显示面试官的基本信息和当前状态
 */
const InterviewerCard: React.FC<InterviewerCardProps> = ({
  interviewer,
  isActive = false,
  className
}) => {
  // 获取面试官默认头像
  const getDefaultAvatar = (interviewerId: string) => {
    switch (interviewerId) {
      case 'technical':
        return '/images/interviewers/technical.png';
      case 'hr':
        return '/images/interviewers/hr.png';
      case 'behavioral':
        return '/images/interviewers/behavioral.png';
      default:
        return '/images/interviewers/default.png';
    }
  };

  const avatarUrl = interviewer.avatarUrl || getDefaultAvatar(interviewer.id);

  return (
    <Card 
      className={twMerge(
        'transition-all duration-300',
        isActive ? 'border-blue-500 shadow-md' : 'opacity-70',
        className
      )}
    >
      <div className="flex items-center">
        {/* 活跃状态指示器 */}
        {isActive && (
          <div className="absolute top-3 right-3">
            <span className="flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
            </span>
          </div>
        )}

        {/* 面试官头像 */}
        <div className="flex-shrink-0 mr-4">
          <div className={twMerge(
            'h-16 w-16 rounded-full bg-gray-200 overflow-hidden border-2',
            isActive ? 'border-blue-500' : 'border-gray-200'
          )}>
            <img
              src={avatarUrl}
              alt={`${interviewer.name}头像`}
              className="h-full w-full object-cover"
            />
          </div>
        </div>

        {/* 面试官信息 */}
        <div className="flex-grow">
          <h3 className="text-lg font-medium text-gray-900">
            {interviewer.name}
            {isActive && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                当前提问
              </span>
            )}
          </h3>
          <p className="text-sm text-gray-500">{interviewer.role}</p>
          {interviewer.description && (
            <p className="mt-1 text-sm text-gray-600">{interviewer.description}</p>
          )}
        </div>
      </div>
    </Card>
  );
};

export default InterviewerCard;
