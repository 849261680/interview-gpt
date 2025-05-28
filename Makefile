# Interview-GPT Makefile
# 简化常用的部署和开发命令

.PHONY: help dev prod build test clean logs health backup

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

# 帮助信息
help: ## 显示帮助信息
	@echo "$(BLUE)Interview-GPT 部署命令$(NC)"
	@echo ""
	@echo "$(GREEN)开发环境:$(NC)"
	@echo "  make dev          启动开发环境"
	@echo "  make dev-build    重新构建并启动开发环境"
	@echo "  make dev-logs     查看开发环境日志"
	@echo ""
	@echo "$(GREEN)生产环境:$(NC)"
	@echo "  make prod         启动生产环境"
	@echo "  make prod-build   重新构建并启动生产环境"
	@echo "  make prod-logs    查看生产环境日志"
	@echo "  make prod-scale   扩展生产环境实例"
	@echo ""
	@echo "$(GREEN)测试和质量:$(NC)"
	@echo "  make test         运行所有测试"
	@echo "  make test-backend 运行后端测试"
	@echo "  make test-frontend 运行前端测试"
	@echo "  make lint         代码质量检查"
	@echo ""
	@echo "$(GREEN)维护操作:$(NC)"
	@echo "  make clean        清理容器和镜像"
	@echo "  make health       健康检查"
	@echo "  make backup       备份数据"
	@echo "  make migrate      数据库迁移"
	@echo ""
	@echo "$(GREEN)监控:$(NC)"
	@echo "  make monitor      打开监控面板"
	@echo "  make logs         查看所有日志"
	@echo ""

# 开发环境
dev: ## 启动开发环境
	@echo "$(BLUE)启动开发环境...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)开发环境已启动$(NC)"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"

dev-build: ## 重新构建并启动开发环境
	@echo "$(BLUE)重新构建开发环境...$(NC)"
	docker-compose up -d --build
	@echo "$(GREEN)开发环境构建完成$(NC)"

dev-logs: ## 查看开发环境日志
	docker-compose logs -f

dev-stop: ## 停止开发环境
	@echo "$(YELLOW)停止开发环境...$(NC)"
	docker-compose down
	@echo "$(GREEN)开发环境已停止$(NC)"

# 生产环境
prod: ## 启动生产环境
	@echo "$(BLUE)启动生产环境...$(NC)"
	@if [ ! -f .env.production ]; then \
		echo "$(RED)错误: .env.production 文件不存在$(NC)"; \
		echo "请复制 env.production.example 并配置环境变量"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)生产环境已启动$(NC)"
	@echo "应用: http://localhost:8000"
	@echo "监控: http://localhost:9090"
	@echo "可视化: http://localhost:3001"

prod-build: ## 重新构建并启动生产环境
	@echo "$(BLUE)重新构建生产环境...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "$(GREEN)生产环境构建完成$(NC)"

prod-logs: ## 查看生产环境日志
	docker-compose -f docker-compose.prod.yml logs -f

prod-scale: ## 扩展生产环境实例
	@echo "$(BLUE)扩展应用实例到3个...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d --scale app=3
	@echo "$(GREEN)实例扩展完成$(NC)"

prod-stop: ## 停止生产环境
	@echo "$(YELLOW)停止生产环境...$(NC)"
	docker-compose -f docker-compose.prod.yml down
	@echo "$(GREEN)生产环境已停止$(NC)"

# 测试
test: test-backend test-frontend ## 运行所有测试

test-backend: ## 运行后端测试
	@echo "$(BLUE)运行后端测试...$(NC)"
	cd backend && python -m pytest tests/ -v --cov=src --cov-report=html
	@echo "$(GREEN)后端测试完成$(NC)"

test-frontend: ## 运行前端测试
	@echo "$(BLUE)运行前端测试...$(NC)"
	cd frontend && npm test -- --coverage --watchAll=false
	@echo "$(GREEN)前端测试完成$(NC)"

lint: ## 代码质量检查
	@echo "$(BLUE)运行代码质量检查...$(NC)"
	cd backend && flake8 src/ --max-line-length=100
	cd backend && black --check src/
	cd frontend && npm run lint
	@echo "$(GREEN)代码质量检查完成$(NC)"

# 构建
build: ## 构建Docker镜像
	@echo "$(BLUE)构建Docker镜像...$(NC)"
	docker build -t interview-gpt:latest .
	@echo "$(GREEN)镜像构建完成$(NC)"

