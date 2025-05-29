/**
 * 前端TTS功能测试脚本
 * 直接测试前端调用后端API的逻辑
 */

async function testFrontendTTS() {
  console.log('🚀 开始测试前端TTS功能...');
  
  // 动态导入fetch
  const { default: fetch } = await import('node-fetch');
  
  const testCases = [
    {
      name: '基础TTS测试',
      data: {
        text: '你好，这是前端TTS测试',
        voice_id: 'female-tianmei',
        service: 'minimax'
      }
    },
    {
      name: '技术面试官语音测试',
      data: {
        text: '让我们开始技术面试，请介绍一下你的技术背景',
        voice_id: 'male-qn-qingse',
        service: 'minimax'
      }
    },
    {
      name: 'HR面试官语音测试',
      data: {
        text: '很高兴见到你，让我们轻松地聊一聊',
        voice_id: 'female-shaonv',
        service: 'minimax'
      }
    }
  ];
  
  for (const testCase of testCases) {
    console.log(`\n📋 ${testCase.name}`);
    console.log('-'.repeat(40));
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/api/minimax-tts/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testCase.data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        console.log('✅ 测试成功');
        console.log(`   语音: ${result.voice_used}`);
        console.log(`   服务: ${result.service}`);
        console.log(`   音频URL: ${result.audio_url ? '已生成' : '未生成'}`);
        
        if (result.audio_url) {
          // 验证音频URL是否可访问
          try {
            const audioResponse = await fetch(result.audio_url, { method: 'HEAD' });
            console.log(`   音频可访问: ${audioResponse.ok ? '是' : '否'}`);
          } catch (err) {
            console.log(`   音频可访问: 否 (${err.message})`);
          }
        }
      } else {
        console.log('❌ 测试失败');
        console.log(`   错误: ${result.error || result.message}`);
      }
      
    } catch (error) {
      console.log('❌ 测试异常');
      console.log(`   错误: ${error.message}`);
    }
  }
  
  // 测试服务状态
  console.log(`\n📋 服务状态测试`);
  console.log('-'.repeat(40));
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/api/minimax-tts/status');
    
    if (response.ok) {
      const status = await response.json();
      console.log('✅ 服务状态获取成功');
      console.log(`   MiniMax可用: ${status.minimax?.available ? '是' : '否'}`);
      console.log(`   API密钥配置: ${status.minimax?.api_key_configured ? '是' : '否'}`);
      console.log(`   MCP工具可用: ${status.minimax?.mcp_tools_available ? '是' : '否'}`);
      console.log(`   OpenAI可用: ${status.openai?.available ? '是' : '否'}`);
    } else {
      console.log('❌ 服务状态获取失败');
    }
  } catch (error) {
    console.log('❌ 服务状态测试异常');
    console.log(`   错误: ${error.message}`);
  }
  
  console.log('\n🎉 测试完成');
}

// 运行测试
testFrontendTTS().catch(console.error); 