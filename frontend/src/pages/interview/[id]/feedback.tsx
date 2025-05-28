import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Link from 'next/link';

/**
 * 面试反馈页面
 * 显示面试评估结果、技能评分和改进建议
 */
export default function InterviewFeedback() {
  const router = useRouter();
  const { id } = router.query;
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 模拟获取面试反馈数据
  useEffect(() => {
    if (id) {
      // 模拟API调用延迟
      const timer = setTimeout(() => {
        // 模拟反馈数据
        const mockFeedback: InterviewFeedback = {
          interviewId: id as string,
          overallScore: 85,
          summary: '总体表现良好，技术知识扎实，沟通能力出色。在压力情境下能保持冷静，并提供结构化的回答。有进一步提升空间的领域包括项目管理经验和系统设计能力。',
          skillScores: [
            { name: '技术知识', score: 88, feedback: '对核心技术概念理解深刻，能够清晰解释复杂问题。' },
            { name: '问题解决', score: 85, feedback: '能够分析问题并提供合理解决方案，但有时缺乏对边缘情况的考虑。' },
            { name: '沟通表达', score: 90, feedback: '表达清晰，回答有条理，能够使用恰当的技术术语。' },
            { name: '团队协作', score: 82, feedback: '表现出良好的团队意识，但在冲突处理案例中可以更加主动。' },
            { name: '学习能力', score: 87, feedback: '展示了快速学习新概念的能力，对新技术保持开放态度。' },
          ],
          strengths: [
            '技术基础知识扎实，对所用技术栈有深入理解',
            '沟通清晰，能够将复杂概念简化解释',
            '解决问题的思路清晰，能够系统性分析问题',
          ],
          improvements: [
            '可以加强系统设计方面的经验和知识',
            '在讨论项目经验时可以更加突出个人贡献',
            '进一步提升处理高压和模糊需求的能力',
          ],
          interviewerFeedback: [
            {
              interviewerId: 'technical',
              name: '张工',
              role: '技术面试官',
              feedback: '候选人技术基础扎实，能够清晰解释所使用的技术和解决方案。在算法问题上表现出良好的逻辑思维，但在系统设计方面需要更多经验。',
            },
            {
              interviewerId: 'hr',
              name: '李萍',
              role: 'HR面试官',
              feedback: '候选人表现出良好的沟通能力和职业素养，对公司文化和团队协作有正确的认识。职业规划清晰，与岗位匹配度高。',
            },
            {
              interviewerId: 'behavioral',
              name: '王总',
              role: '行为面试官',
              feedback: '候选人在压力情境下保持冷静，能够给出结构化的回答。展示了良好的团队合作精神，但在处理冲突的例子中可以更加主动。',
            },
          ],
        };
        
        setFeedback(mockFeedback);
        setIsLoading(false);
      }, 1500);
      
      return () => clearTimeout(timer);
    }
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <h2 className="text-xl font-semibold">正在生成面试评估报告...</h2>
          <p className="text-gray-400 mt-2">我们正在分析您的表现，请稍候...</p>
        </div>
      </div>
    );
  }

  if (!feedback) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <svg className="h-16 w-16 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-xl font-semibold">无法加载面试反馈</h2>
          <p className="text-gray-400 mt-2">请稍后再试或联系支持团队</p>
          <Link href="/" className="mt-6 inline-block bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg">
            返回首页
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Head>
        <title>面试评估报告 | Interview-GPT</title>
        <meta name="description" content="面试评估报告和反馈" />
      </Head>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <Link href="/" className="inline-flex items-center text-blue-400 hover:text-blue-300">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            返回首页
          </Link>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zm0 8H7v4h6v-4z" clipRule="evenodd" />
            </svg>
            打印报告
          </button>
        </div>

        <div className="bg-gray-800 rounded-xl p-8 shadow-lg animate-fadeIn">
          <h1 className="text-3xl font-bold mb-2 text-center">面试评估报告</h1>
          <p className="text-gray-400 text-center mb-8">面试ID: {feedback.interviewId}</p>

          <div className="flex justify-center mb-10">
            <div className="relative w-48 h-48">
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-4xl font-bold">{feedback.overallScore}</span>
              </div>
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#1f2937"
                  strokeWidth="10"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={getScoreColor(feedback.overallScore)}
                  strokeWidth="10"
                  strokeDasharray={`${2 * Math.PI * 45 * feedback.overallScore / 100} ${2 * Math.PI * 45 * (1 - feedback.overallScore / 100)}`}
                />
              </svg>
            </div>
          </div>

          <div className="mb-10">
            <h2 className="text-2xl font-semibold mb-4">总体评价</h2>
            <p className="text-gray-300 leading-relaxed">{feedback.summary}</p>
          </div>

          <div className="mb-10">
            <h2 className="text-2xl font-semibold mb-6">技能评分</h2>
            <div className="space-y-6">
              {feedback.skillScores.map((skill, index) => (
                <div key={index}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium">{skill.name}</span>
                    <span className={`font-bold ${getScoreTextColor(skill.score)}`}>{skill.score}分</span>
                  </div>
                  <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getScoreBarColor(skill.score)}`}
                      style={{ width: `${skill.score}%` }}
                    ></div>
                  </div>
                  <p className="text-gray-400 text-sm mt-2">{skill.feedback}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-10">
            <div>
              <h2 className="text-2xl font-semibold mb-4">优势</h2>
              <ul className="space-y-2">
                {feedback.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-300">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="text-2xl font-semibold mb-4">改进建议</h2>
              <ul className="space-y-2">
                {feedback.improvements.map((improvement, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="h-5 w-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <span className="text-gray-300">{improvement}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-2xl font-semibold mb-6">面试官评价</h2>
            <div className="space-y-6">
              {feedback.interviewerFeedback.map((interviewer, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <div className="w-12 h-12 bg-gray-600 rounded-full mr-4 flex-shrink-0"></div>
                    <div>
                      <h3 className="font-semibold">{interviewer.name}</h3>
                      <p className="text-sm text-gray-400">{interviewer.role}</p>
                    </div>
                  </div>
                  <p className="text-gray-300">{interviewer.feedback}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="text-center mt-12">
            <Link 
              href="/interview/new"
              className="bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-lg font-medium inline-block"
            >
              开始新的模拟面试
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// 辅助函数
function getScoreColor(score: number): string {
  if (score >= 90) return '#10B981'; // 绿色
  if (score >= 80) return '#3B82F6'; // 蓝色
  if (score >= 70) return '#F59E0B'; // 黄色
  if (score >= 60) return '#F97316'; // 橙色
  return '#EF4444'; // 红色
}

function getScoreBarColor(score: number): string {
  if (score >= 90) return 'bg-green-500';
  if (score >= 80) return 'bg-blue-500';
  if (score >= 70) return 'bg-yellow-500';
  if (score >= 60) return 'bg-orange-500';
  return 'bg-red-500';
}

function getScoreTextColor(score: number): string {
  if (score >= 90) return 'text-green-500';
  if (score >= 80) return 'text-blue-500';
  if (score >= 70) return 'text-yellow-500';
  if (score >= 60) return 'text-orange-500';
  return 'text-red-500';
}

// 类型定义
interface InterviewFeedback {
  interviewId: string;
  overallScore: number;
  summary: string;
  skillScores: SkillScore[];
  strengths: string[];
  improvements: string[];
  interviewerFeedback: InterviewerFeedback[];
}

interface SkillScore {
  name: string;
  score: number;
  feedback: string;
}

interface InterviewerFeedback {
  interviewerId: string;
  name: string;
  role: string;
  feedback: string;
}
