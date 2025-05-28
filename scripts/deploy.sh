#!/bin/bash

# Interview-GPT 自动化部署脚本
# 支持开发环境和生产环境部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
Interview-GPT 部署脚本

用法: $0 [选项] <环境>

环境:
    dev         部署开发环境
    prod        部署生产环境
    staging     部署测试环境

选项:
    -h, --help              显示帮助信息
    -c, --clean             清理旧的容器和镜像
    -b, --build             强制重新构建镜像
    -p, --pull              拉取最新代码
    -m, --migrate           运行数据库迁移
    -t, --test              运行测试
    --no-cache              构建时不使用缓存
    --scale <service>=<num> 扩展服务实例数量

示例:
    $0 dev                  部署开发环境
    $0 prod -c -b           清理并重新构建生产环境
    $0 prod --scale app=3   部署生产环境并扩展app服务到3个实例

EOF
}

# 默认参数
ENVIRONMENT=""
CLEAN=false
BUILD=false
PULL=false
MIGRATE=false
TEST=false
NO_CACHE=false
SCALE_ARGS=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -p|--pull)
            PULL=true
            shift
            ;;
        -m|--migrate)
            MIGRATE=true
            shift
            ;;
        -t|--test)
            TEST=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --scale)
            SCALE_ARGS="$2"
            shift 2
            ;;
        dev|prod|staging)
            ENVIRONMENT=$1
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查环境参数
if [[ -z "$ENVIRONMENT" ]]; then
    log_error "请指定部署环境: dev, prod, 或 staging"
    show_help
    exit 1
fi

# 检查必要的工具
check_requirements() {
    log_info "检查部署环境..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 拉取最新代码
pull_code() {
    if [[ "$PULL" == true ]]; then
        log_info "拉取最新代码..."
        git fetch origin
        git pull origin main
        log_success "代码更新完成"
    fi
}

# 清理旧的容器和镜像
cleanup() {
    if [[ "$CLEAN" == true ]]; then
        log_info "清理旧的容器和镜像..."
        
        # 停止并删除容器
        docker-compose -f docker-compose.${ENVIRONMENT}.yml down --remove-orphans || true
        
        # 删除未使用的镜像
        docker image prune -f
        
        # 删除未使用的卷
        docker volume prune -f
        
        log_success "清理完成"
    fi
}

# 运行测试
run_tests() {
    if [[ "$TEST" == true ]]; then
        log_info "运行测试..."
        
        # 后端测试
        log_info "运行后端测试..."
        cd backend
        python -m pytest tests/ -v --cov=src --cov-report=html
        cd ..
        
        # 前端测试
        log_info "运行前端测试..."
        cd frontend
        npm test -- --coverage --watchAll=false
        cd ..
        
        log_success "测试完成"
    fi
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    local build_args=""
    if [[ "$NO_CACHE" == true ]]; then
        build_args="--no-cache"
    fi
    
    if [[ "$BUILD" == true ]] || [[ "$CLEAN" == true ]]; then
        build_args="$build_args --build"
    fi
    
    case $ENVIRONMENT in
        dev)
            docker-compose -f docker-compose.yml build $build_args
            ;;
        prod)
            docker-compose -f docker-compose.prod.yml build $build_args
            ;;
        staging)
            docker-compose -f docker-compose.staging.yml build $build_args
            ;;
    esac
    
    log_success "镜像构建完成"
}

# 部署服务
deploy_services() {
    log_info "部署 $ENVIRONMENT 环境..."
    
    local compose_file=""
    case $ENVIRONMENT in
        dev)
            compose_file="docker-compose.yml"
            ;;
        prod)
            compose_file="docker-compose.prod.yml"
            ;;
        staging)
            compose_file="docker-compose.staging.yml"
            ;;
    esac
    
    # 启动服务
    docker-compose -f $compose_file up -d
    
    # 扩展服务（如果指定）
    if [[ -n "$SCALE_ARGS" ]]; then
        log_info "扩展服务: $SCALE_ARGS"
        docker-compose -f $compose_file up -d --scale $SCALE_ARGS
    fi
    
    log_success "服务部署完成"
}

# 运行数据库迁移
run_migrations() {
    if [[ "$MIGRATE" == true ]]; then
        log_info "运行数据库迁移..."
        
        case $ENVIRONMENT in
            dev)
                docker-compose exec backend python -c "
from src.db.database import engine, Base
from src.models import schemas
Base.metadata.create_all(bind=engine)
print('数据库迁移完成')
"
                ;;
            prod)
                docker-compose -f docker-compose.prod.yml exec app python -c "
from backend.src.db.database import engine, Base
from backend.src.models import schemas
Base.metadata.create_all(bind=engine)
print('数据库迁移完成')
"
                ;;
        esac
        
        log_success "数据库迁移完成"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_retries=30
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "后端服务健康检查通过"
            break
        fi
        
        retry_count=$((retry_count + 1))
        log_info "等待服务启动... ($retry_count/$max_retries)"
        sleep 2
    done
    
    if [[ $retry_count -eq $max_retries ]]; then
        log_error "健康检查失败"
        exit 1
    fi
    
    # 检查前端服务（如果是开发环境）
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        retry_count=0
        while [[ $retry_count -lt $max_retries ]]; do
            if curl -f http://localhost:3000 > /dev/null 2>&1; then
                log_success "前端服务健康检查通过"
                break
            fi
            
            retry_count=$((retry_count + 1))
            log_info "等待前端服务启动... ($retry_count/$max_retries)"
            sleep 2
        done
        
        if [[ $retry_count -eq $max_retries ]]; then
            log_warning "前端服务健康检查失败"
        fi
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 Interview-GPT $ENVIRONMENT 环境部署完成！"
    echo ""
    echo "📍 服务地址:"
    echo "   - 后端API: http://localhost:8000"
    echo "   - API文档: http://localhost:8000/docs"
    echo "   - 健康检查: http://localhost:8000/health"
    
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        echo "   - 前端应用: http://localhost:3000"
    fi
    
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        echo "   - 监控面板: http://localhost:9090 (Prometheus)"
        echo "   - 可视化面板: http://localhost:3001 (Grafana)"
    fi
    
    echo ""
    echo "🔧 管理命令:"
    echo "   - 查看日志: docker-compose -f docker-compose.${ENVIRONMENT}.yml logs -f"
    echo "   - 停止服务: docker-compose -f docker-compose.${ENVIRONMENT}.yml down"
    echo "   - 重启服务: docker-compose -f docker-compose.${ENVIRONMENT}.yml restart"
    echo ""
}

# 主函数
main() {
    log_info "开始部署 Interview-GPT $ENVIRONMENT 环境"
    
    check_requirements
    pull_code
    cleanup
    run_tests
    build_images
    deploy_services
    run_migrations
    health_check
    show_deployment_info
    
    log_success "部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main 