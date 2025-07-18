@echo off
chcp 65001 >nul
echo ========================================
echo    校园招聘数据分析平台 v2.0.0
echo    Windows 便捷启动脚本 (uv版本)
echo ========================================
echo.

REM 检查是否安装了uv
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 uv 包管理器
    echo 请先安装 uv: https://docs.astral.sh/uv/getting-started/installation/
    echo 或使用 PowerShell 安装: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo [1/4] 检查 Python 环境...
uv python list >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 正在安装 Python 3.11...
    uv python install 3.11
)

echo [2/4] 同步项目依赖...
uv sync
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [3/4] 构建前端资源...
if exist "node_modules" (
    npm run build-css
) else (
    echo [警告] 未检测到 node_modules，跳过 CSS 构建
    echo 如需完整功能，请运行: npm install
)

echo [4/4] 启动应用服务器...
echo.
echo 应用将在 http://localhost:8000 启动
echo 按 Ctrl+C 停止服务器
echo.
uv run python main.py

echo.
echo 应用已停止
pause