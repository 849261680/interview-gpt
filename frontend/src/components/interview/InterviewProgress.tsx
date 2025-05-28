/**
 * 面试进度组件
 * 用于显示面试的当前阶段和整体进度
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';

export type InterviewStage = 'technical' | 'hr' | 'behavioral' | 'feedback';

export interface InterviewProgressProps {
  /** 当前面试阶段 */
  currentStage: InterviewStage;
  /** 完成的百分比 (0-100) */
  percentComplete?: number;
  /** 自定义类名 */
  className?: string;
}

/**
 * 面试进度组件
 * 以步骤条形式展示面试的各个阶段和当前进度
 */
const InterviewProgress: React.FC<InterviewProgressProps> = ({
  currentStage,
  percentComplete = 0,
  className
}) => {
  // 面试阶段配置
  const stages = [
    { id: 'technical', name: '技术面试', icon: 'code' },
    { id: 'hr', name: 'HR面试', icon: 'user' },
    { id: 'behavioral', name: '行为面试', icon: 'users' },
    { id: 'feedback', name: '评估反馈', icon: 'clipboard-check' }
  ];

  // 获取当前阶段索引
  const currentIndex = stages.findIndex(stage => stage.id === currentStage);
  
  // 获取图标
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'code':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        );
      case 'user':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
          </svg>
        );
      case 'users':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
          </svg>
        );
      case 'clipboard-check':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className={twMerge('mb-6', className)}>
      {/* 主要进度条 */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-6">
        <div
          className="bg-blue-600 h-2.5 rounded-full"
          style={{ width: `${percentComplete}%` }}
        ></div>
      </div>

      {/* 步骤指示器 */}
      <div className="relative">
        {/* 连接线 */}
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200 -translate-y-1/2 z-0"></div>
        
        {/* 步骤节点 */}
        <div className="relative z-10 flex justify-between">
          {stages.map((stage, index) => {
            // 计算节点状态
            const isActive = index === currentIndex;
            const isPast = index < currentIndex;
            const isFuture = index > currentIndex;
            
            return (
              <div key={stage.id} className="flex flex-col items-center">
                {/* 节点图标 */}
                <div className={twMerge(
                  'w-10 h-10 rounded-full flex items-center justify-center border-2 mb-2',
                  isPast ? 'bg-blue-100 border-blue-500 text-blue-500' : '',
                  isActive ? 'bg-blue-500 border-blue-500 text-white' : '',
                  isFuture ? 'bg-white border-gray-300 text-gray-400' : ''
                )}>
                  {getIcon(stage.icon)}
                </div>
                
                {/* 节点名称 */}
                <div className={twMerge(
                  'text-sm font-medium',
                  isPast ? 'text-blue-500' : '',
                  isActive ? 'text-blue-700' : '',
                  isFuture ? 'text-gray-500' : ''
                )}>
                  {stage.name}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default InterviewProgress;
