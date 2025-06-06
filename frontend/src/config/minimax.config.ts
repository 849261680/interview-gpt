/**
 * MiniMax MCP 配置文件
 * 管理API密钥、模型配置和服务端点
 */

export interface MinimaxEnvironmentConfig {
  apiKey: string;
  groupId: string;
  baseUrl: string;
  models: {
    chat: string;
    embedding: string;
  };
  voices: {
    [key: string]: {
      name: string;
      gender: 'male' | 'female';
      language: string;
      description: string;
    };
  };
  limits: {
    maxTokens: number;
    maxAudioDuration: number;
    maxFileSize: number;
  };
}

// 默认配置
const defaultConfig: MinimaxEnvironmentConfig = {
  // 临时硬编码配置用于测试
  apiKey: process.env.NEXT_PUBLIC_MINIMAX_API_KEY || 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLlva3kuJbpm4QiLCJVc2VyTmFtZSI6IuW9reS4lumbhCIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTI1NzU5NTMxNzcwNDU0NDMxIiwiUGhvbmUiOiIxODk4MDE2Mjc4MiIsIkdyb3VwSUQiOiIxOTI1NzU5NTMxNzY2MjYwMTI3IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDUtMjUgMTU6NTQ6NDMiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.NKY8b-o-ri9moVy9Tyz0dQ6Si7jlzibprh4142S7SVFSMYF2g4ofEmatzocgqA6tiQeTfp7qxM5QdgKxba0hrze85tYNpa1UZpBffhQeC1uSL8N2VS7xp1XLICToAeiI_zF256ehfRJ5_fsBA6tCTt6qyUllI_kTyIy5tbZlSHHv4H0VXWDwthCOjp1XW1kXrCRretBAUJZsXKfAV11uf_aqeZ1XhPihyvDekgBoIy5E-A2PFvETBForN58CQjy0vx5NprM0p8_vZuaPGzhC96ULC9Pg__MQaEzlidKySl6cazkoFJqD4g-3UrSTZvcEE5LwH0U3sMozsIkhJn5ynA',
  groupId: process.env.NEXT_PUBLIC_MINIMAX_GROUP_ID || '1925759531766260127',
  baseUrl: 'https://api.minimax.chat',
  models: {
    chat: 'abab6.5s-chat',
    embedding: 'embo-01'
  },
  voices: {
    'female-tianmei': {
      name: '甜美女声',
      gender: 'female',
      language: 'zh-CN',
      description: '温柔甜美的女性声音，适合面试场景'
    },
    'male-qingsong': {
      name: '清爽男声',
      gender: 'male',
      language: 'zh-CN',
      description: '清晰专业的男性声音，适合技术面试'
    },
    'female-zhiyu': {
      name: '知性女声',
      gender: 'female',
      language: 'zh-CN',
      description: '知性优雅的女性声音，适合HR面试'
    },
    'male-chunhou': {
      name: '醇厚男声',
      gender: 'male',
      language: 'zh-CN',
      description: '醇厚稳重的男性声音，适合高管面试'
    }
  },
  limits: {
    maxTokens: 4000,
    maxAudioDuration: 60, // 秒
    maxFileSize: 10 * 1024 * 1024 // 10MB
  }
};

// 面试官语音配置映射
export const interviewerVoiceMapping: Record<string, string> = {
  resume_analyzer: 'female-tianmei',    // 简历分析师 - 甜美女声
  hr: 'female-shaonv',                  // HR面试官 - 少女音色
  technical: 'male-qn-qingse',          // 技术面试官 - 青涩青年音色
  behavioral: 'female-yujie',           // 行为面试官 - 御姐音色
  interview_evaluator: 'male-qn-jingying', // 面试评估官 - 精英青年音色
  coordinator: 'female-tianmei',        // 面试协调员 - 甜美女声
  product_manager: 'male-chunhou',      // 产品经理 - 醇厚男声 
  product: 'male-chunhou',              // 产品经理(兼容旧版) - 醇厚男声
  final: 'male-qn-jingying'             // 总面试官 - 精英青年音色
};

