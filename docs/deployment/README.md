# Interview-GPT 部署指南

本文档详细介绍了Interview-GPT项目的部署流程，包括开发环境、测试环境和生产环境的部署方法。

## 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [部署方式](#部署方式)
- [监控和维护](#监控和维护)
- [故障排除](#故障排除)
- [安全配置](#安全配置)

## 系统要求

### 硬件要求

**最低配置（开发环境）：**
- CPU: 2核心
- 内存: 4GB RAM
- 存储: 20GB 可用空间
- 网络: 稳定的互联网连接

**推荐配置（生产环境）：**
- CPU: 4核心以上
- 内存: 8GB RAM以上
- 存储: 100GB SSD
- 网络: 高速稳定的互联网连接

### 软件要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Node.js**: 18.0+ (本地开发)
- **Python**: 3.11+ (本地开发)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-org/interview-gpt.git
cd interview-gpt
```

### 2. 环境配置

```bash
# 复制环境变量配置文件
cp env.production.example .env.production

# 编辑配置文件，填入实际值
nano .env.production
```

### 3. 一键部署

```bash
# 开发环境
./scripts/deploy.sh dev

# 生产环境
./scripts/deploy.sh prod -c -b -m
```

## 环境配置

### 环境变量说明

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `SECRET_KEY` | 应用密钥 | ✅ | - |
| `DEBUG` | 调试模式 | ❌ | false |
| `DATABASE_URL` | 数据库连接 | ✅ | - |
| `REDIS_URL` | Redis连接 | ✅ | - |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | ✅ | - |
| `CORS_ORIGINS` | 允许的跨域源 | ✅ | - |

### 配置文件位置

```
├── .env.production          # 生产环境配置
├── env.production.example   # 配置模板
├── backend/.env            # 后端开发配置
└── frontend/.env.local     # 前端开发配置
```

## 部署方式

### 方式一：Docker Compose（推荐）

#### 开发环境部署

```bash
# 启动开发环境
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 生产环境部署

```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 扩展应用实例
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# 滚动更新
docker-compose -f docker-compose.prod.yml up -d --no-deps app
```

### 方式二：自动化脚本

```bash
# 使用部署脚本
./scripts/deploy.sh [环境] [选项]

# 示例
./scripts/deploy.sh prod -c -b -m -t
```

**脚本选项说明：**
- `-c, --clean`: 清理旧容器和镜像
- `-b, --build`: 强制重新构建
- `-m, --migrate`: 运行数据库迁移
- `-t, --test`: 运行测试
- `-p, --pull`: 拉取最新代码

### 方式三：Kubernetes部署

```bash
# 应用Kubernetes配置
kubectl apply -f k8s/

# 查看部署状态
kubectl get pods -n interview-gpt

# 查看服务
kubectl get services -n interview-gpt
```

## 服务架构

### 生产环境架构图

```
┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │      Nginx      │
│    (Optional)   │────│   Reverse Proxy │
└─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │  Interview-GPT  │
                       │   Application   │
                       │   (Multiple)    │
                       └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────────┐ ┌──────────┐ ┌─────────┐
            │PostgreSQL │ │  Redis   │ │ Storage │
            │ Database  │ │  Cache   │ │ (Files) │
            └───────────┘ └──────────┘ └─────────┘
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端应用 | 3000 | Next.js应用 |
| 后端API | 8000 | FastAPI服务 |
| Nginx | 80/443 | 反向代理 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| Prometheus | 9090 | 监控 |
| Grafana | 3001 | 可视化 |

## 数据库配置

### PostgreSQL设置

```bash
# 创建数据库
createdb interview_gpt

# 运行初始化脚本
psql -d interview_gpt -f scripts/init-db.sql

# 备份数据库
pg_dump interview_gpt > backup.sql

# 恢复数据库
psql -d interview_gpt < backup.sql
```

### 数据库迁移

```bash
# 自动迁移（Docker环境）
docker-compose exec app python -c "
from backend.src.db.database import engine, Base
from backend.src.models import schemas
Base.metadata.create_all(bind=engine)
"

# 手动迁移
cd backend
python -c "
from src.db.database import engine, Base
from src.models import schemas
Base.metadata.create_all(bind=engine)
"
```

## 监控和维护

### 健康检查

```bash
# 检查应用健康状态
curl http://localhost:8000/health

# 检查所有服务
./scripts/health-check.sh
```

### 日志管理

```bash
# 查看应用日志
docker-compose logs -f app

# 查看特定服务日志
docker-compose logs -f nginx

# 日志轮转配置
# 在docker-compose.yml中配置logging选项
```

### 监控面板

访问监控服务：
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### 备份策略

```bash
# 数据库备份
docker-compose exec postgres pg_dump -U interview_gpt interview_gpt > backup_$(date +%Y%m%d).sql

# 文件备份
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# 自动备份脚本
./scripts/backup.sh
```

## 性能优化

### 应用层优化

1. **启用缓存**
   ```bash
   # Redis缓存配置
   REDIS_URL=redis://redis:6379/0
   ```

2. **数据库连接池**
   ```python
   # 在settings.py中配置
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=30
   ```

3. **静态文件CDN**
   ```bash
   # 配置CDN地址
   STATIC_URL=https://cdn.interview-gpt.com/static/
   ```

### 系统层优化

1. **Nginx配置优化**
   - 启用Gzip压缩
   - 配置缓存策略
   - 设置连接池

2. **Docker优化**
   - 多阶段构建
   - 镜像层缓存
   - 资源限制

## 安全配置

### SSL/TLS配置

```bash
# 生成SSL证书（Let's Encrypt）
certbot certonly --webroot -w /var/www/html -d interview-gpt.com

# 配置Nginx SSL
# 参考 nginx/nginx.prod.conf
```

### 防火墙设置

```bash
# UFW配置
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 安全头配置

在Nginx配置中已包含：
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Strict-Transport-Security

## 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器日志
docker-compose logs app

# 检查配置文件
docker-compose config

# 重新构建镜像
docker-compose build --no-cache app
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker-compose exec postgres pg_isready

# 检查连接字符串
echo $DATABASE_URL

# 重启数据库服务
docker-compose restart postgres
```

#### 3. 文件上传失败

```bash
# 检查上传目录权限
ls -la uploads/

# 修复权限
chmod 755 uploads/
chown -R appuser:appuser uploads/
```

#### 4. AI服务调用失败

```bash
# 检查API密钥
echo $DEEPSEEK_API_KEY

# 测试API连接
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     https://api.deepseek.com/v1/models
```

### 调试模式

```bash
# 启用调试模式
export DEBUG=true

# 查看详细日志
docker-compose logs -f --tail=100 app
```

### 性能问题诊断

```bash
# 查看资源使用
docker stats

# 查看数据库性能
docker-compose exec postgres psql -U interview_gpt -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
"
```

## 更新和回滚

### 应用更新

```bash
# 拉取最新代码
git pull origin main

# 重新部署
./scripts/deploy.sh prod -b

# 零停机更新
docker-compose -f docker-compose.prod.yml up -d --no-deps app
```

### 版本回滚

```bash
# 回滚到指定版本
git checkout v1.0.0
./scripts/deploy.sh prod -b

# 数据库回滚（谨慎操作）
psql -d interview_gpt < backup_20231201.sql
```

## 扩展部署

### 水平扩展

```bash
# 扩展应用实例
docker-compose -f docker-compose.prod.yml up -d --scale app=5

# 负载均衡配置
# 在nginx.prod.conf中添加更多upstream服务器
```

### 垂直扩展

```yaml
# 在docker-compose.prod.yml中调整资源限制
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
```

## 联系支持

如果遇到部署问题，请：

1. 查看[故障排除](#故障排除)部分
2. 检查[GitHub Issues](https://github.com/your-org/interview-gpt/issues)
3. 联系技术支持团队

---

**注意**: 在生产环境部署前，请确保已经完成安全配置和性能优化。 