#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块 - 现代化日志管理
提供统一的日志配置和管理功能

作者: 百万年薪全栈工程师
特性:
- 结构化日志
- 多级别日志
- 文件轮转
- 彩色控制台输出
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.config import AppConfig


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器

    为不同级别的日志添加颜色，提升开发体验
    """

    # ANSI颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置
    }

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录

        Args:
            record: 日志记录对象

        Returns:
            str: 格式化后的日志字符串
        """
        # 添加颜色
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # 格式化时间
        record.asctime = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # 应用颜色
        record.levelname = f"{color}{record.levelname}{reset}"
        record.name = f"{color}{record.name}{reset}"

        return super().format(record)


class LoggerManager:
    """日志管理器 - 统一管理应用日志

    提供日志配置、创建和管理功能
    """

    _loggers = {}
    _configured = False

    @classmethod
    def setup_logging(cls) -> None:
        """设置全局日志配置

        配置根日志器和处理器
        """
        if cls._configured:
            return

        # 确保日志目录存在
        AppConfig.LOGS_DIR.mkdir(exist_ok=True, parents=True)

        # 获取根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, AppConfig.LOG_LEVEL.upper()))

        # 清除现有处理器
        root_logger.handlers.clear()

        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        console_handler.setFormatter(console_formatter)

        # 创建文件处理器
        log_file = AppConfig.LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(AppConfig.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)

        # 添加处理器到根日志器
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取指定名称的日志器

        Args:
            name: 日志器名称

        Returns:
            logging.Logger: 日志器实例
        """
        if not cls._configured:
            cls.setup_logging()

        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def log_request(
        cls,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_agent: Optional[str] = None,
    ) -> None:
        """记录HTTP请求日志

        Args:
            method: HTTP方法
            path: 请求路径
            status_code: 状态码
            duration: 请求耗时(秒)
            user_agent: 用户代理字符串
        """
        logger = cls.get_logger("http")

        # 根据状态码确定日志级别
        if status_code >= 500:
            level = logging.ERROR
        elif status_code >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO

        message = f"{method} {path} - {status_code} - {duration:.3f}s"
        if user_agent:
            message += f" - {user_agent}"

        logger.log(level, message)

    @classmethod
    def log_error(cls, error: Exception, context: Optional[str] = None) -> None:
        """记录错误日志

        Args:
            error: 异常对象
            context: 错误上下文信息
        """
        logger = cls.get_logger("error")

        message = f"{type(error).__name__}: {str(error)}"
        if context:
            message = f"{context} - {message}"

        logger.error(message, exc_info=True)


# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取日志器的便捷函数

    Args:
        name: 日志器名称

    Returns:
        logging.Logger: 日志器实例
    """
    return LoggerManager.get_logger(name)
