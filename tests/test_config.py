# -*- coding: utf-8 -*-
"""
配置模块测试

测试应用配置的各项功能
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config import AppConfig


class TestAppConfig:
    """应用配置测试类"""

    def test_default_values(self):
        """测试默认配置值"""
        assert AppConfig.TITLE == "校园招聘数据分析平台"
        assert AppConfig.VERSION == "2.0.0"
        assert AppConfig.HOST == "0.0.0.0"
        assert AppConfig.PORT == 8000
        assert AppConfig.DEBUG is True

    @patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "9000"})
    def test_environment_variables(self):
        """测试环境变量覆盖"""
        # 重新导入以获取新的环境变量值
        from importlib import reload

        from src.core import config

        reload(config)

        assert config.AppConfig.HOST == "127.0.0.1"
        assert config.AppConfig.PORT == 9000

    def test_directory_paths(self):
        """测试目录路径配置"""
        assert AppConfig.BASE_DIR.exists()
        assert AppConfig.STATIC_DIR.name == "static"
        assert AppConfig.UPLOADS_DIR.name == "uploads"
        assert AppConfig.REPORTS_DIR.name == "reports"
        assert AppConfig.LOGS_DIR.name == "logs"

    def test_validate_config_success(self):
        """测试配置验证成功"""
        assert AppConfig.validate_config() is True

    def test_validate_config_failure(self):
        """测试配置验证失败"""
        # 临时修改PORT为无效值
        original_port = AppConfig.PORT
        try:
            AppConfig.PORT = "invalid_port"
            result = AppConfig.validate_config()
            assert result is False
        finally:
            AppConfig.PORT = original_port

    def test_ensure_directories(self):
        """测试目录创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 模拟目录路径
            with patch.object(
                AppConfig, "UPLOADS_DIR", temp_path / "uploads"
            ), patch.object(
                AppConfig, "REPORTS_DIR", temp_path / "reports"
            ), patch.object(
                AppConfig, "LOGS_DIR", temp_path / "logs"
            ):

                AppConfig.ensure_directories()

                assert (temp_path / "uploads").exists()
                assert (temp_path / "reports").exists()
                assert (temp_path / "logs").exists()

    def test_get_info(self):
        """测试配置信息获取"""
        info = AppConfig.get_info()

        assert isinstance(info, dict)
        assert "title" in info
        assert "version" in info
        assert "host" in info
        assert "port" in info
        assert "debug" in info

        assert info["title"] == AppConfig.TITLE
        assert info["version"] == AppConfig.VERSION

    def test_cors_origins(self):
        """测试CORS配置"""
        assert isinstance(AppConfig.CORS_ORIGINS, list)
        assert len(AppConfig.CORS_ORIGINS) > 0
        assert "*" in AppConfig.CORS_ORIGINS  # 开发环境允许所有来源
