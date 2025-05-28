/**
 * 面试相关类型定义
 */

// 面试信息
export interface InterviewInfo {
  id: number;
  position: string;
  candidate_name: string;
  status: 'pending' | 'in_progress' | 'completed';
  created_at: string;
}

// 面试消息
export interface InterviewMessage {
  id: number;
  content: string;
  sender_type: 'user' | 'interviewer' | 'system';
  interviewer_id?: string;
  timestamp: string;
}

// 技术面试官反馈
export interface TechnicalFeedback {
  technical_knowledge_score: number;
  problem_solving_score: number;
  code_quality_score: number;
  system_design_score: number;
  learning_ability_score: number;
  strengths: string[];
  improvements: string[];
  overall_comments: string;
}

// HR面试官反馈
export interface HRFeedback {
  professional_quality_score: number;
  cultural_fit_score: number;
  communication_score: number;
  career_development_score: number;
  stability_score: number;
  strengths: string[];
  improvements: string[];
  overall_comments: string;
}

// 产品经理面试官反馈
export interface ProductManagerFeedback {
  product_thinking_score: number;
  user_perspective_score: number;
  cross_functional_score: number;
  business_value_score: number;
  decision_making_score: number;
  strengths: string[];
  improvements: string[];
  overall_comments: string;
}

// 行为面试官反馈
export interface BehavioralFeedback {
  teamwork_score: number;
  leadership_score: number;
  communication_score: number;
  problem_solving_score: number;
  adaptability_score: number;
  strengths: string[];
  improvements: string[];
  overall_comments: string;
}

// 最终评估报告
export interface FinalAssessment {
  technical_score: number;
  professional_score: number;
  product_thinking_score: number;
  behavioral_score: number;
  culture_fit_score: number;
  total_score: number;
  recommendation: '强烈推荐' | '推荐' | '待定' | '不推荐';
  strengths: string[];
  improvements: string[];
  recommended_position: string;
  overall_assessment: string;
  improvement_advice: string;
}

// 面试反馈数据
export interface InterviewFeedback {
  interview_id: number;
  position: string;
  candidate_name: string;
  duration: number;
  interview_date: string;
  feedback_by_interviewer: {
    technical?: TechnicalFeedback;
    hr?: HRFeedback;
    product_manager?: ProductManagerFeedback;
    behavioral?: BehavioralFeedback;
  };
  final_assessment: FinalAssessment;
}

// 面试阶段定义
export interface InterviewStage {
  id: string;
  name: string;
  description: string;
  interviewer_id: string;
  max_messages: number;
  next_stage: string | null;
}

// 面试配置
export interface InterviewConfig {
  position: string;
  resume_text?: string;
  difficulty_level: 'easy' | 'medium' | 'hard';
  focus_areas?: string[];
}
