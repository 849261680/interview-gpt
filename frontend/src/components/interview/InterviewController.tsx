/**
 * 面试控制器组件
 * 管理面试流程，处理面试官轮换，和控制面试状态
 */
import React, { useState, useEffect, useCallback } from 'react';
import { twMerge } from 'tailwind-merge';
import Button from '../common/Button';
import InterviewProgress, { InterviewStage } from './InterviewProgress';

export interface InterviewControllerProps {
  /** 面试ID */
  interviewId: number;
  /** 面试状态 */
  status: 'active' | 'completed' | 'cancelled';
  /** 当前面试阶段 */
  currentStage: InterviewStage;
  /** 当前面试进度百分比 */
  progressPercent: number;
  /** 是否可以进入下一阶段 */
  canAdvance: boolean;
  /** 进入下一阶段的回调 */
  onAdvanceStage: () => void;
  /** 结束面试的回调 */
  onEndInterview: () => void;
  /** 自定义类名 */
  className?: string;
}

/**
 * 面试控制器组件
 * 展示面试进度并提供控制面试流程的按钮
 */
const InterviewController: React.FC<InterviewControllerProps> = ({
  interviewId,
  status,
  currentStage,
  progressPercent,
  canAdvance,
  onAdvanceStage,
  onEndInterview,
  className
}) => {
  // 状态
  const [showConfirmEnd, setShowConfirmEnd] = useState(false);
  const [isEnding, setIsEnding] = useState(false);
  const [isAdvancing, setIsAdvancing] = useState(false);

  // 面试是否活跃
  const isActive = status === 'active';

  // 处理进入下一阶段
  const handleAdvanceStage = useCallback(async () => {
    if (!canAdvance || !isActive) return;
    
    try {
      setIsAdvancing(true);
      await onAdvanceStage();
    } catch (error) {
      console.error('切换面试阶段失败:', error);
    } finally {
      setIsAdvancing(false);
    }
  }, [canAdvance, isActive, onAdvanceStage]);

  // 处理结束面试
  const handleEndInterview = useCallback(async () => {
    if (!isActive) return;
    
    try {
      setIsEnding(true);
      await onEndInterview();
      setShowConfirmEnd(false);
    } catch (error) {
      console.error('结束面试失败:', error);
    } finally {
      setIsEnding(false);
    }
  }, [isActive, onEndInterview]);

  // 获取当前阶段描述
  const getStageDescription = (stage: InterviewStage) => {
    switch (stage) {
      case 'resume_analysis':
        return '简历分析阶段：AI正在分析您的简历，为面试做准备';
      case 'hr_interview':
        return 'HR面试阶段：面试官会评估您的职业规划、文化匹配度和沟通能力';
      case 'technical_interview':
        return '技术面试阶段：面试官会评估您的技术知识和解决问题的能力';
      case 'behavioral_interview':
        return '行为面试阶段：面试官会通过您的过往经历评估您的行为模式和团队协作能力';
      case 'interview_evaluation':
        return '评估反馈阶段：系统正在生成您的面试评估报告';
      default:
        return '正在进行面试...';
    }
  };

  return (
    <div className={twMerge('bg-white p-4 rounded-lg border border-gray-200 shadow-sm', className)}>
      {/* 面试进度 */}
      <InterviewProgress
        currentStage={currentStage}
        percentComplete={progressPercent}
      />
      
      {/* 当前阶段描述 */}
      <div className="bg-blue-50 p-3 rounded-lg mb-4">
        <p className="text-sm text-blue-700">{getStageDescription(currentStage)}</p>
      </div>
      
      {/* 控制按钮 */}
      <div className="flex justify-between">
        <div>
          {isActive && (
            <>
              {showConfirmEnd ? (
                <div className="flex space-x-2">
                  <Button
                    variant="danger"
                    onClick={handleEndInterview}
                    isLoading={isEnding}
                    disabled={isEnding}
                  >
                    确认结束
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowConfirmEnd(false)}
                    disabled={isEnding}
                  >
                    取消
                  </Button>
                </div>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => setShowConfirmEnd(true)}
                >
                  结束面试
                </Button>
              )}
            </>
          )}
        </div>
        
        <div>
          {isActive && currentStage !== 'interview_evaluation' && (
            <Button
              onClick={handleAdvanceStage}
              disabled={!canAdvance || isAdvancing}
              isLoading={isAdvancing}
            >
              进入下一阶段
            </Button>
          )}
        </div>
      </div>
      
      {/* 状态提示 */}
      {!isActive && (
        <div className="mt-4 text-center">
          <div className={twMerge(
            'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
            status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          )}>
            {status === 'completed' ? '面试已完成' : '面试已取消'}
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewController;
