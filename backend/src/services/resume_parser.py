"""
简历解析服务
提供简历文件的解析和信息提取功能
"""
import logging
import re
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# 基础依赖
import filetype
from docx import Document
import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)


class ResumeParser:
    """简历解析器"""
    
    def __init__(self):
        """初始化简历解析器"""
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
        logger.info("简历解析器初始化完成")
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件
        
        Args:
            file_path: 简历文件路径
            
        Returns:
            解析结果字典
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 检测文件类型
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 提取文本内容
            text_content = self._extract_text(file_path, file_ext)
            
            # 解析简历信息
            resume_data = self._parse_resume_content(text_content)
            
            # 添加元数据
            resume_data['metadata'] = {
                'file_path': file_path,
                'file_type': file_ext,
                'file_size': os.path.getsize(file_path),
                'text_length': len(text_content)
            }
            
            logger.info(f"简历解析完成: {file_path}")
            return resume_data
            
        except Exception as e:
            logger.error(f"简历解析失败: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _extract_text(self, file_path: str, file_ext: str) -> str:
        """提取文件文本内容"""
        try:
            if file_ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_ext in ['.docx', '.doc']:
                return self._extract_docx_text(file_path)
            elif file_ext == '.txt':
                return self._extract_txt_text(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
                
        except Exception as e:
            logger.error(f"文本提取失败: {e}")
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """提取PDF文本"""
        text = ""
        try:
            # 使用pdfplumber提取文本
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber提取失败，尝试PyPDF2: {e}")
            try:
                # 备用方案：使用PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                logger.error(f"PDF文本提取失败: {e2}")
        
        return text.strip()
    
    def _extract_docx_text(self, file_path: str) -> str:
        """提取DOCX文本"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX文本提取失败: {e}")
            return ""
    
    def _extract_txt_text(self, file_path: str) -> str:
        """提取TXT文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"TXT文本提取失败: {e}")
                return ""
    
    def _parse_resume_content(self, text: str) -> Dict[str, Any]:
        """解析简历内容"""
        if not text:
            return {'success': False, 'error': '无法提取文本内容'}
        
        resume_data = {
            'success': True,
            'raw_text': text,
            'personal_info': self._extract_personal_info(text),
            'education': self._extract_education(text),
            'work_experience': self._extract_work_experience(text),
            'skills': self._extract_skills(text),
            'summary': f"简历包含 {len(text)} 字符"
        }
        
        return resume_data
    
    def _extract_personal_info(self, text: str) -> Dict[str, Any]:
        """提取个人信息"""
        personal_info = {}
        
        # 提取邮箱
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info['email'] = email_match.group(1).strip()
        
        # 提取电话
        phone_pattern = r'(?:电话|手机|Tel|Phone)[：:\s]*([1-9]\d{10})'
        phone_match = re.search(phone_pattern, text, re.IGNORECASE)
        if phone_match:
            personal_info['phone'] = phone_match.group(1).strip()
        
        return personal_info
    
    def _extract_education(self, text: str) -> List[str]:
        """提取教育经历"""
        education = []
        
        # 查找学历关键词
        degrees = ['本科', '硕士', '博士', '学士', 'Bachelor', 'Master', 'PhD']
        for degree in degrees:
            if degree in text:
                education.append(degree)
        
        return education
    
    def _extract_work_experience(self, text: str) -> List[str]:
        """提取工作经历"""
        work_experience = []
        
        # 查找公司关键词
        company_patterns = ['有限公司', '科技', 'Ltd', 'Inc', 'Corp']
        lines = text.split('\n')
        
        for line in lines:
            if any(pattern in line for pattern in company_patterns):
                work_experience.append(line.strip())
        
        return work_experience
    
    def _extract_skills(self, text: str) -> List[str]:
        """提取技能"""
        skills = []
        
        # 常见技术技能
        tech_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Node.js',
            'MySQL', 'MongoDB', 'Docker', 'Git', 'Linux'
        ]
        
        # 在文本中查找技能
        for skill in tech_skills:
            if skill.lower() in text.lower():
                skills.append(skill)
        
        return list(set(skills))  # 去重


# 创建全局实例
resume_parser = ResumeParser() 