# 清理
clean: ## 清理容器和镜像
	@echo "$(YELLOW)清理Docker资源...$(NC)"
	docker-compose down --remove-orphans
	docker-compose -f docker-compose.prod.yml down --remove-orphans
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)清理完成$(NC)"

# 健康检查
health: ## 健康检查
	@echo "$(BLUE)执行健康检查...$(NC)"
	@if curl -f http://localhost:8000/health > /dev/null 2>&1; then \
		echo "$(GREEN)✅ 后端服务正常$(NC)"; \
	else \
		echo "$(RED)❌ 后端服务异常$(NC)"; \
	fi
	@if curl -f http://localhost:3000 > /dev/null 2>&1; then \
		echo "$(GREEN)✅ 前端服务正常$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  前端服务未运行或异常$(NC)"; \
	fi

# 日志
logs: ## 查看所有服务日志
	docker-compose logs -f --tail=100

logs-app: ## 查看应用日志
	docker-compose logs -f app

logs-nginx: ## 查看Nginx日志
	docker-compose logs -f nginx

logs-db: ## 查看数据库日志
	docker-compose logs -f postgres

# 数据库
migrate: ## 运行数据库迁移
	@echo "$(BLUE)运行数据库迁移...$(NC)"
	docker-compose exec app python -c "from backend.src.db.database import engine, Base; from backend.src.models import schemas; Base.metadata.create_all(bind=engine)"
	@echo "$(GREEN)数据库迁移完成$(NC)"

db-shell: ## 连接数据库
	docker-compose exec postgres psql -U interview_gpt interview_gpt

# 备份
backup: ## 备份数据
	@echo "$(BLUE)备份数据...$(NC)"
	mkdir -p backups
	docker-compose exec postgres pg_dump -U interview_gpt interview_gpt > backups/db_backup_$(shell date +%Y%m%d_%H%M%S).sql
	tar -czf backups/uploads_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz uploads/ || true
	@echo "$(GREEN)备份完成$(NC)"

# 监控
monitor: ## 打开监控面板
	@echo "$(BLUE)打开监控面板...$(NC)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001 (admin/admin)"
	@if command -v open > /dev/null; then \
		open http://localhost:9090; \
		open http://localhost:3001; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:9090; \
		xdg-open http://localhost:3001; \
	fi

# 快速部署
quick-dev: ## 快速启动开发环境（包含构建和迁移）
	@echo "$(BLUE)快速启动开发环境...$(NC)"
	make dev-build
	sleep 10
	make migrate
	make health
	@echo "$(GREEN)开发环境就绪！$(NC)"

quick-prod: ## 快速启动生产环境（包含构建和迁移）
	@echo "$(BLUE)快速启动生产环境...$(NC)"
	make prod-build
	sleep 15
	make migrate
	make health
	@echo "$(GREEN)生产环境就绪！$(NC)"

# 重启服务
restart: ## 重启所有服务
	@echo "$(YELLOW)重启服务...$(NC)"
	docker-compose restart
	@echo "$(GREEN)服务重启完成$(NC)"

restart-app: ## 重启应用服务
	docker-compose restart app

restart-nginx: ## 重启Nginx服务
	docker-compose restart nginx

# 更新
update: ## 更新代码并重新部署
	@echo "$(BLUE)更新应用...$(NC)"
	git pull origin main
	make prod-build
	@echo "$(GREEN)更新完成$(NC)"

# 状态检查
status: ## 查看服务状态
	@echo "$(BLUE)服务状态:$(NC)"
	docker-compose ps

# 进入容器
shell-app: ## 进入应用容器
	docker-compose exec app bash

shell-db: ## 进入数据库容器
	docker-compose exec postgres bash

# 安装依赖
install: ## 安装项目依赖
	@echo "$(BLUE)安装项目依赖...$(NC)"
	cd frontend && npm install
	cd backend && pip install -r requirements.txt
	@echo "$(GREEN)依赖安装完成$(NC)"

# 初始化项目
init: ## 初始化项目（首次部署）
	@echo "$(BLUE)初始化项目...$(NC)"
	cp env.production.example .env.production
	@echo "$(YELLOW)请编辑 .env.production 文件配置环境变量$(NC)"
	@echo "$(YELLOW)然后运行: make quick-prod$(NC)" 