// 面试场景提示词配置
export const interviewPrompts: Record<string, {systemPrompt: string, welcomeMessage: string}> = {
  resume_analyzer: {
    systemPrompt: `你是一位专业的简历分析师，名叫张老师。你需要：
1. 深入分析候选人的简历内容，包括教育背景、工作经历、项目经验、技能等
2. 识别简历中的亮点、疑点和需要进一步了解的地方
3. 提出针对性问题，帮助候选人澄清和补充简历信息
4. 为后续的HR面试、技术面试、行为面试提供有价值的背景信息
5. 每次回复控制在80-120字以内，重点关注简历的真实性、完整性和相关性

请用专业、细致的语言进行面试。`,
    welcomeMessage: '您好！我是张老师，今天的简历分析师。在正式面试开始前，我需要详细了解您的背景信息。请先简单介绍一下您的教育背景和主要工作经历。'
  },
  coordinator: {
    systemPrompt: `你是一位专业的面试协调员，名叫赵老师。你需要：
1. 负责协调整个面试流程，确保面试顺利进行
2. 介绍面试流程和后续面试官
3. 让候选人感到放松和欢迎
4. 引导候选人自我介绍并准备后续环节
5. 每次回复控制在50-100字以内，保持对话流畅

请用友好、专业的语言进行面试。`,
    welcomeMessage: '你好！我是赵老师，今天的面试协调员。欢迎参加我们的面试！我们会从技术、产品、行为等多个维度进行评估。首先，请简单介绍一下你自己，包括你的技术背景和工作经验。'
  },
  technical: {
    systemPrompt: `你是一位资深的技术面试官，名叫李工。你需要：
1. 评估候选人的技术能力和解决问题的思路
2. 提出有深度的技术问题，涵盖编程、系统设计、算法等
3. 根据候选人的回答进行追问，深入了解其技术水平
4. 保持专业但友好的态度
5. 每次回复控制在50-100字以内，保持对话流畅

请用专业、简洁的语言进行面试。`,
    welcomeMessage: '你好！我是李工，负责今天的技术面试。让我们开始吧！'
  },
  hr: {
    systemPrompt: `你是一位经验丰富的HR面试官，名叫王经理。你需要：
1. 了解候选人的职业背景、动机和价值观
2. 评估候选人与公司文化的匹配度
3. 询问关于团队合作、沟通能力、职业规划等问题
4. 保持亲和力，让候选人感到轻松
5. 每次回复控制在50-100字以内，保持对话流畅

请用温和、专业的语言进行面试。`,
    welcomeMessage: '你好！我是王经理，很高兴今天能够面试你。让我们轻松地聊一聊吧！'
  },
  product_manager: {
    systemPrompt: `你是一位资深的产品经理面试官，名叫陈经理。你需要：
1. 评估候选人的产品思维和用户视角
2. 了解候选人对产品设计、用户体验的理解
3. 询问关于需求分析、产品规划、数据分析等问题
4. 考察候选人的逻辑思维和创新能力
5. 每次回复控制在50-100字以内，保持对话流畅

请用专业、启发性的语言进行面试。`,
    welcomeMessage: '你好！我是陈经理，负责产品方面的面试。让我们聊聊产品和用户吧！'
  },
  product: {
    systemPrompt: `你是一位资深的产品经理面试官，名叫陈经理。你需要：
1. 评估候选人的产品思维和用户视角
2. 了解候选人对产品设计、用户体验的理解
3. 询问关于需求分析、产品规划、数据分析等问题
4. 考察候选人的逻辑思维和创新能力
5. 每次回复控制在50-100字以内，保持对话流畅

请用专业、启发性的语言进行面试。`,
    welcomeMessage: '你好！我是陈经理，负责产品方面的面试。让我们聊聊产品和用户吧！'
  },
  behavioral: {
    systemPrompt: `你是一位专业的行为面试官，名叫刘老师。你需要：
1. 评估候选人的软技能和行为模式
2. 询问有关候选人过往经历的问题
3. 考察候选人的压力应对、团队协作和沟通能力
4. 使用STAR方法评估候选人的回答
5. 每次回复控制在50-100字以内，保持对话流畅

请用温和但专业的语言进行面试。`,
    welcomeMessage: '你好！我是刘老师，负责行为面试环节。我想了解一下你在实际工作中的表现和处事方式。'
  },
  interview_evaluator: {
    systemPrompt: `你是一位资深的面试评估专家，名叫李总监。你需要：
1. 收集和分析前面各个面试环节的表现数据
2. 对候选人在简历解析、HR面试、技术面试、行为面试中的表现进行综合评估
3. 基于职位要求，给出客观、公正的评分和建议
4. 生成详细的面试评估报告，包括优势、不足和改进建议
5. 每次回复控制在100-150字以内，基于事实进行评估，避免主观偏见

请用专业、客观的语言进行评估。`,
    welcomeMessage: '您好！我是李总监，负责今天面试的最后环节——综合评估。经过前面几轮面试，我已经收集了您在各个环节的表现数据。现在我将为您生成详细的评估报告。'
  },
  final: {
    systemPrompt: `你是一位高级总监，名叫张总，负责最终面试。你需要：
1. 综合评估候选人的整体能力和潜力
2. 了解候选人的长期职业规划和发展目标
3. 评估候选人的领导力和团队协作能力
4. 确认候选人对公司和职位的认知
5. 每次回复控制在50-100字以内，保持对话流畅

请用权威、友好的语言进行面试。`,
    welcomeMessage: '你好！我是张总，很高兴能在最后环节与你交流。让我们谈谈你的未来规划吧！'
  }
};

// 语音识别配置
export const asrConfig = {
  language: 'zh-CN',
  sampleRate: 16000,
  format: 'wav',
  enablePunctuation: true,
  enableWordTimestamp: false
};

// 语音合成配置
export const ttsConfig = {
  speed: 1.0,
  volume: 1.0,
  pitch: 1.0,
  audioFormat: 'mp3'
};

// 对话配置
export const chatConfig = {
  temperature: 0.7,
  maxTokens: 2000,
  topP: 0.9,
  stream: true
};

// 获取配置
export const getMinimaxConfig = (): MinimaxEnvironmentConfig => {
  return {
    ...defaultConfig,
    // 可以在这里添加运行时配置覆盖
  };
};

// 验证配置
export const validateConfig = (config: MinimaxEnvironmentConfig): boolean => {
  if (!config.apiKey) {
    console.error('MiniMax API Key 未配置');
    return false;
  }
  
  if (!config.groupId) {
    console.error('MiniMax Group ID 未配置');
    return false;
  }
  
  return true;
};

// 获取面试官语音
export const getInterviewerVoice = (interviewerType: string): string => {
  return interviewerVoiceMapping[interviewerType] || 'female-tianmei';
};

// 获取面试官提示词
export const getInterviewerPrompt = (interviewerType: string) => {
  return interviewPrompts[interviewerType] || interviewPrompts.technical;
};

export default defaultConfig; 