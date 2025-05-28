"""
文件上传API端点
处理简历文件的上传、解析和管理
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from ...db.database import get_db
from ...services.file_upload_service import file_upload_service
from ...services.resume_parser import resume_parser
from ...utils.exceptions import ValidationError, FileProcessingError
from ...models.schemas import Interview

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/files", tags=["文件上传"])


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    interview_id: Optional[int] = Query(None, description="面试ID"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    上传简历文件
    
    Args:
        file: 上传的简历文件
        interview_id: 关联的面试ID（可选）
        user_id: 关联的用户ID（可选）
        db: 数据库会话
        
    Returns:
        上传结果和解析信息
    """
    logger.info(f"接收简历上传请求: {file.filename}")
    
    try:
        # 验证面试ID（如果提供）
        if interview_id:
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise HTTPException(status_code=404, detail=f"面试不存在: ID={interview_id}")
        
        # 上传并解析简历
        result = await file_upload_service.upload_resume(
            file=file,
            interview_id=interview_id,
            user_id=user_id
        )
        
        # 验证简历内容
        validation_result = await file_upload_service.validate_resume_content(
            result['parsed_resume']
        )
        
        # 更新面试记录的简历路径（如果有面试ID）
        if interview_id and interview:
            interview.resume_path = result['file_info']['file_path']
            db.commit()
        
        # 构建响应
        response = {
            "success": True,
            "message": "简历上传成功",
            "data": {
                "file_info": result['file_info'],
                "parsed_resume": result['parsed_resume'],
                "validation": validation_result
            }
        }
        
        logger.info(f"简历上传成功: {file.filename}")
        return JSONResponse(content=response, status_code=200)
        
    except ValidationError as e:
        logger.warning(f"简历上传验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except FileProcessingError as e:
        logger.error(f"简历处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"简历上传异常: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/parse-resume")
async def parse_resume_file(
    file: UploadFile = File(...),
    save_file: bool = Query(False, description="是否保存文件")
):
    """
    解析简历文件（不保存文件）
    
    Args:
        file: 上传的简历文件
        save_file: 是否保存文件到服务器
        
    Returns:
        解析结果
    """
    logger.info(f"接收简历解析请求: {file.filename}")
    
    try:
        if save_file:
            # 保存并解析
            result = await file_upload_service.upload_resume(file=file)
            parsed_resume = result['parsed_resume']
            file_info = result['file_info']
        else:
            # 临时保存并解析，然后删除
            import tempfile
            import os
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # 解析临时文件
                parsed_resume = await resume_parser.parse_resume(temp_file_path)
                file_info = {
                    'original_filename': file.filename,
                    'file_size': len(content),
                    'file_type': file.content_type,
                    'temporary': True
                }
            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        # 验证简历内容
        validation_result = await file_upload_service.validate_resume_content(parsed_resume)
        
        response = {
            "success": True,
            "message": "简历解析成功",
            "data": {
                "file_info": file_info,
                "parsed_resume": parsed_resume,
                "validation": validation_result
            }
        }
        
        logger.info(f"简历解析成功: {file.filename}")
        return JSONResponse(content=response, status_code=200)
        
    except ValidationError as e:
        logger.warning(f"简历解析验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except FileProcessingError as e:
        logger.error(f"简历解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"简历解析异常: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/list")
async def list_uploaded_files(
    interview_id: Optional[int] = Query(None, description="面试ID"),
    user_id: Optional[int] = Query(None, description="用户ID")
):
    """
    列出上传的文件
    
    Args:
        interview_id: 面试ID（可选）
        user_id: 用户ID（可选）
        
    Returns:
        文件列表
    """
    logger.info(f"获取文件列表: interview_id={interview_id}, user_id={user_id}")
    
    try:
        files = await file_upload_service.list_uploaded_files(
            interview_id=interview_id,
            user_id=user_id
        )
        
        response = {
            "success": True,
            "message": "获取文件列表成功",
            "data": {
                "files": files,
                "total": len(files)
            }
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/info/{file_path:path}")
async def get_file_info(file_path: str):
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息
    """
    logger.info(f"获取文件信息: {file_path}")
    
    try:
        file_info = await file_upload_service.get_file_info(file_path)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        response = {
            "success": True,
            "message": "获取文件信息成功",
            "data": file_info
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.delete("/delete/{file_path:path}")
async def delete_file(file_path: str, db: Session = Depends(get_db)):
    """
    删除文件
    
    Args:
        file_path: 文件路径
        db: 数据库会话
        
    Returns:
        删除结果
    """
    logger.info(f"删除文件: {file_path}")
    
    try:
        # 删除文件
        success = await file_upload_service.delete_file(file_path)
        
        if success:
            # 更新相关面试记录
            interviews = db.query(Interview).filter(Interview.resume_path == file_path).all()
            for interview in interviews:
                interview.resume_path = None
            db.commit()
            
            response = {
                "success": True,
                "message": "文件删除成功"
            }
            return JSONResponse(content=response, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="文件不存在或删除失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/validate-resume")
async def validate_resume_content(
    file: UploadFile = File(...),
    position: Optional[str] = Query(None, description="目标职位")
):
    """
    验证简历内容质量
    
    Args:
        file: 简历文件
        position: 目标职位（可选）
        
    Returns:
        验证结果和建议
    """
    logger.info(f"验证简历内容: {file.filename}")
    
    try:
        # 临时解析文件
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 解析简历
            parsed_resume = await resume_parser.parse_resume(temp_file_path)
            
            # 验证内容
            validation_result = await file_upload_service.validate_resume_content(parsed_resume)
            
            # 如果提供了职位，进行职位匹配分析
            if position:
                from ...services.assessment_service import assessment_service
                skill_analysis = await assessment_service._analyze_skill_match(
                    messages=[], 
                    resume_data=parsed_resume, 
                    position=position
                )
                validation_result['position_match'] = skill_analysis
            
        finally:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        response = {
            "success": True,
            "message": "简历验证完成",
            "data": {
                "validation": validation_result,
                "recommendations": await _generate_resume_recommendations(validation_result)
            }
        }
        
        return JSONResponse(content=response, status_code=200)
        
    except Exception as e:
        logger.error(f"简历验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"简历验证失败: {str(e)}")


async def _generate_resume_recommendations(validation_result: dict) -> List[str]:
    """生成简历改进建议"""
    recommendations = []
    
    # 基于验证结果生成建议
    if not validation_result['is_valid']:
        recommendations.extend(validation_result['suggestions'])
    
    # 基于质量分数生成建议
    score = validation_result['score']
    if score < 60:
        recommendations.extend([
            "建议完善个人信息，包括姓名、联系方式等",
            "添加详细的工作经验和项目经历",
            "补充相关技能和技术栈信息",
            "完善教育背景信息"
        ])
    elif score < 80:
        recommendations.extend([
            "可以添加更多具体的项目案例",
            "详细描述工作成果和贡献",
            "补充相关认证和培训经历"
        ])
    
    # 职位匹配建议
    if 'position_match' in validation_result:
        match_data = validation_result['position_match']
        if match_data['skill_gaps']:
            recommendations.append(f"建议补充以下技能: {', '.join(match_data['skill_gaps'][:3])}")
    
    return list(set(recommendations))  # 去重 