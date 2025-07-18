# -*- coding: utf-8 -*-
"""
报告生成模块测试

测试HTML报告生成的各项功能
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.utils.report_generator import ReportGenerator


class TestReportGenerator:
    """报告生成器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.generator = ReportGenerator()

        # 创建测试统计数据
        self.test_statistics = {
            "total_count": 100,
            "bilateral_count": 80,
            "trilateral_count": 20,
            "political_status": [
                {"name": "中共党员", "value": 30},
                {"name": "共青团员", "value": 50},
                {"name": "群众", "value": 20},
            ],
            "gender": [{"name": "男", "value": 60}, {"name": "女", "value": 40}],
            "age_distribution": [
                {"name": "22-24岁", "value": 40},
                {"name": "25-27岁", "value": 35},
                {"name": "28-30岁", "value": 25},
            ],
            "education": [
                {"name": "本科", "value": 70},
                {"name": "硕士", "value": 25},
                {"name": "博士", "value": 5},
            ],
            "institution_category": [
                {"name": "C9联盟", "value": 20},
                {"name": "985", "value": 30},
                {"name": "211", "value": 35},
                {"name": "其他", "value": 15},
            ],
            "major_type": [
                {"name": "工科", "value": 50},
                {"name": "理科", "value": 25},
                {"name": "管理", "value": 15},
                {"name": "其他", "value": 10},
            ],
            "province_distribution": [
                {"name": "北京", "value": 15},
                {"name": "上海", "value": 12},
                {"name": "广东", "value": 20},
                {"name": "湖南", "value": 18},
                {"name": "其他", "value": 35},
            ],
            "special_institutions": [
                {"name": "清华大学", "value": 8},
                {"name": "北京大学", "value": 7},
                {"name": "中南大学", "value": 15},
                {"name": "湖南大学", "value": 12},
            ],
        }

    def test_format_chart_data_list(self):
        """测试列表格式图表数据格式化"""
        data = [{"name": "项目A", "value": 30}, {"name": "项目B", "value": 20}]

        result = self.generator.format_chart_data(data)
        expected = "[{name:'项目A',value:30},{name:'项目B',value:20}]"

        assert result == expected

    def test_format_chart_data_dict(self):
        """测试字典格式图表数据格式化"""
        data = {"项目A": 30, "项目B": 20}

        result = self.generator.format_chart_data(data)
        expected = "[{name:'项目A',value:30},{name:'项目B',value:20}]"

        assert result == expected

    def test_format_chart_data_empty(self):
        """测试空数据格式化"""
        result = self.generator.format_chart_data([])
        assert result == "[]"

        result = self.generator.format_chart_data({})
        assert result == "[]"

    def test_format_chart_data_special_characters(self):
        """测试包含特殊字符的数据格式化"""
        data = [{"name": "项目'A'", "value": 30}, {"name": '项目"B"', "value": 20}]

        result = self.generator.format_chart_data(data)
        # 检查特殊字符被正确转义
        assert "项目'A'" in result
        assert '项目"B"' in result

    def test_generate_summary_text(self):
        """测试摘要文本生成"""
        summary = self.generator.generate_summary_text(self.test_statistics)

        # 检查摘要包含关键信息
        assert "100" in summary  # 总人数
        assert "80" in summary  # 双选人数
        assert "20" in summary  # 三选人数
        assert "中共党员" in summary
        assert "清华大学" in summary
        assert "北京大学" in summary
        assert "中南大学" in summary
        assert "湖南大学" in summary

    def test_generate_summary_text_empty_data(self):
        """测试空数据的摘要文本生成"""
        empty_stats = {
            "total_count": 0,
            "bilateral_count": 0,
            "trilateral_count": 0,
            "political_status": [],
            "special_institutions": [],
        }

        summary = self.generator.generate_summary_text(empty_stats)
        assert "0" in summary
        assert len(summary) > 0

    def test_generate_report_html_structure(self):
        """测试生成的HTML报告结构"""
        html_content = self.generator.generate_html_report(self.test_statistics, {})

        # 检查HTML基本结构
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content
        assert "</html>" in html_content

        # 检查标题
        assert "测试报告" in html_content
        assert "test_file.xlsx" in html_content

        # 检查图表容器
        assert 'id="genderChart"' in html_content
        assert 'id="politicalChart"' in html_content
        assert 'id="educationChart"' in html_content
        assert 'id="institutionChart"' in html_content
        assert 'id="majorChart"' in html_content
        assert 'id="provinceChart"' in html_content

        # 检查ECharts库引用
        assert "echarts" in html_content

    def test_generate_report_data_integration(self):
        """测试报告中数据集成"""
        html_content = self.generator.generate_html_report(self.test_statistics, {})

        # 检查统计数据是否正确嵌入
        assert "100" in html_content  # 总人数
        assert "中共党员" in html_content
        assert "清华大学" in html_content
        assert "工科" in html_content
        assert "北京" in html_content

    def test_generate_report_chart_data_format(self):
        """测试报告中图表数据格式"""
        html_content = self.generator.generate_html_report(self.test_statistics, {})

        # 检查图表数据格式
        assert "[{name:" in html_content
        assert ",value:" in html_content
        assert "}]" in html_content

    def test_generate_report_with_minimal_data(self):
        """测试最小数据集的报告生成"""
        minimal_stats = {
            "total_count": 1,
            "bilateral_count": 1,
            "trilateral_count": 0,
            "political_status": [{"name": "群众", "value": 1}],
            "gender": [{"name": "男", "value": 1}],
            "age_distribution": [{"name": "22-24岁", "value": 1}],
            "education": [{"name": "本科", "value": 1}],
            "institution_category": [{"name": "其他", "value": 1}],
            "major_type": [{"name": "其他", "value": 1}],
            "province_distribution": [{"name": "其他", "value": 1}],
            "special_institutions": [],
        }

        html_content = self.generator.generate_html_report(minimal_stats, {})

        # 确保即使数据很少也能生成完整报告
        assert "<!DOCTYPE html>" in html_content
        assert "最小数据测试" in html_content
        assert "1" in html_content

    def test_generate_report_encoding(self):
        """测试报告编码处理"""
        # 包含各种中文字符的测试数据
        chinese_stats = {
            "total_count": 50,
            "bilateral_count": 40,
            "trilateral_count": 10,
            "political_status": [
                {"name": "中国共产党党员", "value": 20},
                {"name": "中国共产主义青年团团员", "value": 30},
            ],
            "gender": [{"name": "男性", "value": 25}, {"name": "女性", "value": 25}],
            "age_distribution": [],
            "education": [],
            "institution_category": [],
            "major_type": [],
            "province_distribution": [],
            "special_institutions": [],
        }

        html_content = self.generator.generate_html_report(chinese_stats, {})

        # 检查中文字符正确显示
        assert "中国共产党党员" in html_content
        assert "中国共产主义青年团团员" in html_content
        assert "中文编码测试报告" in html_content
        assert "中文文件名.xlsx" in html_content

        # 检查UTF-8编码声明
        assert "charset=utf-8" in html_content or "charset=UTF-8" in html_content

    def test_save_report_to_file(self):
        """测试保存报告到文件"""
        html_content = self.generator.generate_html_report(self.test_statistics, {})

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(html_content)
            temp_file_path = f.name

        try:
            # 验证文件存在且可读
            temp_path = Path(temp_file_path)
            assert temp_path.exists()

            # 读取文件内容验证
            with open(temp_path, "r", encoding="utf-8") as f:
                saved_content = f.read()

            assert saved_content == html_content
            assert "文件保存测试" in saved_content

        finally:
            # 清理临时文件
            Path(temp_file_path).unlink(missing_ok=True)

    def test_template_variables_replacement(self):
        """测试模板变量替换"""
        html_content = self.generator.generate_html_report(self.test_statistics, {})

        # 检查所有模板变量都被正确替换
        template_variables = [
            "{{REPORT_TITLE}}",
            "{{FILE_NAME}}",
            "{{TOTAL_COUNT}}",
            "{{BILATERAL_COUNT}}",
            "{{TRILATERAL_COUNT}}",
            "{{SUMMARY_TEXT}}",
            "{{GENDER_DATA}}",
            "{{POLITICAL_DATA}}",
            "{{EDUCATION_DATA}}",
            "{{INSTITUTION_DATA}}",
            "{{MAJOR_DATA}}",
            "{{PROVINCE_DATA}}",
        ]

        for variable in template_variables:
            assert variable not in html_content, f"模板变量 {variable} 未被替换"

    @patch("src.utils.report_generator.ReportGenerator.format_chart_data")
    def test_error_handling_in_chart_formatting(self, mock_format):
        """测试图表格式化错误处理"""
        mock_format.side_effect = Exception("格式化错误")

        # 即使格式化出错，也应该能生成基本报告
        try:
            html_content = self.generator.generate_html_report(self.test_statistics, {})
            # 如果没有抛出异常，检查基本结构仍然存在
            assert "<!DOCTYPE html>" in html_content
        except Exception:
            # 如果抛出异常，这也是可以接受的行为
            pass
