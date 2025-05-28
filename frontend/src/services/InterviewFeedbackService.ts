/**
 * 面试反馈服务
 * 负责获取和处理面试反馈数据
 */
import axios from 'axios';
import { API_BASE_URL } from '../config/constants';
import { InterviewFeedback } from '../types/interview';

/**
 * 获取面试反馈数据
 * @param interviewId 面试ID
 * @returns 面试反馈数据
 */
export const getInterviewFeedback = async (interviewId: string): Promise<InterviewFeedback> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/interviews/${interviewId}/feedback`);
    return response.data;
  } catch (error) {
    console.error('获取面试反馈失败:', error);
    throw error;
  }
};

/**
 * 下载面试反馈报告 (PDF格式)
 * @param interviewId 面试ID
 */
export const downloadFeedbackReport = async (interviewId: string): Promise<void> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/interviews/${interviewId}/feedback/report`, {
      responseType: 'blob'
    });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `面试反馈报告-${interviewId}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('下载面试反馈报告失败:', error);
    throw error;
  }
};

/**
 * 分享面试反馈报告
 * @param interviewId 面试ID
 * @returns 分享链接
 */
export const shareFeedbackReport = async (interviewId: string): Promise<string> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/interviews/${interviewId}/feedback/share`);
    return response.data.shareLink;
  } catch (error) {
    console.error('分享面试反馈报告失败:', error);
    throw error;
  }
};
