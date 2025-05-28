"""
文件上传服务
处理简历文件的上传、验证、存储和管理
"""
import os
import uuid
import logging
import aiofiles
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib
import mimetypes

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from ..utils.exceptions import ValidationError, FileProcessingError
from ..config.settings import settings
from .resume_parser import resume_parser

# 设置日志
logger = logging.getLogger(__name__)

class FileUploadService:
    """
    文件上传服务
    处理简历文件的上传、验证和存储
    """
    
    def __init__(self):
        """初始化文件上传服务"""
        # 支持的文件类型
        self.supported_types = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/msword': 'doc',
            'text/plain': 'txt',
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/tiff': 'tiff'
        }
        
        # 文件大小限制（字节）
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # 上传目录
        self.upload_dir = Path("uploads/resumes")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_resume(
        self, 
        file: UploadFile, 
        interview_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        上传简历文件
        
        Args:
            file: 上传的文件对象
            interview_id: 面试ID（可选）
            user_id: 用户ID（可选）
            
        Returns:
            Dict[str, Any]: 上传结果和解析信息
        """
        logger.info(f"开始上传简历文件: {file.filename}")
        
        # 验证文件
        await self._validate_file(file)
        
        try:
            # 生成唯一文件名
            file_info = await self._generate_file_info(file, interview_id, user_id)
            
            # 保存文件
            file_path = await self._save_file(file, file_info['filename'])
            
            # 解析简历内容
            parsed_resume = await resume_parser.parse_resume(file_path)
            
            # 生成文件哈希（用于去重）
            file_hash = await self._calculate_file_hash(file_path)
            
            # 构建返回结果
            result = {
                'file_info': {
                    'original_filename': file.filename,
                    'saved_filename': file_info['filename'],
                    'file_path': str(file_path),
                    'file_size': file_info['file_size'],
                    'file_type': file_info['file_type'],
                    'mime_type': file.content_type,
                    'file_hash': file_hash,
                    'upload_time': datetime.utcnow().isoformat(),
                    'interview_id': interview_id,
                    'user_id': user_id
                },
                'parsed_resume': parsed_resume,
                'upload_status': 'success'
            }
            
            logger.info(f"简历上传成功: {file.filename} -> {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"简历上传失败: {file.filename}, 错误: {str(e)}")
            raise FileProcessingError(f"文件上传失败: {str(e)}")
    
    async def _validate_file(self, file: UploadFile) -> None:
        """验证上传的文件"""
        # 检查文件名
        if not file.filename:
            raise ValidationError("文件名不能为空")
        
        # 检查文件类型
        if file.content_type not in self.supported_types:
            supported_formats = ', '.join(self.supported_types.values())
            raise ValidationError(f"不支持的文件格式。支持的格式: {supported_formats}")
        
        # 检查文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到文件开头
        
        if file_size > self.max_file_size:
            max_size_mb = self.max_file_size / (1024 * 1024)
            raise ValidationError(f"文件大小超过限制。最大允许: {max_size_mb}MB")
        
        if file_size == 0:
            raise ValidationError("文件不能为空")
    
    async def _generate_file_info(
        self, 
        file: UploadFile, 
        interview_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """生成文件信息"""
        # 获取文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        if not file_extension:
            file_extension = '.' + self.supported_types.get(file.content_type, 'bin')
        
        # 生成唯一文件名
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # 构建文件名：时间戳_唯一ID_面试ID_用户ID.扩展名
        filename_parts = [timestamp, unique_id]
        if interview_id:
            filename_parts.append(f"interview_{interview_id}")
        if user_id:
            filename_parts.append(f"user_{user_id}")
        
        filename = "_".join(filename_parts) + file_extension
        
        # 获取文件大小
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        return {
            'filename': filename,
            'file_size': file_size,
            'file_type': self.supported_types.get(file.content_type, 'unknown'),
            'original_name': file.filename
        }
    
    async def _save_file(self, file: UploadFile, filename: str) -> Path:
        """保存文件到磁盘"""
        file_path = self.upload_dir / filename
        
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                # 分块读取和写入文件
                while chunk := await file.read(8192):  # 8KB chunks
                    await f.write(chunk)
            
            return file_path
            
        except Exception as e:
            # 如果保存失败，清理可能创建的文件
            if file_path.exists():
                file_path.unlink()
            raise FileProcessingError(f"文件保存失败: {str(e)}")
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.warning(f"计算文件哈希失败: {e}")
            return ""
    
    async def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"文件删除成功: {file_path}")
                return True
            else:
                logger.warning(f"文件不存在: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"文件删除失败: {file_path}, 错误: {str(e)}")
            return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            mime_type, _ = mimetypes.guess_type(str(path))
            
            return {
                'filename': path.name,
                'file_path': str(path),
                'file_size': stat.st_size,
                'mime_type': mime_type,
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {file_path}, 错误: {str(e)}")
            return None
    
    async def list_uploaded_files(
        self, 
        interview_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """列出上传的文件"""
        try:
            files = []
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    # 检查文件名是否匹配条件
                    filename = file_path.name
                    
                    # 如果指定了interview_id，检查文件名是否包含
                    if interview_id and f"interview_{interview_id}" not in filename:
                        continue
                    
                    # 如果指定了user_id，检查文件名是否包含
                    if user_id and f"user_{user_id}" not in filename:
                        continue
                    
                    file_info = await self.get_file_info(str(file_path))
                    if file_info:
                        files.append(file_info)
            
            # 按修改时间排序（最新的在前）
            files.sort(key=lambda x: x['modified_time'], reverse=True)
            
            return files
            
        except Exception as e:
            logger.error(f"列出文件失败: {str(e)}")
            return []
    
    async def validate_resume_content(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """验证简历内容的完整性和质量"""
        validation_result = {
            'is_valid': True,
            'score': 0,
            'issues': [],
            'suggestions': []
        }
        
        # 检查必要信息
        personal_info = parsed_resume.get('personal_info', {})
        
        # 检查姓名
        if not personal_info.get('name'):
            validation_result['issues'].append("缺少姓名信息")
            validation_result['suggestions'].append("请确保简历中包含您的姓名")
        
        # 检查联系方式
        if not personal_info.get('email') and not personal_info.get('phone'):
            validation_result['issues'].append("缺少联系方式")
            validation_result['suggestions'].append("请添加邮箱或电话号码")
        
        # 检查工作经验
        work_experience = parsed_resume.get('work_experience', [])
        if not work_experience:
            validation_result['issues'].append("缺少工作经验")
            validation_result['suggestions'].append("请添加相关工作经验")
        
        # 检查技能信息
        skills = parsed_resume.get('skills', {})
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        if total_skills == 0:
            validation_result['issues'].append("缺少技能信息")
            validation_result['suggestions'].append("请添加相关技能和技术栈")
        
        # 检查教育背景
        education = parsed_resume.get('education', [])
        if not education:
            validation_result['issues'].append("缺少教育背景")
            validation_result['suggestions'].append("请添加教育经历")
        
        # 计算质量分数
        summary = parsed_resume.get('summary', {})
        base_score = summary.get('quality_score', 0)
        
        # 根据问题数量调整分数
        issue_penalty = len(validation_result['issues']) * 10
        validation_result['score'] = max(0, base_score - issue_penalty)
        
        # 判断是否有效
        validation_result['is_valid'] = len(validation_result['issues']) <= 2 and validation_result['score'] >= 50
        
        return validation_result


# 全局文件上传服务实例
file_upload_service = FileUploadService() 