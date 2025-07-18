#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理模块
负责Excel文件的读取、验证、增强和统计计算
"""

from typing import Any, Dict, List, Optional

import pandas as pd


class DataProcessor:
    """数据处理器类 - 负责所有数据相关的操作"""

    # 必需的Excel列名
    REQUIRED_COLUMNS = [
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

    @staticmethod
    def classify_institution(row: pd.Series) -> str:
        """院校分类优先级实现

        Args:
            row: 数据行，包含院校类别信息

        Returns:
            str: 分类后的院校类别
        """
        institution_category = str(row.get("最高学历毕业院校类别", ""))

        # 海外院校优先级最高
        if "海外院校" in institution_category:
            if "QS1-50" in institution_category:
                return "QS1-50"
            elif "QS100" in institution_category:
                return "QS100"
            else:
                return "其他海外院校"

        # 国内院校按优先级分类
        categories = [
            "C9联盟",
            "985",
            "211",
            "轨道交通合作院校",
            "优势学科院校",
            "湖南省知名高校",
            "创新型大学",
            "其他签字增补院校",
        ]

        for category in categories:
            if category in institution_category:
                return category

        return "其他"

    @staticmethod
    def calculate_generation(birth_date: str) -> Optional[str]:
        """计算出生年代

        Args:
            birth_date: 出生日期字符串

        Returns:
            Optional[str]: 年代标识（如'95后'）或None
        """
        try:
            if pd.isna(birth_date) or birth_date == "":
                return None

            # 处理不同的日期格式
            birth_str = str(birth_date)
            if "-" in birth_str:
                year = int(birth_str.split("-")[0])
            elif "/" in birth_str:
                year = int(birth_str.split("/")[0])
            else:
                year = int(birth_str[:4])

            # 按年代分类
            if year >= 2005:
                return "05后"
            elif year >= 2000:
                return "00后"
            elif year >= 1995:
                return "95后"
            elif year >= 1990:
                return "90后"
            else:
                return None  # 不统计90前数据

        except (ValueError, IndexError):
            return None  # 无效日期处理

    @staticmethod
    def extract_province(location: str) -> str:
        """提取籍贯中的省份信息

        Args:
            location: 籍贯字符串

        Returns:
            str: 省份名称
        """
        if pd.isna(location) or location == "":
            return "未知"

        location_str = str(location)

        # 省份映射表
        province_map = {
            "湖南长沙": "湖南",
            "湖南": "湖南",
            "北京": "北京",
            "上海": "上海",
            "广东": "广东",
            "江苏": "江苏",
            "浙江": "浙江",
            "山东": "山东",
            "河南": "河南",
            "四川": "四川",
            "湖北": "湖北",
            "河北": "河北",
            "安徽": "安徽",
            "福建": "福建",
            "江西": "江西",
            "辽宁": "辽宁",
            "陕西": "陕西",
            "山西": "山西",
            "重庆": "重庆",
            "天津": "天津",
            "云南": "云南",
            "贵州": "贵州",
            "广西": "广西",
            "海南": "海南",
            "甘肃": "甘肃",
            "青海": "青海",
            "宁夏": "宁夏",
            "新疆": "新疆",
            "西藏": "西藏",
            "内蒙古": "内蒙古",
            "黑龙江": "黑龙江",
            "吉林": "吉林",
            "未知地区": "其他",
        }

        # 直接匹配
        if location_str in province_map:
            return province_map[location_str]

        # 按分隔符处理
        if "-" in location_str:
            province_part = location_str.split("-")[0]
            return province_map.get(province_part, province_part)

        # 查找包含的省份名称
        for full_name, province in province_map.items():
            if full_name in location_str:
                return province

        return location_str

    @classmethod
    def enhance_data(cls, df: pd.DataFrame) -> pd.DataFrame:
        """数据增强处理 - 添加计算字段

        Args:
            df: 原始数据DataFrame

        Returns:
            pd.DataFrame: 增强后的数据
        """
        df_enhanced = df.copy()

        # 新增字段：是否为海外院校
        df_enhanced["是否为海外院校"] = df_enhanced["最高学历毕业院校类别"].apply(
            lambda x: "是" if "海外院校" in str(x) else "否"
        )

        # 新增字段：最高学历毕业院校类别-分类1
        df_enhanced["最高学历毕业院校类别-分类1"] = df_enhanced.apply(
            cls.classify_institution, axis=1
        )

        # 新增字段：籍贯-省份
        df_enhanced["籍贯-省份"] = df_enhanced["籍贯"].apply(cls.extract_province)

        # 新增字段：出生年代
        df_enhanced["出生年代"] = df_enhanced["出生日期"].apply(
            cls.calculate_generation
        )

        return df_enhanced

    @classmethod
    def validate_excel_format(cls, df: pd.DataFrame) -> List[str]:
        """验证Excel文件格式

        Args:
            df: 待验证的DataFrame

        Returns:
            List[str]: 错误信息列表，空列表表示验证通过
        """
        errors = []

        # 检查必需字段
        missing_columns = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            errors.append(f"缺少必需字段: {', '.join(missing_columns)}")

        # 检查数据是否为空
        if df.empty:
            errors.append("Excel文件中没有数据")

        return errors

    @staticmethod
    def generate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
        """生成统计数据

        Args:
            df: 增强后的数据DataFrame

        Returns:
            Dict[str, Any]: 统计结果字典
        """
        stats = {}
        total_count = len(df)

        # 基础统计
        stats["total_count"] = total_count
        stats["bilateral_count"] = len(
            df[df["应聘状态"].str.contains("两方", na=False)]
        )
        stats["trilateral_count"] = len(
            df[df["应聘状态"].str.contains("三方", na=False)]
        )

        # 生成各维度统计
        dimensions = [
            ("political_status", "政治面貌"),
            ("gender", "性别"),
            ("age_distribution", "出生年代"),
            ("education", "最高学历"),
            ("institution_category", "最高学历毕业院校类别-分类1"),
            ("major_type", "专业类型"),
            ("province_distribution", "籍贯-省份"),
        ]

        for stat_key, column_name in dimensions:
            counts = df[column_name].value_counts().to_dict()
            stats[stat_key] = [
                {"name": k, "count": v, "percentage": round(v / total_count * 100, 1)}
                for k, v in counts.items()
                if k is not None
            ]

        # 特殊院校统计
        stats["special_institutions"] = DataProcessor._calculate_special_institutions(
            df
        )

        return stats

    @staticmethod
    def _calculate_special_institutions(df: pd.DataFrame) -> Dict[str, int]:
        """计算特殊院校统计数据

        Args:
            df: 数据DataFrame

        Returns:
            Dict[str, int]: 特殊院校统计结果
        """
        # 特定院校统计
        special_schools = {
            "清华大学": "清华大学",
            "北京大学": "北京大学",
            "同济大学": "同济大学",
            "中南大学": "中南大学",
            "北京交通大学": "北京交通大学",
            "西南交通大学": "西南交通大学",
            "兰州交通大学": "兰州交通大学",
            "大连交通大学": "大连交通大学",
            "华东交通大学": "华东交通大学",
        }

        result = {}
        for display_name, school_name in special_schools.items():
            result[display_name] = len(df[df["最高学历毕业院校"] == school_name])

        # C9联盟统计（排除清华北大）
        c9_total = len(df[df["最高学历毕业院校类别-分类1"] == "C9联盟"])
        tsinghua = result["清华大学"]
        peking = result["北京大学"]
        result["C9联盟"] = c9_total - tsinghua - peking

        return result

    def validate_data(self, df: pd.DataFrame) -> tuple[bool, str]:
        """验证数据格式和完整性

        Args:
            df: 待验证的DataFrame

        Returns:
            tuple[bool, str]: (是否有效, 验证消息)
        """
        if df.empty:
            return False, "数据为空，请检查Excel文件"

        # 检查必需列
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS if col not in df.columns
        ]
        if missing_columns:
            return False, f"缺少必需列: {', '.join(missing_columns)}"

        return True, "数据验证通过"



    def calculate_statistics(self, df: pd.DataFrame) -> dict:
        """计算统计信息

        Args:
            df: 增强后的数据DataFrame

        Returns:
            dict: 统计结果
        """
        total_count = len(df)

        # 基础统计
        stats = {
            "total_count": total_count,
            "bilateral_count": len(df[df["应聘状态"].str.contains("已签约", na=False)]),
            "trilateral_count": 0,  # 示例数据中没有三方协议
        }

        # 各维度统计
        dimensions = [
            ("political_status", "政治面貌"),
            ("gender", "性别"),
            ("age_distribution", "年龄段"),
            ("education", "最高学历"),
            ("institution_category", "院校分类"),
            ("major_type", "专业类型"),
            ("province_distribution", "籍贯省份"),
        ]

        for stat_key, column_name in dimensions:
            if column_name in df.columns:
                counts = df[column_name].value_counts()
                stats[stat_key] = [
                    {"name": str(name), "value": int(count)}
                    for name, count in counts.items()
                ]
            else:
                stats[stat_key] = []

        # 特殊院校统计
        if "最高学历毕业院校" in df.columns:
            school_counts = df["最高学历毕业院校"].value_counts()
            stats["special_institutions"] = [
                {"name": str(name), "value": int(count)}
                for name, count in school_counts.head(10).items()
            ]
        else:
            stats["special_institutions"] = []

        return stats

    def calculate_birth_decade(self, birth_date: str) -> str:
        """计算出生年代

        Args:
            birth_date: 出生日期字符串

        Returns:
            str: 年代标识
        """
        try:
            if pd.isna(birth_date) or birth_date == "":
                return "其他"

            birth_str = str(birth_date)
            if "-" in birth_str:
                year = int(birth_str.split("-")[0])
            elif "/" in birth_str:
                year = int(birth_str.split("/")[0])
            else:
                year = int(birth_str[:4])

            if year >= 2000:
                return "00后"
            elif year >= 1995:
                return "95后"
            elif year >= 1990:
                return "90后"
            else:
                return "其他"

        except (ValueError, IndexError):
            return "其他"

    def calculate_age_group(self, age) -> str:
        """计算年龄段

        Args:
            age: 年龄

        Returns:
            str: 年龄段标识
        """
        try:
            age_int = int(age)
            if age_int <= 24:
                return "00后"
            elif age_int <= 27:
                return "95后"
            elif age_int <= 32:
                return "90后"
            else:
                return "其他"
        except (ValueError, TypeError):
            return "其他"

    def is_party_member(self, political_status: str) -> bool:
        """判断是否为党员

        Args:
            political_status: 政治面貌

        Returns:
            bool: 是否为党员
        """
        if pd.isna(political_status):
            return False

        status_str = str(political_status)
        return "中共党员" in status_str or "中共预备党员" in status_str
