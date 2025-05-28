-- Interview-GPT 数据库初始化脚本
-- PostgreSQL版本

-- 创建数据库（如果不存在）
-- CREATE DATABASE interview_gpt;

-- 连接到数据库
\c interview_gpt;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建面试表
CREATE TABLE IF NOT EXISTS interviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    position VARCHAR(100) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'intermediate',
    status VARCHAR(20) DEFAULT 'pending',
    current_interviewer VARCHAR(50),
    overall_score DECIMAL(5,2),
    resume_path VARCHAR(255),
    session_data JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建消息表
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL,
    interviewer_id VARCHAR(50),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建反馈表
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id) ON DELETE CASCADE,
    summary TEXT,
    overall_score DECIMAL(5,2),
    skill_scores JSONB,
    strengths TEXT[],
    improvements TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建面试官反馈表
CREATE TABLE IF NOT EXISTS interviewer_feedback (
    id SERIAL PRIMARY KEY,
    feedback_id INTEGER REFERENCES feedback(id) ON DELETE CASCADE,
    interviewer_id VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    role VARCHAR(100),
    content TEXT,
    scores JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建文件上传表
CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    saved_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64),
    upload_status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_interviews_user_id ON interviews(user_id);
CREATE INDEX IF NOT EXISTS idx_interviews_status ON interviews(status);
CREATE INDEX IF NOT EXISTS idx_interviews_created_at ON interviews(created_at);

CREATE INDEX IF NOT EXISTS idx_messages_interview_id ON messages(interview_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_sender_type ON messages(sender_type);

CREATE INDEX IF NOT EXISTS idx_feedback_interview_id ON feedback(interview_id);
CREATE INDEX IF NOT EXISTS idx_interviewer_feedback_feedback_id ON interviewer_feedback(feedback_id);

CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_interview_id ON uploaded_files(interview_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_file_hash ON uploaded_files(file_hash);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- 创建全文搜索索引
CREATE INDEX IF NOT EXISTS idx_messages_content_gin ON messages USING gin(to_tsvector('english', content));

-- 创建触发器函数：更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviews_updated_at BEFORE UPDATE ON interviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_updated_at BEFORE UPDATE ON feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认系统配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('max_upload_size', '10485760', '最大文件上传大小（字节）'),
('allowed_file_types', 'pdf,docx,doc,txt,png,jpg,jpeg', '允许的文件类型'),
('interview_timeout', '3600', '面试超时时间（秒）'),
('max_interviews_per_day', '5', '每日最大面试次数'),
('enable_email_notifications', 'true', '是否启用邮件通知'),
('enable_file_upload', 'true', '是否启用文件上传'),
('enable_voice_interview', 'true', '是否启用语音面试'),
('default_interview_difficulty', 'intermediate', '默认面试难度')
ON CONFLICT (config_key) DO NOTHING;

-- 创建视图：面试统计
CREATE OR REPLACE VIEW interview_stats AS
SELECT 
    DATE(created_at) as interview_date,
    COUNT(*) as total_interviews,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_interviews,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_interviews,
    AVG(CASE WHEN overall_score IS NOT NULL THEN overall_score END) as avg_score
FROM interviews
GROUP BY DATE(created_at)
ORDER BY interview_date DESC;

-- 创建视图：用户活动统计
CREATE OR REPLACE VIEW user_activity_stats AS
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(i.id) as total_interviews,
    COUNT(CASE WHEN i.status = 'completed' THEN 1 END) as completed_interviews,
    AVG(CASE WHEN i.overall_score IS NOT NULL THEN i.overall_score END) as avg_score,
    MAX(i.created_at) as last_interview_date
FROM users u
LEFT JOIN interviews i ON u.id = i.user_id
GROUP BY u.id, u.username, u.email;

-- 创建函数：清理过期数据
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    -- 删除30天前的未完成面试
    DELETE FROM interviews 
    WHERE status IN ('pending', 'abandoned') 
    AND created_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    -- 删除90天前的审计日志
    DELETE FROM audit_logs 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    -- 删除孤立的文件记录
    DELETE FROM uploaded_files 
    WHERE interview_id IS NULL 
    AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
    
    RAISE NOTICE '过期数据清理完成';
END;
$$ LANGUAGE plpgsql;

-- 创建定期清理任务（需要pg_cron扩展）
-- SELECT cron.schedule('cleanup-expired-data', '0 2 * * *', 'SELECT cleanup_expired_data();');

COMMIT; 