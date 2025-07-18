#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化部署脚本

功能:
- 环境检查
- 依赖安装
- 静态资源构建
- 应用启动

使用方法:
    python scripts/deploy.py [--env production|development]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


class Deployer:
    """部署管理器"""

    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.is_production = environment == "production"

    def run_command(self, command: List[str], description: str) -> bool:
        """运行命令

        Args:
            command: 要执行的命令列表
            description: 操作描述

        Returns:
            bool: 命令是否成功执行
        """
        print(f"\n🔧 {description}...")
        try:
            result = subprocess.run(command, cwd=self.project_root, check=True)
            print(f"✅ {description} - 完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} - 失败 (退出码: {e.returncode})")
            return False
        except FileNotFoundError:
            print(f"⚠️ {description} - 工具未找到")
            return False

    def check_environment(self) -> bool:
        """检查运行环境"""
        print(f"🌍 检查 {self.environment} 环境...")

        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
            print("需要Python 3.8或更高版本")
            return False

        print(
            f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # 检查uv
        if not self.run_command(["uv", "--version"], "检查uv包管理器"):
            print("请安装uv: https://docs.astral.sh/uv/getting-started/installation/")
            return False

        # 检查Node.js (用于CSS构建)
        if not self.run_command(["node", "--version"], "检查Node.js"):
            print("请安装Node.js用于CSS构建")
            return False

        return True

    def install_dependencies(self) -> bool:
        """安装依赖"""
        print("\n📦 安装依赖...")

        # 安装Python依赖
        if not self.run_command(["uv", "sync"], "安装Python依赖"):
            return False

        # 安装Node.js依赖
        if not self.run_command(["npm", "install"], "安装Node.js依赖"):
            return False

        return True

    def build_assets(self) -> bool:
        """构建静态资源"""
        print("\n🎨 构建静态资源...")

        # 构建CSS
        css_command = ["npm", "run", "build-css"]
        if not self.run_command(css_command, "构建TailwindCSS"):
            return False

        return True

    def setup_directories(self) -> bool:
        """设置必要的目录"""
        print("\n📁 设置目录结构...")

        directories = [
            self.project_root / "uploads",
            self.project_root / "reports",
            self.project_root / "logs",
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"✅ 目录已创建: {directory.name}/")

        return True

    def run_quality_checks(self) -> bool:
        """运行代码质量检查"""
        if self.is_production:
            print("\n🔍 运行代码质量检查...")
            quality_script = self.project_root / "scripts" / "quality_check.py"
            if quality_script.exists():
                return self.run_command(["python", str(quality_script)], "代码质量检查")
        return True

    def start_application(self) -> bool:
        """启动应用"""
        print(f"\n🚀 启动应用 ({self.environment} 模式)...")

        if self.is_production:
            # 生产环境启动
            command = [
                "uv",
                "run",
                "uvicorn",
                "main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--workers",
                "4",
            ]
        else:
            # 开发环境启动
            command = ["uv", "run", "python", "main.py"]

        print(f"执行命令: {' '.join(command)}")
        print("\n" + "=" * 60)
        print(f"🎯 {self.environment.title()} 环境启动完成!")
        print("🌐 访问地址: http://localhost:8000")
        print("按 Ctrl+C 停止服务器")
        print("=" * 60)

        try:
            subprocess.run(command, cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n👋 应用已停止")

        return True

    def deploy(self) -> bool:
        """执行完整部署流程

        Returns:
            bool: 部署是否成功
        """
        print("🚀 开始自动化部署...")
        print(f"📋 环境: {self.environment}")
        print(f"📂 项目路径: {self.project_root}")

        steps = [
            ("环境检查", self.check_environment),
            ("安装依赖", self.install_dependencies),
            ("构建资源", self.build_assets),
            ("设置目录", self.setup_directories),
        ]

        # 生产环境额外检查
        if self.is_production:
            steps.append(("质量检查", self.run_quality_checks))

        # 执行部署步骤
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ 部署失败: {step_name}")
                return False

        print("\n✅ 部署准备完成!")

        # 启动应用
        return self.start_application()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化部署脚本")
    parser.add_argument(
        "--env",
        choices=["development", "production"],
        default="development",
        help="部署环境 (默认: development)",
    )

    args = parser.parse_args()

    deployer = Deployer(args.env)
    success = deployer.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
