"""
文件上传服务测试
测试简历上传、解析和验证功能
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi import UploadFile
import io

from src.services.file_upload_service import file_upload_service
from src.services.resume_parser import resume_parser
from src.utils.exceptions import ValidationError, FileProcessingError


class TestFileUploadService:
    """文件上传服务测试"""
    
    @pytest.fixture
    def sample_pdf_content(self):
        """模拟PDF文件内容"""
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    
    @pytest.fixture
    def sample_upload_file(self, sample_pdf_content):
        """创建模拟上传文件"""
        file_obj = io.BytesIO(sample_pdf_content)
        return UploadFile(
            filename="test_resume.pdf",
            file=file_obj,
            content_type="application/pdf"
        )
    
    @pytest.mark.asyncio
    async def test_upload_resume_success(self, sample_upload_file):
        """测试成功上传简历"""
        with patch.object(resume_parser, 'parse_resume') as mock_parse:
            mock_parse.return_value = {
                'personal_info': {'name': '张三', 'email': 'zhangsan@example.com'},
                'skills': {'programming_languages': ['Python', 'Java']},
                'summary': {'quality_score': 85}
            }
            
            result = await file_upload_service.upload_resume(
                file=sample_upload_file,
                interview_id=1,
                user_id=1
            )
            
            assert result['upload_status'] == 'success'
            assert 'file_info' in result
            assert 'parsed_resume' in result
            assert result['file_info']['original_filename'] == 'test_resume.pdf'
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self):
        """测试上传无效文件类型"""
        invalid_file = UploadFile(
            filename="test.exe",
            file=io.BytesIO(b"invalid content"),
            content_type="application/x-executable"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await file_upload_service.upload_resume(invalid_file)
        
        assert "不支持的文件格式" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_upload_empty_file(self):
        """测试上传空文件"""
        empty_file = UploadFile(
            filename="empty.pdf",
            file=io.BytesIO(b""),
            content_type="application/pdf"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await file_upload_service.upload_resume(empty_file)
        
        assert "文件不能为空" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_validate_resume_content(self):
        """测试简历内容验证"""
        parsed_resume = {
            'personal_info': {'name': '张三', 'email': 'zhangsan@example.com'},
            'education': [{'school': '清华大学', 'degree': '学士'}],
            'work_experience': [{'company': 'ABC公司', 'position': '工程师'}],
            'skills': {'programming_languages': ['Python']},
            'summary': {'quality_score': 75}
        }
        
        validation = await file_upload_service.validate_resume_content(parsed_resume)
        
        assert validation['is_valid'] is True
        assert validation['score'] >= 50
        assert isinstance(validation['issues'], list)
        assert isinstance(validation['suggestions'], list)
    
    @pytest.mark.asyncio
    async def test_validate_incomplete_resume(self):
        """测试不完整简历验证"""
        incomplete_resume = {
            'personal_info': {},  # 缺少个人信息
            'education': [],      # 缺少教育背景
            'work_experience': [],  # 缺少工作经验
            'skills': {},         # 缺少技能
            'summary': {'quality_score': 30}
        }
        
        validation = await file_upload_service.validate_resume_content(incomplete_resume)
        
        assert validation['is_valid'] is False
        assert len(validation['issues']) > 0
        assert len(validation['suggestions']) > 0
    
    @pytest.mark.asyncio
    async def test_list_uploaded_files(self):
        """测试列出上传文件"""
        # 创建临时测试文件
        test_dir = Path("uploads/resumes")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / "20231201_123456_interview_1_user_1.pdf"
        test_file.write_text("test content")
        
        try:
            files = await file_upload_service.list_uploaded_files(interview_id=1)
            
            assert isinstance(files, list)
            # 检查是否包含我们创建的测试文件
            file_names = [f['filename'] for f in files]
            assert any("interview_1" in name for name in file_names)
            
        finally:
            # 清理测试文件
            if test_file.exists():
                test_file.unlink()


class TestResumeParser:
    """简历解析器测试"""
    
    @pytest.mark.asyncio
    async def test_parse_text_resume(self):
        """测试解析文本简历"""
        # 创建临时文本文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            张三
            邮箱: zhangsan@example.com
            电话: 13800138000
            
            教育背景:
            2018-2022 清华大学 计算机科学与技术 学士
            
            工作经验:
            2022-2023 ABC科技公司 Python工程师
            
            技能:
            Python, Django, MySQL, Git
            """)
            temp_file = f.name
        
        try:
            result = await resume_parser.parse_resume(temp_file)
            
            assert 'personal_info' in result
            assert 'education' in result
            assert 'work_experience' in result
            assert 'skills' in result
            assert 'summary' in result
            
            # 检查个人信息提取
            personal_info = result['personal_info']
            assert 'zhangsan@example.com' in str(personal_info)
            
            # 检查技能提取
            skills = result['skills']
            assert 'python' in str(skills).lower()
            
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(FileProcessingError) as exc_info:
            await resume_parser.parse_resume("nonexistent_file.pdf")
        
        assert "文件不存在" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_extract_personal_info(self):
        """测试提取个人信息"""
        text = """
        张三
        邮箱: zhangsan@example.com
        电话: 13800138000
        地址: 北京市海淀区
        """
        
        personal_info = await resume_parser._extract_personal_info(text)
        
        assert personal_info.get('email') == 'zhangsan@example.com'
        assert personal_info.get('phone') == '13800138000'
    
    @pytest.mark.asyncio
    async def test_extract_skills(self):
        """测试提取技能"""
        text = """
        技能:
        编程语言: Python, Java, JavaScript
        框架: Django, Spring, React
        数据库: MySQL, PostgreSQL
        工具: Git, Docker
        """
        
        skills = await resume_parser._extract_skills(text)
        
        assert 'python' in skills['programming_languages']
        assert 'django' in skills['frameworks']
        assert 'mysql' in skills['databases']
        assert 'git' in skills['tools']
    
    @pytest.mark.asyncio
    async def test_generate_summary(self):
        """测试生成简历摘要"""
        text = """
        张三，软件工程师，有3年Python开发经验。
        毕业于清华大学计算机科学专业。
        熟悉Django、Flask等Web框架。
        参与过多个大型项目开发。
        联系邮箱: zhangsan@example.com
        电话: 13800138000
        """
        
        summary = await resume_parser._generate_summary(text)
        
        assert summary['word_count'] > 0
        assert summary['character_count'] > 0
        assert summary['quality_score'] > 0
        assert isinstance(summary['completeness'], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 