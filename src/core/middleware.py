#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中间件模块 - 现代化请求处理
提供请求日志、错误处理、性能监控等中间件

作者: 百万年薪全栈工程师
特性:
- 请求日志记录
- 错误处理和追踪
- 性能监控
- 安全头设置
"""

import time
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.logger import LoggerManager, get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件

    记录所有HTTP请求的详细信息，包括耗时、状态码等
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("http")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志

        Args:
            request: HTTP请求对象
            call_next: 下一个处理器

        Returns:
            Response: HTTP响应对象
        """
        start_time = time.time()

        # 获取请求信息
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        # user_agent = request.headers.get("user-agent", "Unknown")  # 暂未使用
        client_ip = request.client.host if request.client else "Unknown"

        try:
            # 处理请求
            response = await call_next(request)

            # 计算耗时
            duration = time.time() - start_time

            # 记录成功请求
            log_message = f"{method} {path}"
            if query_params:
                log_message += f"?{query_params}"
            log_message += f" - {response.status_code} - {duration:.3f}s - {client_ip}"

            if response.status_code >= 400:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)

            return response

        except Exception as e:
            # 计算耗时
            duration = time.time() - start_time

            # 记录错误请求
            error_message = (
                f"{method} {path} - ERROR - {duration:.3f}s - {client_ip} - {str(e)}"
            )
            self.logger.error(error_message)

            # 重新抛出异常
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件

    统一处理应用中的异常，提供友好的错误响应
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("error")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并捕获异常

        Args:
            request: HTTP请求对象
            call_next: 下一个处理器

        Returns:
            Response: HTTP响应对象
        """
        try:
            return await call_next(request)

        except Exception as e:
            # 记录详细错误信息
            error_context = {
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else "Unknown",
            }

            self.logger.error(
                f"未处理的异常: {type(e).__name__}: {str(e)}",
                extra={"context": error_context},
                exc_info=True,
            )

            # 返回友好的错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "error": "服务器内部错误",
                    "message": "请稍后重试或联系管理员",
                    "type": type(e).__name__,
                    "timestamp": time.time(),
                },
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件

    为所有响应添加安全相关的HTTP头
    """

    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:;"
            ),
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """添加安全头到响应

        Args:
            request: HTTP请求对象
            call_next: 下一个处理器

        Returns:
            Response: 添加了安全头的HTTP响应对象
        """
        response = await call_next(request)

        # 添加安全头
        for header, value in self.security_headers.items():
            response.headers[header] = value

        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件

    监控请求性能，记录慢请求
    """

    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.logger = get_logger("performance")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """监控请求性能

        Args:
            request: HTTP请求对象
            call_next: 下一个处理器

        Returns:
            Response: HTTP响应对象
        """
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # 记录慢请求
        if duration > self.slow_request_threshold:
            self.logger.warning(
                f"慢请求检测: {request.method} {request.url.path} - {duration:.3f}s"
            )

        # 添加性能头
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        return response
