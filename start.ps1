# 校园招聘数据分析平台 v2.0.0 - Windows PowerShell 启动脚本

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 显示启动信息
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   校园招聘数据分析平台 v2.0.0" -ForegroundColor Green
Write-Host "   Windows PowerShell 启动脚本 (uv版本)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查uv是否安装
try {
    $uvVersion = uv --version 2>$null
    Write-Host "[✓] 检测到 uv: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] 未检测到 uv 包管理器" -ForegroundColor Red
    Write-Host "请先安装 uv:" -ForegroundColor Yellow
    Write-Host "  方法1: winget install --id=astral-sh.uv" -ForegroundColor White
    Write-Host "  方法2: powershell -c 'irm https://astral.sh/uv/install.ps1 | iex'" -ForegroundColor White
    Write-Host "  方法3: 访问 https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor White
    Read-Host "按回车键退出"
    exit 1
}

# 步骤1: 检查Python环境
Write-Host "[1/4] 检查 Python 环境..." -ForegroundColor Blue
try {
    $pythonList = uv python list 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[i] 正在安装 Python 3.11..." -ForegroundColor Yellow
        uv python install 3.11
        if ($LASTEXITCODE -ne 0) {
            throw "Python 安装失败"
        }
    }
    Write-Host "[✓] Python 环境就绪" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python 环境配置失败: $_" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 步骤2: 同步项目依赖
Write-Host "[2/4] 同步项目依赖..." -ForegroundColor Blue
try {
    uv sync
    if ($LASTEXITCODE -ne 0) {
        throw "依赖同步失败"
    }
    Write-Host "[✓] 依赖同步完成" -ForegroundColor Green
} catch {
    Write-Host "[✗] 依赖安装失败: $_" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 步骤3: 构建前端资源
Write-Host "[3/4] 构建前端资源..." -ForegroundColor Blue
if (Test-Path "node_modules") {
    try {
        npm run build-css
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] CSS 构建完成" -ForegroundColor Green
        } else {
            Write-Host "[!] CSS 构建失败，但不影响核心功能" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[!] CSS 构建出错，但不影响核心功能" -ForegroundColor Yellow
    }
} else {
    Write-Host "[!] 未检测到 node_modules，跳过 CSS 构建" -ForegroundColor Yellow
    Write-Host "    如需完整前端功能，请运行: npm install" -ForegroundColor Gray
}

# 步骤4: 启动应用
Write-Host "[4/4] 启动应用服务器..." -ForegroundColor Blue
Write-Host ""
Write-Host "🚀 应用将在 http://localhost:8000 启动" -ForegroundColor Green
Write-Host "📱 本地访问: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "🛑 按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

# 启动应用
try {
    uv run python main.py
} catch {
    Write-Host ""
    Write-Host "[✗] 应用启动失败: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "应用已停止" -ForegroundColor Gray
    Read-Host "按回车键退出"
}