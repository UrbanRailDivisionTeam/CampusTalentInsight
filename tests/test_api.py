# -*- coding: utf-8 -*-
"""
API路由测试

测试FastAPI应用的各个端点
"""

import io
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app


class TestAPI:
    """API测试类"""

    def setup_method(self):
        """测试前准备"""
        self.client = TestClient(app)

        # 创建测试Excel文件
        self.test_data = pd.DataFrame(
            {
                "序号": [1, 2, 3],
                "姓名": ["张三", "李四", "王五"],
                "性别": ["男", "女", "男"],
                "年龄": [25, 23, 27],
                "出生日期": ["1998-01-01", "2000-05-15", "1996-12-20"],
                "政治面貌": ["中共党员", "共青团员", "群众"],
                "籍贯": ["湖南长沙", "北京朝阳", "广东深圳"],
                "应聘状态": ["已签约", "已签约", "已签约"],
                "应聘职位": ["软件工程师", "产品经理", "数据分析师"],
                "最高学历": ["本科", "硕士", "本科"],
                "最高学历专业": ["计算机科学", "工商管理", "统计学"],
                "专业类型": ["工科", "管理", "理科"],
                "最高学历毕业院校": ["清华大学", "北京大学", "中南大学"],
                "最高学历毕业院校类别": ["C9联盟", "C9联盟", "211"],
            }
        )

    def create_test_excel_file(self) -> io.BytesIO:
        """创建测试Excel文件"""
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            self.test_data.to_excel(writer, index=False, sheet_name="Sheet1")
        buffer.seek(0)
        return buffer

    def test_root_endpoint(self):
        """测试根路径"""
        response = self.client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_check(self):
        """测试健康检查"""
        response = self.client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "uptime" in data

    def test_upload_valid_file(self):
        """测试上传有效文件"""
        excel_buffer = self.create_test_excel_file()

        files = {
            "file": (
                "test_data.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        response = self.client.post("/api/upload", files=files)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "statistics" in data
        assert "file_id" in data

    def test_upload_invalid_file_type(self):
        """测试上传无效文件类型"""
        files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}

        response = self.client.post("/api/upload", files=files)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "Excel" in data["detail"]

    def test_upload_no_file(self):
        """测试未上传文件"""
        response = self.client.post("/api/upload")
        assert response.status_code == 422  # Validation error

    def test_upload_empty_file(self):
        """测试上传空文件"""
        files = {
            "file": (
                "empty.xlsx",
                io.BytesIO(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        response = self.client.post("/api/upload", files=files)
        assert response.status_code == 400

    @patch("src.core.data_processor.DataProcessor.validate_data")
    def test_upload_invalid_data_structure(self, mock_validate):
        """测试上传数据结构无效的文件"""
        mock_validate.return_value = (False, "缺少必需列: 姓名, 性别")

        excel_buffer = self.create_test_excel_file()
        files = {
            "file": (
                "invalid_data.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        response = self.client.post("/api/upload", files=files)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "缺少必需列" in data["detail"]

    def test_get_statistics_valid_file(self):
        """测试获取有效文件的统计信息"""
        # 首先上传文件
        excel_buffer = self.create_test_excel_file()
        files = {
            "file": (
                "test_data.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        upload_response = self.client.post("/api/upload", files=files)
        assert upload_response.status_code == 200

        file_id = upload_response.json()["file_id"]

        # 获取统计信息
        response = self.client.get(f"/api/statistics/{file_id}")
        assert response.status_code == 200

        data = response.json()
        assert "total_count" in data
        assert "political_status" in data
        assert "gender" in data
        assert data["total_count"] == 3

    def test_get_statistics_invalid_file_id(self):
        """测试获取无效文件ID的统计信息"""
        response = self.client.get("/api/statistics/invalid_file_id")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "文件不存在" in data["detail"]

    def test_generate_report_valid_file(self):
        """测试生成有效文件的报告"""
        # 首先上传文件
        excel_buffer = self.create_test_excel_file()
        files = {
            "file": (
                "test_data.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        upload_response = self.client.post("/api/upload", files=files)
        assert upload_response.status_code == 200

        file_id = upload_response.json()["file_id"]

        # 生成报告
        response = self.client.post(f"/api/generate-report/{file_id}")
        assert response.status_code == 200

        # 检查响应头
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

        # 检查内容不为空
        assert len(response.content) > 0

    def test_generate_report_invalid_file_id(self):
        """测试生成无效文件ID的报告"""
        response = self.client.post("/api/generate-report/invalid_file_id")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "文件不存在" in data["detail"]

    def test_list_files(self):
        """测试获取文件列表"""
        # 上传几个文件
        for i in range(2):
            excel_buffer = self.create_test_excel_file()
            files = {
                "file": (
                    f"test_data_{i}.xlsx",
                    excel_buffer,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            response = self.client.post("/api/upload", files=files)
            assert response.status_code == 200

        # 获取文件列表
        response = self.client.get("/api/files")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        # 检查文件信息结构
        for file_info in data:
            assert "file_id" in file_info
            assert "filename" in file_info
            assert "upload_time" in file_info
            assert "record_count" in file_info

    def test_delete_file_valid_id(self):
        """测试删除有效文件"""
        # 首先上传文件
        excel_buffer = self.create_test_excel_file()
        files = {
            "file": (
                "test_data.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        upload_response = self.client.post("/api/upload", files=files)
        assert upload_response.status_code == 200

        file_id = upload_response.json()["file_id"]

        # 删除文件
        response = self.client.delete(f"/api/files/{file_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]

        # 验证文件已被删除
        get_response = self.client.get(f"/api/statistics/{file_id}")
        assert get_response.status_code == 404

    def test_delete_file_invalid_id(self):
        """测试删除无效文件ID"""
        response = self.client.delete("/api/files/invalid_file_id")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "文件不存在" in data["detail"]

    def test_cors_headers(self):
        """测试CORS头部"""
        response = self.client.options("/")
        # FastAPI自动处理CORS，检查基本响应
        assert response.status_code in [200, 405]  # OPTIONS可能不被支持

    def test_error_handling(self):
        """测试错误处理"""
        # 测试不存在的端点
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404

    @patch("src.core.data_processor.DataProcessor.calculate_statistics")
    def test_internal_server_error(self, mock_calculate):
        """测试内部服务器错误"""
        mock_calculate.side_effect = Exception("Internal error")

        excel_buffer = self.create_test_excel_file()
        files = {
            "file": (
                "test_data.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        response = self.client.post("/api/upload", files=files)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
