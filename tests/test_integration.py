# -*- coding: utf-8 -*-
"""
集成测试

测试应用的端到端功能和模块间集成
"""

import io
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from src.core.config import AppConfig
from src.core.data_processor import DataProcessor
from src.utils.report_generator import ReportGenerator


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """测试前准备"""
        self.client = TestClient(app)
        self.processor = DataProcessor()
        self.generator = ReportGenerator()

        # 创建完整的测试数据集
        self.comprehensive_test_data = pd.DataFrame(
            {
                "序号": list(range(1, 51)),
                "姓名": [f"测试用户{i}" for i in range(1, 51)],
                "性别": ["男" if i % 2 == 0 else "女" for i in range(1, 51)],
                "年龄": [22 + (i % 8) for i in range(1, 51)],
                "出生日期": [
                    f"{1995 + (i % 8)}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
                    for i in range(1, 51)
                ],
                "政治面貌": [
                    "中共党员" if i % 3 == 0 else "共青团员" if i % 3 == 1 else "群众"
                    for i in range(1, 51)
                ],
                "籍贯": [f"省份{i % 10}城市{i % 5}" for i in range(1, 51)],
                "应聘状态": ["已签约" for _ in range(50)],
                "应聘职位": [f"职位{i % 5}" for i in range(1, 51)],
                "最高学历": [
                    "本科" if i % 4 != 0 else "硕士" if i % 8 != 0 else "博士"
                    for i in range(1, 51)
                ],
                "最高学历专业": [f"专业{i % 8}" for i in range(1, 51)],
                "专业类型": [
                    "工科" if i % 2 == 0 else "理科" if i % 3 == 0 else "管理"
                    for i in range(1, 51)
                ],
                "最高学历毕业院校": [f"大学{i % 15}" for i in range(1, 51)],
                "最高学历毕业院校类别": [
                    (
                        "C9联盟"
                        if i % 10 == 0
                        else "985" if i % 5 == 0 else "211" if i % 3 == 0 else "其他"
                    )
                    for i in range(1, 51)
                ],
            }
        )

    def create_comprehensive_excel_file(self) -> io.BytesIO:
        """创建综合测试Excel文件"""
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            self.comprehensive_test_data.to_excel(
                writer, index=False, sheet_name="Sheet1"
            )
        buffer.seek(0)
        return buffer

    def test_complete_workflow(self):
        """测试完整的工作流程：上传 -> 处理 -> 统计 -> 报告生成"""
        # 1. 上传文件
        excel_buffer = self.create_comprehensive_excel_file()
        files = {
            "file": (
                "comprehensive_test.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        upload_response = self.client.post("/api/upload", files=files)
        assert upload_response.status_code == 200

        upload_data = upload_response.json()
        assert upload_data["success"] is True
        assert "file_id" in upload_data
        assert "statistics" in upload_data

        file_id = upload_data["file_id"]

        # 2. 获取统计信息
        stats_response = self.client.get(f"/api/statistics/{file_id}")
        assert stats_response.status_code == 200

        statistics = stats_response.json()
        assert statistics["total_count"] == 50
        assert len(statistics["gender"]) == 2
        assert len(statistics["political_status"]) >= 2

        # 3. 生成报告
        report_response = self.client.post(f"/api/generate-report/{file_id}")
        assert report_response.status_code == 200
        assert "text/html" in report_response.headers["content-type"]
        assert len(report_response.content) > 1000  # 报告应该有足够的内容

        # 4. 验证报告内容
        report_html = report_response.content.decode("utf-8")
        assert "comprehensive_test.xlsx" in report_html
        assert "50" in report_html  # 总人数
        assert "echarts" in report_html.lower()  # 包含图表库

    def test_data_processing_pipeline(self):
        """测试数据处理管道"""
        # 1. 数据验证
        is_valid, message = self.processor.validate_data(self.comprehensive_test_data)
        assert is_valid is True
        assert "验证通过" in message

        # 2. 数据增强
        enhanced_data = self.processor.enhance_data(self.comprehensive_test_data)

        # 验证新增列
        expected_new_columns = [
            "院校分类",
            "籍贯省份",
            "出生年代",
            "年龄段",
            "是否党员",
        ]
        for column in expected_new_columns:
            assert column in enhanced_data.columns

        # 验证数据完整性
        assert len(enhanced_data) == len(self.comprehensive_test_data)
        assert not enhanced_data.isnull().any().any()  # 没有空值

        # 3. 统计计算
        statistics = self.processor.calculate_statistics(enhanced_data)

        # 验证统计结果
        assert statistics["total_count"] == 50
        assert isinstance(statistics["gender"], list)
        assert isinstance(statistics["political_status"], list)
        assert sum(item["value"] for item in statistics["gender"]) == 50

    def test_report_generation_pipeline(self):
        """测试报告生成管道"""
        # 1. 处理数据
        enhanced_data = self.processor.enhance_data(self.comprehensive_test_data)
        statistics = self.processor.calculate_statistics(enhanced_data)

        # 2. 生成报告
        html_report = self.generator.generate_report(
            statistics, "集成测试报告", "integration_test.xlsx"
        )

        # 3. 验证报告质量
        assert len(html_report) > 5000  # 报告应该有足够的内容
        assert "<!DOCTYPE html>" in html_report
        assert "集成测试报告" in html_report
        assert "integration_test.xlsx" in html_report

        # 验证所有图表都存在
        chart_ids = [
            "genderChart",
            "politicalChart",
            "educationChart",
            "institutionChart",
            "majorChart",
            "provinceChart",
        ]
        for chart_id in chart_ids:
            assert f'id="{chart_id}"' in html_report

        # 验证数据正确嵌入
        assert "50" in html_report  # 总人数
        assert "[{name:" in html_report  # 图表数据格式

    def test_error_recovery_and_handling(self):
        """测试错误恢复和处理"""
        # 1. 测试无效文件上传
        invalid_files = {
            "file": ("invalid.txt", io.BytesIO(b"invalid content"), "text/plain")
        }

        response = self.client.post("/api/upload", files=invalid_files)
        assert response.status_code == 400

        # 2. 测试缺少列的数据
        incomplete_data = self.comprehensive_test_data.drop(columns=["姓名", "性别"])
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            incomplete_data.to_excel(writer, index=False, sheet_name="Sheet1")
        buffer.seek(0)

        files = {
            "file": (
                "incomplete.xlsx",
                buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        response = self.client.post("/api/upload", files=files)
        assert response.status_code == 400
        assert "缺少必需列" in response.json()["detail"]

        # 3. 测试不存在的文件ID
        response = self.client.get("/api/statistics/nonexistent_id")
        assert response.status_code == 404

        response = self.client.post("/api/generate-report/nonexistent_id")
        assert response.status_code == 404

    def test_concurrent_file_operations(self):
        """测试并发文件操作"""
        file_ids = []

        # 上传多个文件
        for i in range(3):
            excel_buffer = self.create_comprehensive_excel_file()
            files = {
                "file": (
                    f"concurrent_test_{i}.xlsx",
                    excel_buffer,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            response = self.client.post("/api/upload", files=files)
            assert response.status_code == 200

            file_id = response.json()["file_id"]
            file_ids.append(file_id)

        # 验证所有文件都能正常访问
        for file_id in file_ids:
            stats_response = self.client.get(f"/api/statistics/{file_id}")
            assert stats_response.status_code == 200

            report_response = self.client.post(f"/api/generate-report/{file_id}")
            assert report_response.status_code == 200

        # 获取文件列表
        list_response = self.client.get("/api/files")
        assert list_response.status_code == 200

        file_list = list_response.json()
        assert len(file_list) >= 3

        # 删除文件
        for file_id in file_ids:
            delete_response = self.client.delete(f"/api/files/{file_id}")
            assert delete_response.status_code == 200

        # 验证文件已删除
        for file_id in file_ids:
            stats_response = self.client.get(f"/api/statistics/{file_id}")
            assert stats_response.status_code == 404

    def test_configuration_integration(self):
        """测试配置集成"""
        # 验证配置正确加载
        assert AppConfig.validate_config() is True

        # 验证目录创建
        AppConfig.ensure_directories()
        assert AppConfig.UPLOADS_DIR.exists()
        assert AppConfig.REPORTS_DIR.exists()
        assert AppConfig.LOGS_DIR.exists()

        # 验证应用信息
        info_response = self.client.get("/")
        assert info_response.status_code == 200

        app_info = info_response.json()
        assert app_info["version"] == AppConfig.VERSION
        assert app_info["status"] == "running"

    def test_health_check_integration(self):
        """测试健康检查集成"""
        health_response = self.client.get("/health")
        assert health_response.status_code == 200

        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "uptime" in health_data

    def test_large_dataset_handling(self):
        """测试大数据集处理"""
        # 创建较大的数据集（200条记录）
        large_data = pd.DataFrame(
            {
                "序号": list(range(1, 201)),
                "姓名": [f"用户{i}" for i in range(1, 201)],
                "性别": ["男" if i % 2 == 0 else "女" for i in range(1, 201)],
                "年龄": [22 + (i % 10) for i in range(1, 201)],
                "出生日期": [
                    f"{1990 + (i % 15)}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
                    for i in range(1, 201)
                ],
                "政治面貌": [
                    "中共党员" if i % 4 == 0 else "共青团员" if i % 4 == 1 else "群众"
                    for i in range(1, 201)
                ],
                "籍贯": [f"省份{i % 20}城市{i % 10}" for i in range(1, 201)],
                "应聘状态": ["已签约" for _ in range(200)],
                "应聘职位": [f"职位{i % 10}" for i in range(1, 201)],
                "最高学历": [
                    "本科" if i % 5 != 0 else "硕士" if i % 10 != 0 else "博士"
                    for i in range(1, 201)
                ],
                "最高学历专业": [f"专业{i % 15}" for i in range(1, 201)],
                "专业类型": [
                    "工科" if i % 3 == 0 else "理科" if i % 3 == 1 else "管理"
                    for i in range(1, 201)
                ],
                "最高学历毕业院校": [f"大学{i % 30}" for i in range(1, 201)],
                "最高学历毕业院校类别": [
                    (
                        "C9联盟"
                        if i % 20 == 0
                        else "985" if i % 10 == 0 else "211" if i % 5 == 0 else "其他"
                    )
                    for i in range(1, 201)
                ],
            }
        )

        # 创建Excel文件
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            large_data.to_excel(writer, index=False, sheet_name="Sheet1")
        buffer.seek(0)

        # 上传大文件
        files = {
            "file": (
                "large_dataset.xlsx",
                buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        upload_response = self.client.post("/api/upload", files=files)
        assert upload_response.status_code == 200

        file_id = upload_response.json()["file_id"]

        # 验证统计处理
        stats_response = self.client.get(f"/api/statistics/{file_id}")
        assert stats_response.status_code == 200

        statistics = stats_response.json()
        assert statistics["total_count"] == 200

        # 验证报告生成
        report_response = self.client.post(f"/api/generate-report/{file_id}")
        assert report_response.status_code == 200

        # 清理
        delete_response = self.client.delete(f"/api/files/{file_id}")
        assert delete_response.status_code == 200

    def test_memory_usage_optimization(self):
        """测试内存使用优化"""
        # 这个测试主要验证处理过程中没有明显的内存泄漏
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 执行多次上传和处理操作
        for i in range(5):
            excel_buffer = self.create_comprehensive_excel_file()
            files = {
                "file": (
                    f"memory_test_{i}.xlsx",
                    excel_buffer,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            upload_response = self.client.post("/api/upload", files=files)
            assert upload_response.status_code == 200

            file_id = upload_response.json()["file_id"]

            # 生成报告
            report_response = self.client.post(f"/api/generate-report/{file_id}")
            assert report_response.status_code == 200

            # 删除文件
            delete_response = self.client.delete(f"/api/files/{file_id}")
            assert delete_response.status_code == 200

            # 强制垃圾回收
            gc.collect()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 内存增长应该在合理范围内（小于100MB）
        assert (
            memory_increase < 100 * 1024 * 1024
        ), f"内存增长过多: {memory_increase / 1024 / 1024:.2f}MB"
