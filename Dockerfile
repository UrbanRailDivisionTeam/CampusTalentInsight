# 校园招聘数据分析平台 Docker镜像
# Campus Talent Insight Platform Docker Image

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装uv包管理器
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装Python依赖
RUN uv sync --frozen

# 复制项目源代码
COPY src/ ./src/
COPY main.py ./

# 复制静态文件和模板
COPY static/ ./static/
COPY templates/ ./templates/

# 复制配置文件
COPY config/ ./config/

# 创建必要的目录
RUN mkdir -p uploads logs reports

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动命令
CMD ["uv", "run", "python", "main.py"]