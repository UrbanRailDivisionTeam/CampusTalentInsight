#!/bin/bash
# Docker部署脚本 - 校园招聘数据分析平台
# Bash脚本，适用于Linux/macOS环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印彩色输出
print_color() {
    printf "${1}${2}${NC}\n"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_color $RED "错误: Docker 未安装"
        print_color $YELLOW "请先安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_color $RED "错误: Docker Compose 未安装"
        print_color $YELLOW "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_color $RED "错误: Docker 服务未启动"
        print_color $YELLOW "请先启动 Docker 服务"
        exit 1
    fi
}

# 创建必要目录
setup_directories() {
    local directories=("uploads" "logs" "reports" "config")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_color $YELLOW "创建目录: $dir"
        fi
    done
    
    # 确保密码文件存在
    if [ ! -f "config/password.txt" ]; then
        echo "Zhuji123！" > config/password.txt
        print_color $YELLOW "创建默认密码文件: config/password.txt"
    fi
}

# 启动应用
start_app() {
    print_color $GREEN "启动校园招聘数据分析平台..."
    
    local compose_args=("up" "-d")
    
    if [ "$BUILD" = "true" ]; then
        compose_args+=("--build")
        print_color $YELLOW "重新构建Docker镜像..."
    fi
    
    if [ "$PRODUCTION" = "true" ]; then
        compose_args+=("--profile" "production")
        print_color $CYAN "使用生产环境配置（包含Nginx）"
    fi
    
    if docker-compose "${compose_args[@]}"; then
        echo
        print_color $GREEN "✅ 应用启动成功！"
        print_color $CYAN "📱 访问地址: http://localhost:8000"
        print_color $CYAN "🔑 默认密码: Zhuji123！"
        
        if [ "$PRODUCTION" = "true" ]; then
            print_color $CYAN "🌐 Nginx代理: http://localhost:80"
        fi
        
        echo
        print_color $YELLOW "💡 提示:"
        print_color $NC "  - 查看日志: ./deploy.sh logs"
        print_color $NC "  - 查看状态: ./deploy.sh status"
        print_color $NC "  - 停止服务: ./deploy.sh stop"
    else
        print_color $RED "❌ 应用启动失败，请检查日志"
        exit 1
    fi
}

# 停止应用
stop_app() {
    print_color $YELLOW "停止校园招聘数据分析平台..."
    
    if [ "$PRODUCTION" = "true" ]; then
        docker-compose --profile production down
    else
        docker-compose down
    fi
    
    print_color $GREEN "✅ 应用已停止"
}

# 重启应用
restart_app() {
    print_color $YELLOW "重启校园招聘数据分析平台..."
    stop_app
    sleep 2
    start_app
}

# 显示状态
show_status() {
    print_color $GREEN "=== 服务状态 ==="
    docker-compose ps
    
    echo
    print_color $GREEN "=== 资源使用情况 ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# 显示日志
show_logs() {
    if [ "$FOLLOW" = "true" ]; then
        print_color $GREEN "=== 实时日志 (按 Ctrl+C 退出) ==="
        docker-compose logs -f
    else
        print_color $GREEN "=== 最近日志 ==="
        docker-compose logs --tail=50
    fi
}

# 清理应用
clean_app() {
    print_color $YELLOW "清理Docker资源..."
    
    read -p "这将删除所有容器、镜像和卷，确定继续吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        docker system prune -f
        print_color $GREEN "✅ 清理完成"
    else
        print_color $YELLOW "取消清理操作"
    fi
}

# 备份数据
backup_data() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="backup_${timestamp}.tar.gz"
    
    print_color $GREEN "创建数据备份: $backup_file"
    
    local files_to_backup=()
    for dir in "uploads" "config" "logs"; do
        if [ -d "$dir" ]; then
            files_to_backup+=("$dir")
        fi
    done
    
    if [ ${#files_to_backup[@]} -gt 0 ]; then
        tar -czf "$backup_file" "${files_to_backup[@]}"
        print_color $GREEN "✅ 备份完成: $backup_file"
    else
        print_color $YELLOW "⚠️ 没有找到需要备份的数据"
    fi
}

# 显示帮助
show_help() {
    print_color $GREEN "=== 校园招聘数据分析平台 Docker 部署工具 ==="
    echo
    print_color $CYAN "用法:"
    echo "  ./deploy.sh [动作] [选项]"
    echo
    print_color $CYAN "动作:"
    echo "  start     启动应用 (默认)"
    echo "  stop      停止应用"
    echo "  restart   重启应用"
    echo "  status    查看状态"
    echo "  logs      查看日志"
    echo "  clean     清理所有Docker资源"
    echo "  backup    备份数据"
    echo "  help      显示帮助"
    echo
    print_color $CYAN "选项:"
    echo "  --production  使用生产环境配置（包含Nginx）"
    echo "  --build       重新构建Docker镜像"
    echo "  --follow      显示实时日志"
    echo
    print_color $CYAN "示例:"
    echo "  ./deploy.sh start                    # 启动开发环境"
    echo "  ./deploy.sh start --production       # 启动生产环境"
    echo "  ./deploy.sh start --build            # 重新构建并启动"
    echo "  ./deploy.sh logs --follow            # 查看实时日志"
    echo "  ./deploy.sh restart --production     # 重启生产环境"
}

# 主函数
main() {
    print_color $GREEN "=== 校园招聘数据分析平台 Docker 部署工具 ==="
    print_color $CYAN "版本: 2.0.0"
    print_color $CYAN "作者: 百万年薪全栈工程师"
    echo
    
    # 检查Docker环境
    check_docker
    
    # 设置目录
    setup_directories
    
    # 解析参数
    ACTION="start"
    PRODUCTION="false"
    BUILD="false"
    FOLLOW="false"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status|logs|clean|backup|help)
                ACTION="$1"
                shift
                ;;
            --production)
                PRODUCTION="true"
                shift
                ;;
            --build)
                BUILD="true"
                shift
                ;;
            --follow)
                FOLLOW="true"
                shift
                ;;
            *)
                print_color $RED "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 执行动作
    case $ACTION in
        start)
            start_app
            ;;
        stop)
            stop_app
            ;;
        restart)
            restart_app
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_app
            ;;
        backup)
            backup_data
            ;;
        help)
            show_help
            ;;
        *)
            print_color $RED "未知动作: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"