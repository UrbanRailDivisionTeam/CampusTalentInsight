#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园招聘数据分析平台 - 主应用文件
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..api.routes import create_api_router, create_main_router
from ..utils.file_manager import FileManager
from ..utils.logger import LoggerManager, get_logger
from .config import AppConfig
from .auth_middleware import AuthMiddleware
from .middleware import (
    ErrorHandlingMiddleware,
    PerformanceMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    logger = get_logger("startup")

    try:
        # 设置日志系统
        LoggerManager.setup_logging()
        logger.info(f"🚀 启动 {AppConfig.TITLE} v{AppConfig.VERSION}")

        # 验证配置
        if not AppConfig.validate_config():
            logger.error("❌ 配置验证失败，应用启动中止")
            raise RuntimeError("配置验证失败")

        # 确保目录存在
        AppConfig.ensure_directories()
        logger.info("📁 目录结构检查完成")

        # 记录配置信息
        config_info = AppConfig.get_info()
        logger.info(f"📋 配置信息: {config_info}")

        # 自动加载最新Excel文件
        try:
            from ..api.routes import get_data_manager
            from ..utils.file_manager import FileManager
            from .data_processor import DataProcessor

            file_manager = FileManager()
            data_manager = get_data_manager()

            latest_result = file_manager.get_latest_file()
            if latest_result:
                latest_filename, df = latest_result

                # 数据增强处理
                df_enhanced = DataProcessor.enhance_data(df)

                # 获取文件的上传记录信息
                upload_records = file_manager.get_upload_history()
                matching_record = None
                for record in upload_records:
                    if record["filename"] == latest_filename:
                        matching_record = record
                        break

                description = (
                    matching_record["description"] if matching_record else "自动加载的文件"
                )
                upload_time = (
                    matching_record["upload_time"]
                    if matching_record
                    else None
                )
                
                # 如果没有找到匹配的记录，使用文件的修改时间
                if upload_time is None:
                    from pathlib import Path
                    from datetime import datetime
                    
                    file_path = Path(file_manager.uploads_dir) / latest_filename
                    if file_path.exists():
                        upload_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    else:
                        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 将数据设置到全局数据管理器
                data_manager.update_data(df_enhanced, description, upload_time)

                logger.info(
                    f"📊 已自动加载最新Excel文件: {latest_filename} (共{len(df_enhanced)}条记录)"
                )
            else:
                logger.info("📂 未找到已上传的Excel文件")
        except Exception as e:
            logger.warning(f"⚠️ 自动加载Excel文件失败: {str(e)}")

        logger.info("✅ 应用启动完成")

    except Exception as e:
        logger.error(f"❌ 应用启动失败: {str(e)}")
        raise

    yield  # 应用运行期间

    # 关闭时执行
    logger.info("👋 应用正在关闭...")
    logger.info("✅ 应用已安全关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例

    Returns:
        FastAPI: 配置好的应用实例
    """
    # 确保必要目录存在
    AppConfig.ensure_directories()

    # 创建FastAPI应用实例
    app = FastAPI(
        title=AppConfig.TITLE,
        description=AppConfig.DESCRIPTION,
        version=AppConfig.VERSION,
        lifespan=lifespan,  # 使用现代化的lifespan事件
    )

    # 添加自定义中间件（按执行顺序添加）
    app.add_middleware(ErrorHandlingMiddleware)  # 最外层：错误处理
    app.add_middleware(AuthMiddleware)  # 身份验证中间件
    app.add_middleware(SecurityHeadersMiddleware)  # 安全头
    app.add_middleware(PerformanceMiddleware, slow_request_threshold=2.0)  # 性能监控
    app.add_middleware(RequestLoggingMiddleware)  # 请求日志

    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=AppConfig.CORS_ORIGINS,
        allow_credentials=AppConfig.CORS_CREDENTIALS,
        allow_methods=AppConfig.CORS_METHODS,
        allow_headers=AppConfig.CORS_HEADERS,
    )

    # 配置静态文件服务
    app.mount(
        "/static", StaticFiles(directory=str(AppConfig.STATIC_DIR)), name="static"
    )

    # 注册路由
    main_router = create_main_router()
    api_router = create_api_router()

    app.include_router(main_router)
    app.include_router(api_router)

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        reload=AppConfig.RELOAD,
    )
