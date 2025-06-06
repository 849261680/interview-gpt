#!/usr/bin/env python3
"""
数据库迁移脚本：更新interviews表结构
- 将resume_path重命名为resume_filename
- 确保resume_content列存在
"""
import sqlite3
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_interview_schema():
    """更新interviews表结构"""
    
    # 数据库文件路径
    db_paths = [
        "interview_gpt.db",
        "interview.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            logger.info(f"正在更新数据库: {db_path}")
            
            try:
                # 连接数据库
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 检查当前表结构
                cursor.execute("PRAGMA table_info(interviews)")
                columns = {column[1]: column for column in cursor.fetchall()}
                column_names = list(columns.keys())
                
                logger.info(f"当前interviews表的列: {column_names}")
                
                # 检查是否需要迁移
                needs_migration = False
                
                if 'resume_path' in column_names and 'resume_filename' not in column_names:
                    needs_migration = True
                    logger.info("需要将resume_path重命名为resume_filename")
                
                if 'resume_content' not in column_names:
                    needs_migration = True
                    logger.info("需要添加resume_content列")
                
                if needs_migration:
                    # 开始事务
                    cursor.execute("BEGIN TRANSACTION")
                    
                    # 创建新表结构
                    cursor.execute("""
                        CREATE TABLE interviews_new (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            position VARCHAR(100),
                            difficulty VARCHAR(20),
                            status VARCHAR(20) DEFAULT 'active',
                            created_at DATETIME,
                            completed_at DATETIME,
                            resume_filename VARCHAR(255),
                            resume_content TEXT,
                            overall_score FLOAT,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    """)
                    
                    # 复制数据，处理字段重命名
                    if 'resume_path' in column_names:
                        cursor.execute("""
                            INSERT INTO interviews_new 
                            (id, user_id, position, difficulty, status, created_at, completed_at, resume_filename, resume_content, overall_score)
                            SELECT 
                                id, user_id, position, difficulty, status, created_at, completed_at, 
                                resume_path as resume_filename, 
                                COALESCE(resume_content, '') as resume_content, 
                                overall_score
                            FROM interviews
                        """)
                    else:
                        cursor.execute("""
                            INSERT INTO interviews_new 
                            (id, user_id, position, difficulty, status, created_at, completed_at, resume_filename, resume_content, overall_score)
                            SELECT 
                                id, user_id, position, difficulty, status, created_at, completed_at, 
                                resume_filename, 
                                COALESCE(resume_content, '') as resume_content, 
                                overall_score
                            FROM interviews
                        """)
                    
                    # 删除旧表
                    cursor.execute("DROP TABLE interviews")
                    
                    # 重命名新表
                    cursor.execute("ALTER TABLE interviews_new RENAME TO interviews")
                    
                    # 重新创建索引
                    cursor.execute("CREATE INDEX IF NOT EXISTS ix_interviews_id ON interviews (id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS ix_interviews_position ON interviews (position)")
                    
                    # 提交事务
                    cursor.execute("COMMIT")
                    
                    logger.info(f"✅ 成功更新 {db_path} 的表结构")
                else:
                    logger.info(f"ℹ️ {db_path} 的表结构已是最新版本")
                
                # 验证最终表结构
                cursor.execute("PRAGMA table_info(interviews)")
                final_columns = [column[1] for column in cursor.fetchall()]
                logger.info(f"更新后interviews表的列: {final_columns}")
                
                conn.close()
                
            except Exception as e:
                logger.error(f"❌ 更新数据库 {db_path} 失败: {str(e)}")
                if 'conn' in locals():
                    try:
                        conn.rollback()
                        conn.close()
                    except:
                        pass
        else:
            logger.info(f"数据库文件不存在: {db_path}")

if __name__ == "__main__":
    logger.info("开始数据库迁移...")
    update_interview_schema()
    logger.info("数据库迁移完成") 