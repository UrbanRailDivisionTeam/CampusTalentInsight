# Docker部署脚本 - 校园招聘数据分析平台
# PowerShell脚本，适用于Windows环境

param(
    [string]$Action = "start",
    [switch]$Production = $false,
    [switch]$Build = $false,
    [switch]$Logs = $false
)

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# 检查Docker是否安装
function Test-Docker {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        return $true
    } catch {
        Write-ColorOutput Red "错误: Docker 或 Docker Compose 未安装或未启动"
        Write-ColorOutput Yellow "请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
        return $false
    }
}

# 主函数
function Main {
    Write-ColorOutput Green "=== 校园招聘数据分析平台 Docker 部署工具 ==="
    Write-ColorOutput Cyan "版本: 2.0.0"
    Write-ColorOutput Cyan "作者: 百万年薪全栈工程师"
    Write-Output ""

    # 检查Docker环境
    if (-not (Test-Docker)) {
        exit 1
    }

    # 确保必要目录存在
    $directories = @("uploads", "logs", "reports", "config")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColorOutput Yellow "创建目录: $dir"
        }
    }

    # 确保密码文件存在
    if (-not (Test-Path "config/password.txt")) {
        "Zhuji123！" | Out-File -FilePath "config/password.txt" -Encoding UTF8
        Write-ColorOutput Yellow "创建默认密码文件: config/password.txt"
    }

    switch ($Action.ToLower()) {
        "start" {
            Start-Application
        }
        "stop" {
            Stop-Application
        }
        "restart" {
            Restart-Application
        }
        "status" {
            Show-Status
        }
        "logs" {
            Show-Logs
        }
        "clean" {
            Clean-Application
        }
        "backup" {
            Backup-Data
        }
        default {
            Show-Help
        }
    }
}

# 启动应用
function Start-Application {
    Write-ColorOutput Green "启动校园招聘数据分析平台..."
    
    $composeArgs = @("up", "-d")
    
    if ($Build) {
        $composeArgs += "--build"
        Write-ColorOutput Yellow "重新构建Docker镜像..."
    }
    
    if ($Production) {
        $composeArgs += @("--profile", "production")
        Write-ColorOutput Cyan "使用生产环境配置（包含Nginx）"
    }
    
    & docker-compose $composeArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Output ""
        Write-ColorOutput Green "✅ 应用启动成功！"
        Write-ColorOutput Cyan "📱 访问地址: http://localhost:8000"
        Write-ColorOutput Cyan "🔑 默认密码: Zhuji123！"
        
        if ($Production) {
            Write-ColorOutput Cyan "🌐 Nginx代理: http://localhost:80"
        }
        
        Write-Output ""
        Write-ColorOutput Yellow "💡 提示:"
        Write-ColorOutput White "  - 查看日志: .\deploy.ps1 logs"
        Write-ColorOutput White "  - 查看状态: .\deploy.ps1 status"
        Write-ColorOutput White "  - 停止服务: .\deploy.ps1 stop"
    } else {
        Write-ColorOutput Red "❌ 应用启动失败，请检查日志"
    }
}

# 停止应用
function Stop-Application {
    Write-ColorOutput Yellow "停止校园招聘数据分析平台..."
    
    if ($Production) {
        docker-compose --profile production down
    } else {
        docker-compose down
    }
    
    Write-ColorOutput Green "✅ 应用已停止"
}

# 重启应用
function Restart-Application {
    Write-ColorOutput Yellow "重启校园招聘数据分析平台..."
    Stop-Application
    Start-Sleep -Seconds 2
    Start-Application
}

# 显示状态
function Show-Status {
    Write-ColorOutput Green "=== 服务状态 ==="
    docker-compose ps
    
    Write-Output ""
    Write-ColorOutput Green "=== 资源使用情况 ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# 显示日志
function Show-Logs {
    if ($Logs) {
        Write-ColorOutput Green "=== 实时日志 (按 Ctrl+C 退出) ==="
        docker-compose logs -f
    } else {
        Write-ColorOutput Green "=== 最近日志 ==="
        docker-compose logs --tail=50
    }
}

# 清理应用
function Clean-Application {
    Write-ColorOutput Yellow "清理Docker资源..."
    
    $confirm = Read-Host "这将删除所有容器、镜像和卷，确定继续吗？(y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        docker-compose down -v --rmi all
        docker system prune -f
        Write-ColorOutput Green "✅ 清理完成"
    } else {
        Write-ColorOutput Yellow "取消清理操作"
    }
}

# 备份数据
function Backup-Data {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backup_$timestamp.zip"
    
    Write-ColorOutput Green "创建数据备份: $backupFile"
    
    $filesToBackup = @("uploads", "config", "logs")
    $existingFiles = $filesToBackup | Where-Object { Test-Path $_ }
    
    if ($existingFiles.Count -gt 0) {
        Compress-Archive -Path $existingFiles -DestinationPath $backupFile -Force
        Write-ColorOutput Green "✅ 备份完成: $backupFile"
    } else {
        Write-ColorOutput Yellow "⚠️ 没有找到需要备份的数据"
    }
}

# 显示帮助
function Show-Help {
    Write-ColorOutput Green "=== 校园招聘数据分析平台 Docker 部署工具 ==="
    Write-Output ""
    Write-ColorOutput Cyan "用法:"
    Write-Output "  .\deploy.ps1 [动作] [选项]"
    Write-Output ""
    Write-ColorOutput Cyan "动作:"
    Write-Output "  start     启动应用 (默认)"
    Write-Output "  stop      停止应用"
    Write-Output "  restart   重启应用"
    Write-Output "  status    查看状态"
    Write-Output "  logs      查看日志"
    Write-Output "  clean     清理所有Docker资源"
    Write-Output "  backup    备份数据"
    Write-Output ""
    Write-ColorOutput Cyan "选项:"
    Write-Output "  -Production   使用生产环境配置（包含Nginx）"
    Write-Output "  -Build        重新构建Docker镜像"
    Write-Output "  -Logs         显示实时日志"
    Write-Output ""
    Write-ColorOutput Cyan "示例:"
    Write-Output "  .\deploy.ps1 start                    # 启动开发环境"
    Write-Output "  .\deploy.ps1 start -Production        # 启动生产环境"
    Write-Output "  .\deploy.ps1 start -Build             # 重新构建并启动"
    Write-Output "  .\deploy.ps1 logs -Logs               # 查看实时日志"
    Write-Output "  .\deploy.ps1 restart -Production      # 重启生产环境"
}

# 执行主函数
Main