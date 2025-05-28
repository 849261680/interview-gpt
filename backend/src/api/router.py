"""
API路由主文件
汇总所有API端点到一个主路由
"""
from fastapi import APIRouter
from .endpoints import interviews, users, feedback, interview_process, speech_processing, interview_feedback, ai_services, interview_chat
from .endpoints import file_upload, assessment, real_time_assessment, assessment_report
from .endpoints import real_mcp_speech  # 添加真实 MCP 语音端点

# 导入 DeepSeek API 路由
from .deepseek import router as deepseek_router
# 暂时禁用WebSocket功能
# from .endpoints import websocket_routes

# 导入语音处理端点
from .endpoints.speech import router as speech_router
from .endpoints.real_mcp_speech import router as real_mcp_speech_router
from .endpoints.true_mcp_speech import router as true_mcp_speech_router

# 导入新的语音API
from .speech import router as new_speech_router

# 创建主路由
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(interview_process.router, prefix="/interview-process", tags=["interview_process"])
api_router.include_router(speech_processing.router, prefix="/interview-process", tags=["speech_processing"])
api_router.include_router(interview_feedback.router, tags=["interview_feedback"])
api_router.include_router(ai_services.router, prefix="/ai-services", tags=["ai_services"])

# 新增功能路由
api_router.include_router(file_upload.router, tags=["file_upload"])
api_router.include_router(assessment.router, tags=["assessment"])

# 面试聊天路由
api_router.include_router(interview_chat.router, prefix="/interview", tags=["interview_chat"])

# 实时评估和报告生成路由
api_router.include_router(real_time_assessment.router, tags=["real_time_assessment"])
api_router.include_router(assessment_report.router, tags=["assessment_report"])

# 真实 MCP 语音处理路由
api_router.include_router(real_mcp_speech_router, tags=["real_mcp_speech"])

# 注册语音路由
api_router.include_router(speech_router)
api_router.include_router(true_mcp_speech_router)

# 新的MiniMax MCP语音API路由
api_router.include_router(new_speech_router, tags=["minimax_mcp_speech"])

# DeepSeek API路由 - 直接完整路径路由方式
api_router.include_router(deepseek_router, tags=["deepseek"], prefix="/deepseek")

# 暂时禁用WebSocket路由
# 注册WebSocket路由 - 不需要前缀，因为WebSocket路由已包含完整路径
# api_router.include_router(websocket_routes.router, tags=["websocket"])
