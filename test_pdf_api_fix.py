#!/usr/bin/env python3
"""
PDF简历API测试
通过HTTP API测试PDF简历上传和处理
"""

import requests
import os
import logging
from pathlib import Path
import sqlite3

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_existing_pdf():
    """获取现有的PDF文件"""
    upload_dir = Path("backend/uploads/resumes")
    if upload_dir.exists():
        pdf_files = list(upload_dir.glob("*.pdf"))
        if pdf_files:
            return str(pdf_files[0])
    return None

def check_database_content(interview_id):
    """检查数据库中的简历内容"""
    try:
        # 尝试多个可能的数据库路径
        db_paths = [
            'backend/interview_gpt.db',
            'interview_gpt.db',
            'backend/src/interview_gpt.db'
        ]
        
        conn = None
        for db_path in db_paths:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                logger.info(f"📁 使用数据库: {db_path}")
                break
        
        if not conn:
            logger.error("❌ 找不到数据库文件")
            return False
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT resume_context, resume_path FROM interviews WHERE id = ?",
            (interview_id,)
        )
        result = cursor.fetchone()
        
        if result:
            resume_context, resume_path = result
            logger.info(f"📄 数据库中的简历路径: {resume_path}")
            logger.info(f"📝 数据库中的简历内容长度: {len(resume_context) if resume_context else 0} 字符")
            
            if resume_context:
                logger.info(f"📄 简历内容预览: {resume_context[:200]}...")
                
                # 检查是否包含PDF二进制标识
                if '%PDF-' in resume_context or 'stream' in resume_context:
                    logger.error("❌ 数据库中的简历内容包含PDF二进制标识!")
                    return False
                else:
                    logger.info("✅ 数据库中的简历内容为纯文本")
                    return True
            else:
                logger.error("❌ 数据库中没有简历内容")
                return False
        else:
            logger.error("❌ 数据库中没有找到面试记录")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库查询失败: {e}")
        return False
    finally:
        conn.close()

def test_pdf_upload_api():
    """测试PDF上传API"""
    logger.info("🚀 开始测试PDF简历上传API")
    
    # 获取现有PDF文件
    pdf_path = get_existing_pdf()
    if not pdf_path:
        logger.error("❌ 没有找到可用的PDF文件进行测试")
        return False
    
    logger.info(f"📄 使用PDF文件: {pdf_path}")
    
    try:
        # 准备API请求
        url = "http://localhost:8000/api/interviews/"
        
        # 准备表单数据
        data = {
            'position': 'AI应用工程师',
            'difficulty': 'medium'
        }
        
        # 准备文件
        with open(pdf_path, 'rb') as f:
            files = {
                'resume': (os.path.basename(pdf_path), f, 'application/pdf')
            }
            
            # 发送请求
            logger.info("📤 发送API请求...")
            response = requests.post(url, data=data, files=files)
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            interview_id = result.get('id')
            logger.info(f"✅ API请求成功: 面试ID={interview_id}")
            
            # 检查数据库内容
            logger.info("🔍 检查数据库中的简历内容...")
            db_success = check_database_content(interview_id)
            
            if db_success:
                logger.info("🎉 PDF简历上传和解析成功!")
                return True
            else:
                logger.error("❌ 数据库中的简历内容有问题")
                return False
        else:
            logger.error(f"❌ API请求失败: {response.status_code}")
            logger.error(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到API服务器，请确保后端服务正在运行")
        return False
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")
        return False

def test_binary_vs_text_comparison():
    """测试二进制内容与文本内容的对比"""
    logger.info("🔍 测试二进制内容与文本内容的对比...")
    
    pdf_path = get_existing_pdf()
    if not pdf_path:
        logger.warning("⚠️ 没有PDF文件进行对比测试")
        return
    
    try:
        # 读取PDF二进制内容（错误的方式）
        with open(pdf_path, 'rb') as f:
            binary_content = f.read()
        
        # 尝试直接解码（之前的错误做法）
        try:
            wrong_decoded = binary_content.decode('utf-8', errors='ignore')
            logger.info("❌ 错误方式（直接解码PDF二进制）:")
            logger.info(f"   内容长度: {len(wrong_decoded)} 字符")
            logger.info(f"   内容预览: {wrong_decoded[:100]}...")
            logger.info(f"   包含PDF标识: {'%PDF-' in wrong_decoded}")
            logger.info(f"   会导致API错误: {'是' if '%PDF-' in wrong_decoded else '否'}")
        except Exception as e:
            logger.error(f"❌ 直接解码失败: {e}")
        
        # 使用正确的方式（PDF解析器）
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))
        from services.resume_parser import resume_parser
        
        result = resume_parser.parse_resume(pdf_path)
        if result.get('success', False):
            correct_content = result.get('raw_text', '')
            logger.info("✅ 正确方式（PDF解析器）:")
            logger.info(f"   内容长度: {len(correct_content)} 字符")
            logger.info(f"   内容预览: {correct_content[:100]}...")
            logger.info(f"   包含PDF标识: {'%PDF-' in correct_content}")
            logger.info(f"   会导致API错误: {'否' if '%PDF-' not in correct_content else '是'}")
        else:
            logger.error(f"❌ PDF解析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        logger.error(f"❌ 对比测试失败: {e}")

def main():
    """主函数"""
    logger.info("🚀 开始PDF简历API修复测试")
    
    # 测试1: API上传测试
    logger.info("\n" + "="*50)
    logger.info("测试1: PDF简历API上传测试")
    logger.info("="*50)
    success1 = test_pdf_upload_api()
    
    # 测试2: 二进制vs文本对比
    logger.info("\n" + "="*50)
    logger.info("测试2: 二进制vs文本内容对比")
    logger.info("="*50)
    test_binary_vs_text_comparison()
    
    # 总结
    logger.info("\n" + "="*50)
    logger.info("测试总结")
    logger.info("="*50)
    if success1:
        logger.info("✅ PDF简历API修复成功!")
        logger.info("✅ 修复效果:")
        logger.info("   1. PDF文件正确解析为文本内容")
        logger.info("   2. 数据库中存储的是纯文本，不是二进制")
        logger.info("   3. DeepSeek API将接收到可读的文本内容")
        logger.info("   4. 不再出现HTTP 400 Bad Request错误")
        logger.info("✅ 用户可以正常上传PDF简历进行AI面试!")
    else:
        logger.error("❌ PDF简历API仍有问题")
        logger.error("💡 可能的原因:")
        logger.error("   1. 后端服务未启动")
        logger.error("   2. PDF解析器配置问题")
        logger.error("   3. 数据库连接问题")
    
    return success1

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 