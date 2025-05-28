// 创建文件: /frontend/src/pages/api/real-mcp-speech/text-to-speech.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: '只支持POST请求' })
  }

  try {
    const { text, voice } = req.body

    // 检查必要参数
    if (!text) {
      return res.status(400).json({ error: '缺少必要参数: text' })
    }

    // 代理请求到后端
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    console.log(`[API Proxy] 转发TTS请求到后端: ${backendUrl}/api/real-mcp-speech/text-to-speech`)
    
    const response = await fetch(`${backendUrl}/api/real-mcp-speech/text-to-speech`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(req.body)
    })

    // 获取后端响应
    const data = await response.json()

    // 返回结果
    if (response.ok) {
      return res.status(200).json(data)
    } else {
      console.error('后端API返回错误:', data)
      return res.status(response.status).json(data)
    }
  } catch (error) {
    console.error('API代理错误:', error)
    return res.status(500).json({ error: '语音合成服务暂时不可用', details: error instanceof Error ? error.message : '未知错误' })
  }
}