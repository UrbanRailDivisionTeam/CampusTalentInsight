# -*- coding: utf-8 -*-
"""
身份验证中间件
实现基于密码的访问控制
"""

import os
from pathlib import Path
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.logger import get_logger


class AuthMiddleware(BaseHTTPMiddleware):
    """身份验证中间件
    
    这个中间件会检查用户是否已经通过密码验证
    如果没有验证，会显示登录页面
    如果验证成功，会设置session标记
    """

    def __init__(self, app, password_file: str = "config/password.txt"):
        """
        初始化身份验证中间件
        
        Args:
            app: FastAPI应用实例
            password_file: 密码文件路径
        """
        super().__init__(app)
        self.password_file = password_file
        self.logger = get_logger("auth")
        
    def _load_password(self) -> str:
        """
        从文件中加载密码
        
        Returns:
            str: 密码字符串
        """
        try:
            password_path = Path(self.password_file)
            if password_path.exists():
                with open(password_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                self.logger.warning(f"密码文件不存在: {self.password_file}，使用默认密码")
                return "Zhuji123！"
        except Exception as e:
            self.logger.error(f"读取密码文件失败: {e}，使用默认密码")
            return "Zhuji123！"
    
    def _get_login_page(self) -> str:
        """
        生成登录页面HTML
        
        Returns:
            str: 登录页面HTML内容
        """
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>校园招聘数据分析平台 - 登录</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #666;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .login-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
        }
        
        .error-message {
            color: #e74c3c;
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
        }
        
        .success-message {
            color: #27ae60;
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🎓 校园招聘数据分析平台</h1>
            <p>请输入访问密码</p>
        </div>
        
        <form id="loginForm" method="post" action="/auth/login">
            <div class="form-group">
                <label for="password">访问密码</label>
                <input type="password" id="password" name="password" required placeholder="请输入密码">
            </div>
            
            <button type="submit" class="login-btn">登录</button>
        </form>
        
        <div id="message"></div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const messageDiv = document.getElementById('message');
            
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `password=${encodeURIComponent(password)}`
                });
                
                if (response.ok) {
                    messageDiv.innerHTML = '<div class="success-message">登录成功，正在跳转...</div>';
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    const result = await response.json();
                    messageDiv.innerHTML = `<div class="error-message">${result.detail || '登录失败'}</div>`;
                }
            } catch (error) {
                messageDiv.innerHTML = '<div class="error-message">网络错误，请重试</div>';
            }
        });
    </script>
</body>
</html>
        """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求的中间件逻辑
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理函数
            
        Returns:
            Response: 响应对象
        """
        # 静态文件不需要验证
        if (
            request.url.path.startswith("/static/") or
            request.url.path == "/favicon.ico"
        ):
            return await call_next(request)
        
        # 如果是POST请求到登录接口，处理登录逻辑
        if request.url.path == "/auth/login" and request.method == "POST":
            return await self._handle_login(request)
        
        # 如果是登出请求，直接传递给下一个中间件处理
        if request.url.path == "/auth/logout":
            return await call_next(request)
        
        # 检查是否已经登录（通过cookie检查）
        auth_token = request.cookies.get("auth_token")
        if auth_token == "authenticated":
            return await call_next(request)
        
        # 未登录，返回登录页面
        return HTMLResponse(content=self._get_login_page(), status_code=200)
    
    async def _handle_login(self, request: Request) -> Response:
        """
        处理登录请求
        
        Args:
            request: 请求对象
            
        Returns:
            Response: 响应对象
        """
        try:
            # 获取表单数据
            form_data = await request.form()
            password = form_data.get("password", "")
            
            # 验证密码
            correct_password = self._load_password()
            
            if password == correct_password:
                # 密码正确，设置认证cookie并重定向
                response = Response(
                    content='{"success": true, "message": "登录成功"}',
                    media_type="application/json"
                )
                response.set_cookie(
                    key="auth_token",
                    value="authenticated",
                    max_age=86400,  # 24小时
                    httponly=True,
                    secure=False,  # 在生产环境中应该设置为True
                    samesite="lax"
                )
                self.logger.info(f"用户登录成功，IP: {request.client.host}")
                return response
            else:
                # 密码错误
                self.logger.warning(f"登录失败，密码错误，IP: {request.client.host}")
                return Response(
                    content='{"success": false, "detail": "密码错误"}',
                    status_code=401,
                    media_type="application/json"
                )
                
        except Exception as e:
            self.logger.error(f"登录处理异常: {e}")
            return Response(
                content='{"success": false, "detail": "服务器错误"}',
                status_code=500,
                media_type="application/json"
            )