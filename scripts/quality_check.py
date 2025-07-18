#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检查脚本

功能:
- 检查代码格式
- 运行类型检查
- 执行单元测试
- 生成质量报告

使用方法:
    python scripts/quality_check.py
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class QualityChecker:
    """代码质量检查器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.results: List[Tuple[str, bool, str]] = []

    def run_command(self, command: List[str], description: str) -> bool:
        """运行命令并记录结果

        Args:
            command: 要执行的命令列表
            description: 检查描述

        Returns:
            bool: 命令是否成功执行
        """
        print(f"\n🔍 {description}...")
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"✅ {description} - 通过")
            self.results.append((description, True, result.stdout))
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} - 失败")
            print(f"错误输出: {e.stderr}")
            self.results.append((description, False, e.stderr))
            return False
        except FileNotFoundError:
            print(f"⚠️ {description} - 工具未安装")
            self.results.append((description, False, "工具未安装"))
            return False

    def check_black_format(self) -> bool:
        """检查代码格式 (Black)"""
        return self.run_command(
            ["uv", "run", "black", "--check", "--diff", "src/", "main.py"],
            "代码格式检查 (Black)",
        )

    def check_mypy_types(self) -> bool:
        """检查类型注解 (MyPy)"""
        return self.run_command(["uv", "run", "mypy", "src/"], "类型检查 (MyPy)")

    def check_flake8_style(self) -> bool:
        """检查代码风格 (Flake8)"""
        return self.run_command(
            ["uv", "run", "flake8", "src/", "main.py"], "代码风格检查 (Flake8)"
        )

    def run_tests(self) -> bool:
        """运行单元测试"""
        return self.run_command(["uv", "run", "pytest", "-v"], "单元测试")

    def check_imports(self) -> bool:
        """检查导入排序"""
        return self.run_command(
            ["uv", "run", "isort", "--check-only", "--diff", "src/", "main.py"],
            "导入排序检查 (isort)",
        )

    def generate_report(self) -> None:
        """生成质量检查报告"""
        print("\n" + "=" * 60)
        print("📊 代码质量检查报告")
        print("=" * 60)

        passed = 0
        total = len(self.results)

        for description, success, output in self.results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{description:<30} {status}")
            if success:
                passed += 1

        print("\n" + "-" * 60)
        print(f"总计: {passed}/{total} 项检查通过")

        if passed == total:
            print("🎉 所有检查都通过了！代码质量良好。")
            return True
        else:
            print("⚠️ 部分检查未通过，请修复相关问题。")
            return False

    def run_all_checks(self) -> bool:
        """运行所有质量检查

        Returns:
            bool: 所有检查是否都通过
        """
        print("🚀 开始代码质量检查...")

        # 运行各项检查
        checks = [
            self.check_black_format,
            self.check_imports,
            self.check_flake8_style,
            self.check_mypy_types,
            self.run_tests,
        ]

        for check in checks:
            check()

        # 生成报告
        return self.generate_report()


def main():
    """主函数"""
    checker = QualityChecker()
    success = checker.run_all_checks()

    # 根据结果设置退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
