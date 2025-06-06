"""
数据库迁移脚本
用于重新创建数据库表结构，解决表结构不一致问题
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..models.schemas import Base
from ..config.settings import settings

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """
    重新创建数据库表结构
    删除旧的数据库文件并创建新的表结构
    """
    try:
        # 获取数据库文件路径
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite:///"):
            db_file = db_url.replace("sqlite:///", "")
            
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(db_file):
                # 获取项目根目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                db_file = os.path.join(project_root, "backend", db_file)
            
            # 删除旧的数据库文件
            if os.path.exists(db_file):
                os.remove(db_file)
                logger.info(f"已删除旧数据库文件: {db_file}")
        
        # 创建新的数据库引擎
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表结构已重新创建")
        
        # 验证表结构
        with engine.connect() as conn:
            # 检查messages表是否包含sender_type列
            result = conn.execute(text("PRAGMA table_info(messages)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'sender_type' in columns:
                logger.info("✓ messages表包含sender_type列")
            else:
                logger.error("✗ messages表缺少sender_type列")
                
            # 检查所有表是否存在
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['users', 'interviews', 'messages', 'feedbacks', 'interviewer_feedbacks']
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✓ 表 {table} 已创建")
                else:
                    logger.error(f"✗ 表 {table} 未创建")
        
        logger.info("数据库迁移完成")
        return True
        
    except Exception as e:
        logger.error(f"数据库迁移失败: {str(e)}")
        return False


if __name__ == "__main__":
    migrate_database() 