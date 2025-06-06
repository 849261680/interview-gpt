/**
 * u9762u8bd5u670du52a1
 * u901au8fc7u7edfu4e00u63a5u53e3u8c03u7528u4e0du540cu7684AIu6a21u578bu83b7u53d6u9762u8bd5u95eeu9898u7684u56deu7b54
 */
import deepseekService, { ChatMessage as DeepSeekChatMessage } from './DeepSeekService';
import MinimaxMCPService, { ChatMessage as MinimaxChatMessage } from './MinimaxMCPService';
import { chatConfig } from '../config/minimax.config';

// u5b9au4e49u9762u8bd5u5b98u7c7bu578b
export type InterviewerType = 'technical' | 'hr' | 'product' | 'final';

// u901au7528u6d88u606fu683cu5f0f
export interface Message {
  role: 'user' | 'system' | 'assistant';
  content: string;
}

// u5b9au4e49AIu6a21u578bu7c7bu578b
export type AIModelType = 'deepseek' | 'minimax';

// u9762u8bd5u670du52a1u7c7b
class InterviewService {
  private activeModel: AIModelType = 'deepseek'; // u9ed8u8ba4u4f7fu7528DeepSeek
  
  /**
   * u8bbeu7f6eu6d3bu52a8u6a21u578b
   * @param model u6a21u578bu7c7bu578b
   */
  setActiveModel(model: AIModelType) {
    this.activeModel = model;
    console.log(`u5207u6362u5230${model}u6a21u578b`);
  }
  
  /**
   * u83b7u53d6u5f53u524du6d3bu52a8u6a21u578b
   * @returns u6d3bu52a8u6a21u578bu7c7bu578b
   */
  getActiveModel(): AIModelType {
    return this.activeModel;
  }
  
  /**
   * u4eceu901au7528u6d88u606fu683cu5f0fu8f6cu6362u4e3aDeepSeeku6d88u606fu683cu5f0f
   * @param messages u901au7528u6d88u606fu5217u8868
   * @returns DeepSeeku683cu5f0fu7684u6d88u606fu5217u8868
   */
  private toDeepSeekMessages(messages: Message[]): DeepSeekChatMessage[] {
    return messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
  }
  
  /**
   * u4eceu901au7528u6d88u606fu683cu5f0fu8f6cu6362u4e3aMiniMaxu6d88u606fu683cu5f0f
   * @param messages u901au7528u6d88u606fu5217u8868
   * @returns MiniMaxu683cu5f0fu7684u6d88u606fu5217u8868
   */
  private toMinimaxMessages(messages: Message[]): MinimaxChatMessage[] {
    return messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
  }
  
  /**
   * u83b7u53d6AIu56deu590d
   * @param messages u6d88u606fu5386u53f2
   * @param minimaxService MiniMaxu670du52a1u5b9eu4f8buff08u53efu9009uff0cu53eau6709u5f53u4f7fu7528MiniMaxu6a21u578bu65f6u624du9700u8981uff09
   * @returns u56deu590du7ed3u679cu548cu9519u8befu4fe1u606fuff08u5982u679cu6709uff09
   */
  async getAIResponse(messages: Message[], minimaxService?: MinimaxMCPService | null): Promise<{
    success: boolean;
    content: string;
    error?: string;
  }> {
    try {
      if (this.activeModel === 'deepseek') {
        // u4f7fu7528DeepSeek API
        console.log('u4f7fu7528DeepSeek APIu83b7u53d6u56deu590d...');
        
        const deepseekMessages = this.toDeepSeekMessages(messages);
        const response = await deepseekService.chat(deepseekMessages);
        
        if (!response || !response.success) {
          throw new Error((response && response.error) || 'DeepSeek API\u8c03\u7528\u5931\u8d25');
        }
        
        // 从响应中安全地提取内容
        const content = response.data?.choices?.[0]?.message?.content || '\u62b1\u6b49\uff0c\u9762\u8bd5\u7cfb\u7edf\u6682\u65f6\u65e0\u6cd5\u54cd\u5e94\u3002\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002';
        return {
          success: true,
          content
        };
      } 
      else if (this.activeModel === 'minimax' && minimaxService) {
        // u4f7fu7528MiniMax API
        console.log('u4f7fu7528MiniMax Chatu83b7u53d6u56deu590d...');
        
        const minimaxMessages = this.toMinimaxMessages(messages);
        const response = await minimaxService.chat(minimaxMessages, chatConfig);
        
        // MiniMax的chat方法直接返回ChatResponse，如果出错会抛出异常
        const content = response.content || 'u62b1u6b49uff0cu9762u8bd5u7cfbu7edfu6682u65f6u65e0u6cd5u54cdu5e94u3002u8bf7u7a0du540eu518du8bd5u3002';
        return {
          success: true,
          content
        };
      } 
      else {
        // u6a21u62dfu56deu590duff0cu5f53u670du52a1u4e0du53efu7528u65f6
        const lastUserMessage = messages.findLast(msg => msg.role === 'user')?.content || 'u65e0u6d88u606f';
        return {
          success: true,
          content: `u6a21u62dfu56deu590d: u6211u6536u5230u4e86u60a8u7684u95eeu9898u201c${lastUserMessage.substring(0, 20)}...u201duff0cu4f46u5f53u524du6ca1u6709u53efu7528u7684AIu670du52a1u3002`
        };
      }
    } catch (error: any) {
      console.error('u83b7u53d6AIu56deu590du5931u8d25:', error);
      return {
        success: false,
        content: 'u62b1u6b49uff0cu9762u8bd5u7cfbu7edfu6682u65f6u65e0u6cd5u54cdu5e94u3002u8bf7u7a0du540eu518du8bd5u3002',
        error: error.message || 'u672au77e5u9519u8bef'
      };
    }
  }
}

// u521bu5efau5355u4f8bu5b9eu4f8b
const interviewService = new InterviewService();
export default interviewService;
