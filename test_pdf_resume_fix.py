#!/usr/bin/env python3
"""
测试PDF简历解析修复
验证PDF文件能够正确解析为文本，而不是直接传递二进制内容给DeepSeek API
"""

import asyncio
import sys
import os
import tempfile
import logging
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.resume_parser import resume_parser

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_pdf():
    """创建一个测试PDF文件"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            pdf_path = temp_file.name
        
        # 创建PDF内容
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "简历")
        c.drawString(100, 720, "姓名：张三")
        c.drawString(100, 690, "邮箱：zhangsan@example.com")
        c.drawString(100, 660, "电话：13800138000")
        c.drawString(100, 630, "教育背景：")
        c.drawString(120, 600, "清华大学 计算机科学与技术 本科 2018-2022")
        c.drawString(100, 570, "工作经验：")
        c.drawString(120, 540, "腾讯 软件工程师 2022-2024")
        c.drawString(120, 510, "负责微信小程序开发和维护")
        c.drawString(100, 480, "技能：")
        c.drawString(120, 450, "Python, JavaScript, React, Node.js")
        c.save()
        
        logger.info(f"✅ 测试PDF文件创建成功: {pdf_path}")
        return pdf_path
        
    except ImportError:
        logger.warning("⚠️ reportlab未安装，使用现有PDF文件进行测试")
        return None
    except Exception as e:
        logger.error(f"❌ 创建测试PDF失败: {e}")
        return None

def test_pdf_parsing():
    """测试PDF解析功能"""
    logger.info("🔍 开始测试PDF简历解析...")
    
    # 创建测试PDF
    test_pdf_path = create_test_pdf()
    
    if not test_pdf_path:
        # 查找现有的PDF文件
        upload_dir = Path("backend/uploads/resumes")
        if upload_dir.exists():
            pdf_files = list(upload_dir.glob("*.pdf"))
            if pdf_files:
                test_pdf_path = str(pdf_files[0])
                logger.info(f"📄 使用现有PDF文件: {test_pdf_path}")
            else:
                logger.error("❌ 没有找到可用的PDF文件进行测试")
                return False
        else:
            logger.error("❌ 没有找到可用的PDF文件进行测试")
            return False
    
    try:
        # 测试解析
        logger.info(f"📖 开始解析PDF文件: {test_pdf_path}")
        result = resume_parser.parse_resume(test_pdf_path)
        
        if result.get('success', False):
            raw_text = result.get('raw_text', '')
            logger.info(f"✅ PDF解析成功!")
            logger.info(f"📝 提取的文本长度: {len(raw_text)} 字符")
            logger.info(f"📄 文本预览: {raw_text[:200]}...")
            
            # 检查是否包含PDF二进制标识
            if '%PDF-' in raw_text or 'stream' in raw_text or 'endstream' in raw_text:
                logger.error("❌ 解析结果包含PDF二进制内容，解析失败!")
                return False
            else:
                logger.info("✅ 解析结果为纯文本，没有二进制内容")
                
            # 检查个人信息提取
            personal_info = result.get('personal_info', {})
            logger.info(f"👤 个人信息: {personal_info}")
            
            # 检查教育背景
            education = result.get('education', {})
            logger.info(f"🎓 教育背景: {education}")
            
            # 检查工作经验
            work_experience = result.get('work_experience', {})
            logger.info(f"💼 工作经验: {work_experience}")
            
            # 检查技能
            skills = result.get('skills', {})
            logger.info(f"🛠️ 技能: {skills}")
            
            return True
        else:
            error = result.get('error', '未知错误')
            logger.error(f"❌ PDF解析失败: {error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        # 清理测试文件
        if test_pdf_path and test_pdf_path.startswith('/tmp'):
            try:
                os.unlink(test_pdf_path)
                logger.info("🧹 测试文件已清理")
            except:
                pass

def test_binary_vs_text():
    """测试二进制内容与文本内容的区别"""
    logger.info("🔍 测试二进制内容与文本内容的区别...")
    
    # 模拟之前的错误处理方式（直接解码PDF二进制）
    test_pdf_path = create_test_pdf()
    if not test_pdf_path:
        logger.warning("⚠️ 无法创建测试PDF，跳过二进制测试")
        return
    
    try:
        # 读取PDF二进制内容并尝试解码（错误的方式）
        with open(test_pdf_path, 'rb') as f:
            binary_content = f.read()
        
        # 尝试解码为UTF-8（这是之前的错误做法）
        try:
            decoded_content = binary_content.decode('utf-8', errors='ignore')
            logger.info(f"❌ 错误方式解码结果长度: {len(decoded_content)} 字符")
            logger.info(f"❌ 错误方式解码预览: {decoded_content[:100]}...")
            
            # 检查是否包含PDF标识
            if '%PDF-' in decoded_content:
                logger.error("❌ 错误方式包含PDF二进制标识，会导致API错误!")
        except Exception as e:
            logger.error(f"❌ 错误方式解码失败: {e}")
        
        # 使用正确的方式解析
        result = resume_parser.parse_resume(test_pdf_path)
        if result.get('success', False):
            correct_content = result.get('raw_text', '')
            logger.info(f"✅ 正确方式解析结果长度: {len(correct_content)} 字符")
            logger.info(f"✅ 正确方式解析预览: {correct_content[:100]}...")
            
            # 对比两种方式
            logger.info("📊 对比结果:")
            logger.info(f"   错误方式包含PDF标识: {'%PDF-' in decoded_content}")
            logger.info(f"   正确方式包含PDF标识: {'%PDF-' in correct_content}")
            logger.info(f"   错误方式可读性: {'低' if '%PDF-' in decoded_content else '高'}")
            logger.info(f"   正确方式可读性: {'高' if '%PDF-' not in correct_content else '低'}")
            
    except Exception as e:
        logger.error(f"❌ 对比测试失败: {e}")
    finally:
        # 清理测试文件
        try:
            os.unlink(test_pdf_path)
        except:
            pass

def main():
    """主函数"""
    logger.info("🚀 开始PDF简历解析修复测试")
    
    # 测试1: PDF解析功能
    logger.info("\n" + "="*50)
    logger.info("测试1: PDF解析功能")
    logger.info("="*50)
    success1 = test_pdf_parsing()
    
    # 测试2: 二进制vs文本对比
    logger.info("\n" + "="*50)
    logger.info("测试2: 二进制vs文本对比")
    logger.info("="*50)
    test_binary_vs_text()
    
    # 总结
    logger.info("\n" + "="*50)
    logger.info("测试总结")
    logger.info("="*50)
    if success1:
        logger.info("✅ PDF简历解析修复成功!")
        logger.info("✅ 现在PDF文件会被正确解析为文本，而不是传递二进制内容给DeepSeek API")
        logger.info("✅ 这将解决HTTP 400 Bad Request错误")
    else:
        logger.error("❌ PDF简历解析仍有问题，需要进一步调试")
    
    return success1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 