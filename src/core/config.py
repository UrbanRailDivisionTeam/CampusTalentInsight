#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置模块 - 现代化配置管理
管理应用的所有配置信息，支持环境变量和类型安全

作者: 百万年薪全栈工程师
特性:
- 环境变量支持
- 类型安全的配置
- 自动目录创建
- 配置验证
"""

import os
from pathlib import Path
from typing import List, Optional


class AppConfig:
    """应用配置类 - 现代化配置管理

    支持环境变量覆盖默认配置，提供类型安全的配置访问
    """

    # 应用基本信息
    TITLE = "校园招聘数据分析平台"
    DESCRIPTION = (
        "处理校园招聘签约名单Excel文件，实现数据解析、统计计算及可视化展示 - 重构版"
    )
    VERSION = "2.0.0"
    AUTHOR = "百万年薪全栈工程师"

    # 服务器配置 - 支持环境变量
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    RELOAD = os.getenv("RELOAD", "true").lower() == "true"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # 目录配置
    BASE_DIR = Path(__file__).parent.parent
    PROJECT_ROOT = BASE_DIR.parent  # 项目根目录
    STATIC_DIR = PROJECT_ROOT / "static"  # 修正：指向项目根目录的static
    UPLOADS_DIR = PROJECT_ROOT / "uploads"
    REPORTS_DIR = PROJECT_ROOT / "reports"  # 新增报告目录
    LOGS_DIR = PROJECT_ROOT / "logs"  # 新增日志目录

    # CORS配置 - 生产环境应该限制origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",  # 开发环境允许所有来源
    ]
    CORS_CREDENTIALS = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]

    # 文件上传配置
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    ALLOWED_EXTENSIONS = [".xlsx", ".xls"]
    MAX_DESCRIPTION_LENGTH = 500

    # 历史记录配置
    MAX_HISTORY_RECORDS = int(os.getenv("MAX_HISTORY_RECORDS", "10"))

    # 报告生成配置
    REPORT_TEMPLATE_DIR = PROJECT_ROOT / "templates"
    REPORT_FORMATS = ["markdown", "html", "pdf"]

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def ensure_directories(cls) -> None:
        """确保必要的目录存在

        创建所有必需的目录，包括上传、静态文件、报告和日志目录
        """
        directories = [
            cls.UPLOADS_DIR,
            cls.STATIC_DIR,
            cls.REPORTS_DIR,
            cls.LOGS_DIR,
            cls.REPORT_TEMPLATE_DIR,
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)

        # 创建.gitkeep文件保持目录结构
        for directory in [cls.UPLOADS_DIR, cls.REPORTS_DIR, cls.LOGS_DIR]:
            gitkeep_file = directory / ".gitkeep"
            if not gitkeep_file.exists():
                gitkeep_file.touch()

    @classmethod
    def validate_config(cls) -> bool:
        """验证配置的有效性

        Returns:
            bool: 配置是否有效
        """
        try:
            # 验证端口范围
            if not (1 <= cls.PORT <= 65535):
                raise ValueError(f"端口号无效: {cls.PORT}")

            # 验证文件大小限制
            if cls.MAX_FILE_SIZE <= 0:
                raise ValueError(f"文件大小限制无效: {cls.MAX_FILE_SIZE}")

            # 验证历史记录数量
            if cls.MAX_HISTORY_RECORDS <= 0:
                raise ValueError(f"历史记录数量无效: {cls.MAX_HISTORY_RECORDS}")

            return True

        except Exception as e:
            print(f"❌ 配置验证失败: {e}")
            return False

    @classmethod
    def get_info(cls) -> dict:
        """获取配置信息摘要

        Returns:
            dict: 配置信息字典
        """
        return {
            "title": cls.TITLE,
            "version": cls.VERSION,
            "author": cls.AUTHOR,
            "host": cls.HOST,
            "port": cls.PORT,
            "debug": cls.DEBUG,
            "reload": cls.RELOAD,
            "max_file_size_mb": cls.MAX_FILE_SIZE // (1024 * 1024),
            "max_history_records": cls.MAX_HISTORY_RECORDS,
        }
