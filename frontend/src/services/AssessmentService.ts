/**
 * 评估服务
 * 封装实时评估和评估报告相关的API调用
 */

export interface StartAssessmentRequest {
  interview_id: number;
  position: string;
  difficulty: string;
  interviewer_type?: string;
}

export interface ProcessMessageRequest {
  interview_id: number;
  message: {
    content: string;
    sender_type: string;
    timestamp: string;
  };
  interviewer_type?: string;
}

export interface GenerateReportRequest {
  interview_id: number;
  candidate_name: string;
  position: string;
  additional_data?: Record<string, any>;
}

export interface AssessmentResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface RealTimeAssessmentData {
  interview_id: number;
  message_count: number;
  current_scores: Record<string, number>;
  overall_score: number;
  engagement_level: number;
  assessment_performed: boolean;
  feedback_provided: boolean;
  assessment?: {
    timestamp: string;
    dimension_scores: Record<string, number>;
    overall_score: number;
    assessment_trend: string;
    performance_level: string;
  };
  feedback?: {
    timestamp: string;
    content: string;
    score: number;
    trend: string;
    type: string;
  };
}

export interface AssessmentSessionSummary {
  interview_id: number;
  duration: number;
  message_count: number;
  final_scores: Record<string, number>;
  overall_score: number;
  assessment_count: number;
  feedback_count: number;
  engagement_level: number;
  performance_trend: string;
}

export interface AssessmentMetrics {
  conversation_metrics: {
    response_times: number[];
    response_lengths: number[];
    engagement_level: number;
    coherence_score: number;
    keyword_matches: Record<string, number>;
  };
  dimension_scores: Record<string, number>;
  assessment_history: Array<{
    timestamp: string;
    interviewer_type: string;
    dimension_scores: Record<string, number>;
    overall_score: number;
    message_count: number;
  }>;
  feedback_history: Array<{
    timestamp: string;
    content: string;
    score: number;
    trend: string;
  }>;
  performance_analysis: {
    total_messages: number;
    user_messages: number;
    interviewer_messages: number;
    session_duration: number;
    average_response_length: number;
  };
}

/**
 * 评估服务类
 * 提供实时评估和评估报告的API接口
 */
export class AssessmentService {
  private baseUrl: string;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  /**
   * 启动实时评估会话
   */
  async startRealTimeAssessment(request: StartAssessmentRequest): Promise<AssessmentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/real-time-assessment/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('启动实时评估失败:', error);
      throw error;
    }
  }

  /**
   * 处理消息并更新实时评估
   */
  async processMessage(request: ProcessMessageRequest): Promise<AssessmentResponse<RealTimeAssessmentData>> {
    try {
      const response = await fetch(`${this.baseUrl}/real-time-assessment/process-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('处理消息失败:', error);
      throw error;
    }
  }

  /**
   * 获取评估会话信息
   */
  async getAssessmentSession(interviewId: number): Promise<AssessmentResponse<AssessmentSessionSummary>> {
    try {
      const response = await fetch(`${this.baseUrl}/real-time-assessment/session/${interviewId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取评估会话失败:', error);
      throw error;
    }
  }

  /**
   * 结束评估会话
   */
  async endAssessmentSession(interviewId: number): Promise<AssessmentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/real-time-assessment/end/${interviewId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('结束评估会话失败:', error);
      throw error;
    }
  }

  /**
   * 获取详细评估指标
   */
  async getAssessmentMetrics(interviewId: number): Promise<{ success: boolean; data: AssessmentMetrics }> {
    try {
      const response = await fetch(`${this.baseUrl}/real-time-assessment/metrics/${interviewId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取评估指标失败:', error);
      throw error;
    }
  }

  /**
   * 生成评估报告
   */
  async generateReport(request: GenerateReportRequest): Promise<AssessmentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment-report/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('生成评估报告失败:', error);
      throw error;
    }
  }

  /**
   * 查看评估报告
   */
  async viewReport(interviewId: number): Promise<{ success: boolean; data: any }> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment-report/view/${interviewId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('查看评估报告失败:', error);
      throw error;
    }
  }

  /**
   * 导出评估报告
   */
  async exportReport(interviewId: number, format: 'json' = 'json'): Promise<Blob> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment-report/export/${interviewId}/${format}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('导出评估报告失败:', error);
      throw error;
    }
  }

  /**
   * 获取报告摘要
   */
  async getReportSummary(interviewId: number): Promise<{ success: boolean; data: any }> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment-report/summary/${interviewId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取报告摘要失败:', error);
      throw error;
    }
  }

  /**
   * 获取维度分析
   */
  async getDimensionAnalysis(interviewId: number): Promise<{ success: boolean; data: any }> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment-report/dimensions/${interviewId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取维度分析失败:', error);
      throw error;
    }
  }

  /**
   * 获取关键洞察
   */
  async getKeyInsights(interviewId: number): Promise<{ success: boolean; data: any }> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment-report/insights/${interviewId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取关键洞察失败:', error);
      throw error;
    }
  }

  /**
   * 检查实时评估服务健康状态
   */
  async checkRealTimeAssessmentHealth(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/real-time-assessment/health`);
      return await response.json();
    } catch (error) {
      console.error('检查实时评估服务健康状态失败:', error);
      throw error;
    }
  }

  /**
   * 检查评估报告服务健康状态
   */
  async checkReportServiceHealth(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment-report/health`);
      return await response.json();
    } catch (error) {
      console.error('检查评估报告服务健康状态失败:', error);
      throw error;
    }
  }

  /**
   * 清理过期会话
   */
  async cleanupExpiredSessions(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/real-time-assessment/cleanup`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('清理过期会话失败:', error);
      throw error;
    }
  }
}

// 创建默认实例
export const assessmentService = new AssessmentService(); 