#!/usr/bin/env python3
"""
简单的测试API，验证异步处理
"""
from fastapi import FastAPI, BackgroundTasks, Form
import asyncio
import logging
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

async def background_task(task_id: str):
    """后台任务"""
    logger.info(f"后台任务开始: {task_id}")
    await asyncio.sleep(10)  # 模拟长时间运行的任务
    logger.info(f"后台任务完成: {task_id}")

@app.post("/test")
async def test_endpoint(
    background_tasks: BackgroundTasks,
    name: str = Form(...)
):
    """测试端点"""
    start_time = time.time()
    logger.info(f"收到请求: {name}")
    
    # 添加后台任务
    background_tasks.add_task(background_task, f"task_{name}")
    
    end_time = time.time()
    logger.info(f"请求处理完成，耗时: {end_time - start_time:.2f}秒")
    
    return {
        "message": f"Hello {name}",
        "processing_time": end_time - start_time,
        "background_task": "started"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 