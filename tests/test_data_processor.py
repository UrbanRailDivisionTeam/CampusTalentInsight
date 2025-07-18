# -*- coding: utf-8 -*-
"""
数据处理模块测试

测试Excel数据处理的各项功能
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.core.data_processor import DataProcessor


class TestDataProcessor:
    """数据处理器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.processor = DataProcessor()

        # 创建测试数据
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

    def test_required_columns(self):
        """测试必需列定义"""
        expected_columns = [
            "序号",
            "姓名",
            "性别",
            "年龄",
            "出生日期",
            "政治面貌",
            "籍贯",
            "应聘状态",
            "应聘职位",
            "最高学历",
            "最高学历专业",
            "专业类型",
            "最高学历毕业院校",
            "最高学历毕业院校类别",
        ]

        assert DataProcessor.REQUIRED_COLUMNS == expected_columns

    def test_classify_institution_c9(self):
        """测试C9联盟院校分类"""
        row = pd.Series({"最高学历毕业院校类别": "C9联盟"})
        result = DataProcessor.classify_institution(row)
        assert result == "C9联盟"

    def test_classify_institution_985(self):
        """测试985院校分类"""
        row = pd.Series({"最高学历毕业院校类别": "985"})
        result = DataProcessor.classify_institution(row)
        assert result == "985"

    def test_classify_institution_overseas_qs1_50(self):
        """测试QS1-50海外院校分类"""
        row = pd.Series({"最高学历毕业院校类别": "海外院校,QS1-50"})
        result = DataProcessor.classify_institution(row)
        assert result == "QS1-50"

    def test_classify_institution_overseas_qs100(self):
        """测试QS100海外院校分类"""
        row = pd.Series({"最高学历毕业院校类别": "海外院校,QS100"})
        result = DataProcessor.classify_institution(row)
        assert result == "QS100"

    def test_classify_institution_other_overseas(self):
        """测试其他海外院校分类"""
        row = pd.Series({"最高学历毕业院校类别": "海外院校"})
        result = DataProcessor.classify_institution(row)
        assert result == "其他海外院校"

    def test_classify_institution_unknown(self):
        """测试未知院校分类"""
        row = pd.Series({"最高学历毕业院校类别": "未知类型"})
        result = DataProcessor.classify_institution(row)
        assert result == "其他"

    def test_validate_data_success(self):
        """测试数据验证成功"""
        is_valid, message = self.processor.validate_data(self.test_data)
        assert is_valid is True
        assert "验证通过" in message

    def test_validate_data_missing_columns(self):
        """测试缺少必需列"""
        incomplete_data = self.test_data.drop(columns=["姓名", "性别"])
        is_valid, message = self.processor.validate_data(incomplete_data)
        assert is_valid is False
        assert "缺少必需列" in message

    def test_validate_data_empty(self):
        """测试空数据"""
        empty_data = pd.DataFrame()
        is_valid, message = self.processor.validate_data(empty_data)
        assert is_valid is False
        assert "数据为空" in message

    def test_enhance_data(self):
        """测试数据增强"""
        enhanced_data = self.processor.enhance_data(self.test_data)

        # 检查新增列
        expected_new_columns = [
            "院校分类",
            "籍贯省份",
            "出生年代",
            "年龄段",
            "是否党员",
        ]

        for column in expected_new_columns:
            assert column in enhanced_data.columns

        # 检查数据行数不变
        assert len(enhanced_data) == len(self.test_data)

    def test_extract_province(self):
        """测试省份提取"""
        test_cases = [
            ("湖南长沙", "湖南"),
            ("北京朝阳", "北京"),
            ("广东深圳", "广东"),
            ("上海浦东", "上海"),
            ("重庆渝中", "重庆"),
            ("天津和平", "天津"),
            ("内蒙古呼和浩特", "内蒙古"),
            ("新疆乌鲁木齐", "新疆"),
            ("西藏拉萨", "西藏"),
            ("宁夏银川", "宁夏"),
            ("广西南宁", "广西"),
            ("未知地区", "其他"),
        ]

        for location, expected_province in test_cases:
            result = self.processor.extract_province(location)
            assert result == expected_province

    def test_calculate_age_group(self):
        """测试年龄段计算"""
        test_cases = [(22, "00后"), (25, "95后"), (28, "90后"), (35, "其他")]

        for age, expected_group in test_cases:
            result = self.processor.calculate_age_group(age)
            assert result == expected_group

    def test_calculate_birth_decade(self):
        """测试出生年代计算"""
        test_cases = [
            ("2002-01-01", "00后"),
            ("1998-05-15", "95后"),
            ("1992-12-20", "90后"),
            ("1985-03-10", "其他"),
        ]

        for birth_date, expected_decade in test_cases:
            result = self.processor.calculate_birth_decade(birth_date)
            assert result == expected_decade

    def test_calculate_statistics(self):
        """测试统计计算"""
        enhanced_data = self.processor.enhance_data(self.test_data)
        stats = self.processor.calculate_statistics(enhanced_data)

        # 检查统计结果结构
        expected_keys = [
            "total_count",
            "bilateral_count",
            "trilateral_count",
            "political_status",
            "gender",
            "age_distribution",
            "education",
            "institution_category",
            "major_type",
            "province_distribution",
            "special_institutions",
        ]

        for key in expected_keys:
            assert key in stats

        # 检查基本统计
        assert stats["total_count"] == 3
        assert isinstance(stats["political_status"], list)
        assert isinstance(stats["gender"], list)

    @pytest.mark.parametrize(
        "political_status,expected",
        [
            ("中共党员", True),
            ("中共预备党员", True),
            ("共青团员", False),
            ("群众", False),
        ],
    )
    def test_is_party_member(self, political_status, expected):
        """测试党员判断"""
        result = self.processor.is_party_member(political_status)
        assert result == expected
