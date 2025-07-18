#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园招聘数据分析平台 - 项目入口文件
使用模块化架构的现代化版本
"""

import sys
from pathlib import Path


# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.app import app
from src.core.config import AppConfig


def main() -> None:
    """主函数 - 启动应用服务器

    使用uvicorn作为ASGI服务器，支持热重载和自动重启
    """
    import uvicorn

    print("=" * 60)
    print(f"🎯 {AppConfig.TITLE}")
    print(f"📦 版本: {AppConfig.VERSION}")
    print(f"🌐 访问地址: http://{AppConfig.HOST}:{AppConfig.PORT}")
    print(f"🔄 热重载: {'开启' if AppConfig.RELOAD else '关闭'}")
    print("=" * 60)

    try:
        uvicorn.run(
            "main:app",
            host=AppConfig.HOST,
            port=AppConfig.PORT,
            reload=AppConfig.RELOAD,
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")


if __name__ == "__main__":
    main()
