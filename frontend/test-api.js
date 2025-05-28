/**
 * 测试 DeepSeek API 连接脚本
 */
const axios = require('axios');

// 测试的API端点 - 使用IPv4地址
const API_URL = 'http://127.0.0.1:8000/api/deepseek/chat';

// 另外测试不带 /api 前缀的地址
const DIRECT_URL = 'http://127.0.0.1:8000/deepseek/chat';

// 测试指定URL
async function testAPI(url, description) {
  console.log(`测试连接到 ${description}: ${url}`);
  
  try {
    const response = await axios.post(url, {
      messages: [
        { role: 'user', content: '你好，请介绍一下自己' }
      ],
      temperature: 0.7,
      max_tokens: 1000
    });
    
    console.log(`${description} 响应状态码:`, response.status);
    console.log(`${description} 响应数据:`, JSON.stringify(response.data, null, 2));
    console.log(`${description} 测试成功! ✅`);
    return true;
  } catch (error) {
    console.error(`${description} 测试失败! ❌`);
    console.error(`${description} 错误信息:`, error.message);
    
    if (error.response) {
      console.error(`${description} 状态码:`, error.response.status);
      console.error(`${description} 响应数据:`, error.response.data);
    } else if (error.request) {
      console.error(`${description} 请求已发送但未收到响应`);
    }
    return false;
  }
}

async function testDeepSeekAPI() {
  console.log('===== 开始测试 DeepSeek API 连接 =====');
  
  // 先测试正确的URL路径
  const apiSuccess = await testAPI(API_URL, '带 /api 前缀的 URL');
  
  // 再测试直接访问的URL
  const directSuccess = await testAPI(DIRECT_URL, '不带 /api 前缀的 URL');
  
  // 输出结论
  if (apiSuccess) {
    console.log('结论: 应使用带 /api 前缀的 URL: ' + API_URL);
  } else if (directSuccess) {
    console.log('结论: 应使用不带 /api 前缀的 URL: ' + DIRECT_URL);
  } else {
    console.log('结论: 两种 URL 均连接失败，请检查后端服务是否正常运行');
  }
}

// 运行测试
testDeepSeekAPI();
