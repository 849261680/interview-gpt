import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: '只支持POST请求' })
  }

  try {
    const { audio_data, format } = req.body

    // 检查必要参数
    if (!audio_data) {
      return res.status(400).json({ error: '缺少必要参数: audio_data' })
    }

    // 代理请求到后端
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    console.log(`[API Proxy] 转发ASR请求到后端: ${backendUrl}/api/real-mcp-speech/speech-to-text`)
    
    const response = await fetch(`${backendUrl}/api/real-mcp-speech/speech-to-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(req.body)
    })

    // 获取后端响应
    const data = await response.json()
    console.log(`[API Proxy] 收到后端ASR响应: 状态=${response.status}`)

    // 返回结果
    if (response.ok) {
      return res.status(200).json(data)
    } else {
      console.error('[API Proxy] 后端ASR API返回错误:', data)
      return res.status(response.status).json(data)
    }
  } catch (error) {
    console.error('[API Proxy] ASR API代理错误:', error)
    return res.status(500).json({ 
      error: '语音识别服务暂时不可用', 
      details: error instanceof Error ? error.message : '未知错误',
      success: false
    })
  }
}
