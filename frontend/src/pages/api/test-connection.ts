import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // 测试后端连接
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    console.log('Attempting to connect to:', backendUrl);
    
    const response = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // 添加超时
      signal: AbortSignal.timeout(5000)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    res.status(200).json({
      frontend: 'connected',
      backend: data,
      environment: {
        API_URL: process.env.NEXT_PUBLIC_API_URL,
        WS_URL: process.env.NEXT_PUBLIC_WS_URL,
        MINIMAX_CONFIGURED: !!process.env.NEXT_PUBLIC_MINIMAX_API_KEY,
        NODE_ENV: process.env.NODE_ENV
      },
      connection_test: {
        url: `${backendUrl}/health`,
        status: response.status,
        ok: response.ok
      }
    });
  } catch (error) {
    console.error('Connection test failed:', error);
    res.status(500).json({
      error: 'Connection failed',
      message: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
      environment: {
        API_URL: process.env.NEXT_PUBLIC_API_URL,
        NODE_ENV: process.env.NODE_ENV
      }
    });
  }
} 