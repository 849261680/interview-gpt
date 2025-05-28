/**
 * 面试完成模态框组件
 * 当面试完成时显示，提示用户查看反馈结果
 */
import React from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

interface InterviewCompletedModalProps {
  /** 面试ID */
  interviewId: number;
  /** 是否显示 */
  isVisible: boolean;
  /** 关闭回调 */
  onClose: () => void;
}

/**
 * 面试完成模态框
 * 提示用户面试已完成，并引导其查看反馈
 */
const InterviewCompletedModal: React.FC<InterviewCompletedModalProps> = ({
  interviewId,
  isVisible,
  onClose
}) => {
  const router = useRouter();
  
  if (!isVisible) return null;
  
  // 查看反馈
  const handleViewFeedback = () => {
    router.push(`/feedback/${interviewId}`);
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">面试已完成</h2>
          <p className="text-gray-600">
            您已成功完成本次模拟面试！系统正在准备您的详细面试反馈报告，这可能需要几秒钟时间。
          </p>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-lg mb-6">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <p className="text-blue-700 text-sm">
              您的面试反馈报告将包含各个面试官的评估和建议，以及综合评分和改进方向。
            </p>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={handleViewFeedback}
            className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
          >
            查看面试反馈
          </button>
          <Link href="/">
            <a className="w-full py-3 px-4 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg font-medium text-center transition-colors">
              返回首页
            </a>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default InterviewCompletedModal;
