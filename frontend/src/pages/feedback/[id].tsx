import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { getInterviewFeedback, downloadFeedbackReport, shareFeedbackReport } from '../../services/InterviewFeedbackService';
import { InterviewFeedback } from '../../types/interview';
import { toast } from 'react-hot-toast';

// 评分展示组件
const ScoreDisplay: React.FC<{ 
  score: number; 
  label: string;
  maxScore?: number;
}> = ({ score, label, maxScore = 5 }) => {
  const percentage = (score / maxScore) * 100;
  
  return (
    <div className="mb-4">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-medium text-gray-700">{score}/{maxScore}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className="bg-blue-600 h-2.5 rounded-full" 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

// 面试官评估卡片组件
const InterviewerFeedbackCard: React.FC<{ 
  title: string;
  feedback: any;
  scores: { label: string; key: string }[];
}> = ({ title, feedback, scores }) => {
  if (!feedback) return null;
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-xl font-bold mb-4 text-gray-800">{title}</h3>
      
      <div className="mb-6">
        {scores.map((score, index) => (
          <ScoreDisplay 
            key={index}
            label={score.label}
            score={feedback[score.key]}
          />
        ))}
      </div>
      
      <div className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2">优势:</h4>
        <ul className="list-disc pl-5 space-y-1">
          {feedback.strengths.map((strength: string, index: number) => (
            <li key={index} className="text-gray-600">{strength}</li>
          ))}
        </ul>
      </div>
      
      <div className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2">改进点:</h4>
        <ul className="list-disc pl-5 space-y-1">
          {feedback.improvements.map((improvement: string, index: number) => (
            <li key={index} className="text-gray-600">{improvement}</li>
          ))}
        </ul>
      </div>
      
      <div>
        <h4 className="font-semibold text-gray-700 mb-2">总体评价:</h4>
        <p className="text-gray-600">{feedback.overall_comments}</p>
      </div>
    </div>
  );
};

// 最终评估卡片组件
const FinalAssessmentCard: React.FC<{ 
  assessment: any
}> = ({ assessment }) => {
  // 决定推荐标签的样式
  const getRecommendationStyle = () => {
    switch (assessment.recommendation) {
      case '强烈推荐':
        return 'bg-green-100 text-green-800';
      case '推荐':
        return 'bg-blue-100 text-blue-800';
      case '待定':
        return 'bg-yellow-100 text-yellow-800';
      case '不推荐':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6 border-t-4 border-indigo-500">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-gray-800">最终评估</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRecommendationStyle()}`}>
          {assessment.recommendation}
        </span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <ScoreDisplay label="技术能力" score={assessment.technical_score} />
          <ScoreDisplay label="专业素养" score={assessment.professional_score} />
          <ScoreDisplay label="产品思维" score={assessment.product_thinking_score} />
        </div>
        <div>
          <ScoreDisplay label="行为表现" score={assessment.behavioral_score} />
          <ScoreDisplay label="文化契合度" score={assessment.culture_fit_score} />
          <ScoreDisplay label="总体评分" score={assessment.total_score} />
        </div>
      </div>
      
      <div className="mb-6">
        <h4 className="font-semibold text-gray-700 mb-2">推荐岗位:</h4>
        <p className="text-gray-600 font-medium">{assessment.recommended_position}</p>
      </div>
      
      <div className="mb-6">
        <h4 className="font-semibold text-gray-700 mb-2">优势:</h4>
        <ul className="list-disc pl-5 space-y-1">
          {assessment.strengths.map((strength: string, index: number) => (
            <li key={index} className="text-gray-600">{strength}</li>
          ))}
        </ul>
      </div>
      
      <div className="mb-6">
        <h4 className="font-semibold text-gray-700 mb-2">改进建议:</h4>
        <ul className="list-disc pl-5 space-y-1">
          {assessment.improvements.map((improvement: string, index: number) => (
            <li key={index} className="text-gray-600">{improvement}</li>
          ))}
        </ul>
      </div>
      
      <div className="p-4 bg-gray-50 rounded-lg mb-6">
        <h4 className="font-semibold text-gray-700 mb-2">成长建议:</h4>
        <p className="text-gray-600">{assessment.improvement_advice}</p>
      </div>
      
      <div>
        <h4 className="font-semibold text-gray-700 mb-2">综合评价:</h4>
        <p className="text-gray-600">{assessment.overall_assessment}</p>
      </div>
    </div>
  );
};

// 面试反馈页面组件
const InterviewFeedbackPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  
  const [loading, setLoading] = useState<boolean>(true);
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('final');
  
  // 获取面试反馈数据
  useEffect(() => {
    const fetchFeedback = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const data = await getInterviewFeedback(id as string);
        setFeedback(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || '获取面试反馈失败');
        toast.error('获取面试反馈失败');
      } finally {
        setLoading(false);
      }
    };
    
    fetchFeedback();
  }, [id]);
  
  // 下载面试报告
  const handleDownloadReport = async () => {
    if (!id) return;
    
    try {
      await downloadFeedbackReport(id as string);
      toast.success('报告下载成功');
    } catch (err) {
      toast.error('报告下载失败');
    }
  };
  
  // 分享面试报告
  const handleShareReport = async () => {
    if (!id) return;
    
    try {
      const shareLink = await shareFeedbackReport(id as string);
      
      // 复制分享链接到剪贴板
      navigator.clipboard.writeText(shareLink);
      toast.success('分享链接已复制到剪贴板');
    } catch (err) {
      toast.error('分享失败');
    }
  };
  
  // 渲染加载状态
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="w-16 h-16 border-t-4 border-blue-500 border-solid rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">正在加载面试反馈...</h2>
        </div>
      </div>
    );
  }
  
  // 渲染错误状态
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center bg-white p-8 rounded-lg shadow-md max-w-md">
          <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">出错了</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link href="/">
            <a className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
              返回首页
            </a>
          </Link>
        </div>
      </div>
    );
  }
  
  // 如果没有反馈数据
  if (!feedback) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center bg-white p-8 rounded-lg shadow-md max-w-md">
          <svg className="w-16 h-16 text-yellow-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">没有找到面试反馈</h2>
          <p className="text-gray-600 mb-4">此面试可能尚未完成或面试反馈尚未生成</p>
          <Link href="/">
            <a className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
              返回首页
            </a>
          </Link>
        </div>
      </div>
    );
  }
  
  return (
    <>
      <Head>
        <title>面试反馈 - Interview GPT</title>
        <meta name="description" content="AI模拟面试反馈报告" />
      </Head>
      
      <div className="min-h-screen bg-gray-100">
        {/* 顶部导航栏 */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center">
                <Link href="/">
                  <a className="text-2xl font-bold text-indigo-600">Interview GPT</a>
                </Link>
              </div>
              <div className="flex space-x-4">
                <button 
                  onClick={handleDownloadReport}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  下载报告
                </button>
                <button 
                  onClick={handleShareReport}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  分享报告
                </button>
              </div>
            </div>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 面试信息 */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{feedback.candidate_name} 的面试反馈</h1>
                <p className="text-gray-600">应聘职位: {feedback.position}</p>
              </div>
              <div className="mt-4 md:mt-0">
                <p className="text-gray-600">面试日期: {new Date(feedback.interview_date).toLocaleDateString()}</p>
                <p className="text-gray-600">面试时长: {Math.floor(feedback.duration / 60)} 分钟</p>
              </div>
            </div>
            
            <div className="bg-indigo-50 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-indigo-500 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <p className="text-indigo-700">
                  此报告由AI面试官生成，基于面试过程中的表现评估。评分范围为1-5分，其中5分为最高。
                </p>
              </div>
            </div>
          </div>
          
          {/* 选项卡导航 */}
          <div className="border-b border-gray-200 mb-8">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('final')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'final'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                最终评估
              </button>
              <button
                onClick={() => setActiveTab('technical')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'technical'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                技术面试
              </button>
              <button
                onClick={() => setActiveTab('hr')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'hr'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                HR面试
              </button>
              <button
                onClick={() => setActiveTab('product')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'product'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                产品面试
              </button>
              <button
                onClick={() => setActiveTab('behavioral')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'behavioral'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                行为面试
              </button>
            </nav>
          </div>
          
          {/* 反馈内容 */}
          <div>
            {activeTab === 'final' && (
              <FinalAssessmentCard assessment={feedback.final_assessment} />
            )}
            
            {activeTab === 'technical' && (
              <InterviewerFeedbackCard 
                title="技术面试反馈"
                feedback={feedback.feedback_by_interviewer.technical}
                scores={[
                  { label: '技术知识', key: 'technical_knowledge_score' },
                  { label: '问题解决能力', key: 'problem_solving_score' },
                  { label: '代码质量', key: 'code_quality_score' },
                  { label: '系统设计', key: 'system_design_score' },
                  { label: '学习能力', key: 'learning_ability_score' }
                ]}
              />
            )}
            
            {activeTab === 'hr' && (
              <InterviewerFeedbackCard 
                title="HR面试反馈"
                feedback={feedback.feedback_by_interviewer.hr}
                scores={[
                  { label: '专业素养', key: 'professional_quality_score' },
                  { label: '文化契合度', key: 'cultural_fit_score' },
                  { label: '沟通能力', key: 'communication_score' },
                  { label: '职业发展', key: 'career_development_score' },
                  { label: '稳定性', key: 'stability_score' }
                ]}
              />
            )}
            
            {activeTab === 'product' && (
              <InterviewerFeedbackCard 
                title="产品面试反馈"
                feedback={feedback.feedback_by_interviewer.product_manager}
                scores={[
                  { label: '产品思维', key: 'product_thinking_score' },
                  { label: '用户视角', key: 'user_perspective_score' },
                  { label: '跨职能沟通', key: 'cross_functional_score' },
                  { label: '业务价值', key: 'business_value_score' },
                  { label: '决策能力', key: 'decision_making_score' }
                ]}
              />
            )}
            
            {activeTab === 'behavioral' && (
              <InterviewerFeedbackCard 
                title="行为面试反馈"
                feedback={feedback.feedback_by_interviewer.behavioral}
                scores={[
                  { label: '团队协作', key: 'teamwork_score' },
                  { label: '领导能力', key: 'leadership_score' },
                  { label: '沟通能力', key: 'communication_score' },
                  { label: '问题解决', key: 'problem_solving_score' },
                  { label: '适应能力', key: 'adaptability_score' }
                ]}
              />
            )}
          </div>
          
          {/* 返回按钮 */}
          <div className="mt-10 flex justify-center">
            <Link href={`/interview/${feedback.interview_id}`}>
              <a className="mr-4 px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                返回面试记录
              </a>
            </Link>
            <Link href="/">
              <a className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
                返回首页
              </a>
            </Link>
          </div>
        </main>
        
        {/* 页脚 */}
        <footer className="bg-white mt-12 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p className="text-center text-gray-500 text-sm">
              © {new Date().getFullYear()} Interview GPT. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
};

export default InterviewFeedbackPage;
