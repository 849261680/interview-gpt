/**
 * 面试历史卡片组件
 * 用于在用户仪表板展示过去的面试记录
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import Card from '../common/Card';
import Button from '../common/Button';
import { useRouter } from 'next/router';

export interface InterviewHistoryItem {
  /** 面试ID */
  id: number;
  /** 面试职位 */
  position: string;
  /** 面试难度 */
  difficulty: string;
  /** 面试状态 */
  status: 'active' | 'completed' | 'cancelled';
  /** 面试创建时间 */
  createdAt: Date;
  /** 面试完成时间 */
  completedAt?: Date;
  /** 总体评分 */
  overallScore?: number;
}

export interface InterviewHistoryCardProps {
  /** 面试历史记录 */
  interviews: InterviewHistoryItem[];
  /** 是否显示空状态 */
  showEmptyState?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 面试历史卡片组件
 * 展示用户的面试历史记录，包括状态、分数和操作选项
 */
const InterviewHistoryCard: React.FC<InterviewHistoryCardProps> = ({
  interviews,
  showEmptyState = true,
  className
}) => {
  const router = useRouter();

  // 根据状态获取颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // 根据状态获取文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '进行中';
      case 'completed':
        return '已完成';
      case 'cancelled':
        return '已取消';
      default:
        return '未知状态';
    }
  };

  // 根据难度获取文本
  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return '初级';
      case 'medium':
        return '中级';
      case 'hard':
        return '高级';
      default:
        return '未知难度';
    }
  };

  // 查看面试
  const viewInterview = (id: number) => {
    router.push(`/interview/${id}`);
  };

  // 查看反馈
  const viewFeedback = (id: number) => {
    router.push(`/interview/${id}/feedback`);
  };

  // 继续面试
  const continueInterview = (id: number) => {
    router.push(`/interview/${id}`);
  };

  // 空状态
  if (showEmptyState && interviews.length === 0) {
    return (
      <Card
        title="面试历史"
        className={twMerge('mb-6', className)}
      >
        <div className="text-center py-8">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">暂无面试记录</h3>
          <p className="mt-1 text-sm text-gray-500">开始您的第一次模拟面试，获取专业评估和反馈。</p>
          <div className="mt-6">
            <Button
              onClick={() => router.push('/interview/new')}
              leftIcon={
                <svg className="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
              }
            >
              开始模拟面试
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card
      title="面试历史"
      className={twMerge('mb-6', className)}
      headerRight={
        <Button
          size="sm"
          variant="outline"
          onClick={() => router.push('/interview/new')}
        >
          新建面试
        </Button>
      }
    >
      <div className="overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                职位
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                难度
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                日期
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                评分
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {interviews.map((interview) => (
              <tr key={interview.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{interview.position}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{getDifficultyText(interview.difficulty)}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={twMerge(
                    'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                    getStatusColor(interview.status)
                  )}>
                    {getStatusText(interview.status)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {format(interview.createdAt, 'yyyy-MM-dd HH:mm', { locale: zhCN })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {interview.overallScore ? (
                    <div className="flex items-center">
                      <div className={twMerge(
                        'text-sm font-medium',
                        interview.overallScore >= 80 ? 'text-green-600' :
                          interview.overallScore >= 60 ? 'text-yellow-600' : 'text-red-600'
                      )}>
                        {interview.overallScore}
                      </div>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-400">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-2">
                    {interview.status === 'active' ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => continueInterview(interview.id)}
                      >
                        继续
                      </Button>
                    ) : interview.status === 'completed' ? (
                      <>
                        <Button
                          size="sm"
                          variant="text"
                          onClick={() => viewInterview(interview.id)}
                        >
                          查看
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => viewFeedback(interview.id)}
                        >
                          反馈
                        </Button>
                      </>
                    ) : (
                      <Button
                        size="sm"
                        variant="text"
                        onClick={() => viewInterview(interview.id)}
                      >
                        查看
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default InterviewHistoryCard;
