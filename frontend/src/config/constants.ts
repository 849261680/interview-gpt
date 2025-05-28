/**
 * 应用程序常量配置
 * 包含API地址、超时设置等全局常量
 */

// API基础URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// WebSocket基础URL
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

// API请求超时时间（毫秒）
export const API_TIMEOUT = 30000;

// 面试官类型
export const INTERVIEWER_TYPES = {
  TECHNICAL: 'technical',
  HR: 'hr',
  PRODUCT_MANAGER: 'product_manager',
  BEHAVIORAL: 'behavioral',
  SENIOR: 'senior'
};

// 面试阶段
export const INTERVIEW_STAGES = {
  INTRODUCTION: 'introduction',
  TECHNICAL: 'technical',
  HR: 'hr',
  PRODUCT_MANAGER: 'product_manager',
  BEHAVIORAL: 'behavioral',
  SENIOR: 'senior',
  CONCLUSION: 'conclusion',
  FEEDBACK: 'feedback'
};

// 面试状态
export const INTERVIEW_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
};

// 岗位列表
export const JOB_POSITIONS = [
  { id: 'ai_engineer', name: 'AI应用工程师' },
  { id: 'frontend_engineer', name: '前端工程师' },
  { id: 'backend_engineer', name: '后端工程师' },
  { id: 'fullstack_engineer', name: '全栈工程师' },
  { id: 'product_manager', name: '产品经理' },
  { id: 'data_scientist', name: '数据科学家' },
  { id: 'marketing_specialist', name: '市场营销专员' },
  { id: 'operations_manager', name: '运营经理' }
];

// 面试难度
export const DIFFICULTY_LEVELS = [
  { id: 'easy', name: '初级' },
  { id: 'medium', name: '中级' },
  { id: 'hard', name: '高级' }
];

// 本地存储键
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'interview_gpt_auth_token',
  USER_INFO: 'interview_gpt_user_info',
  INTERVIEW_HISTORY: 'interview_gpt_history'
};
