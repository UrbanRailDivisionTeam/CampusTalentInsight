#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器模块
负责生成各种格式的报告
"""

import os
import re
from datetime import datetime
from typing import Any, Dict


class ReportGenerator:
    """报告生成器类 - 生成各种格式的报告"""

    def __init__(self):
        """初始化报告生成器"""
        # 确保报告目录存在
        os.makedirs("reports", exist_ok=True)

    def process_chart_image(self, image_data: str) -> str:
        """
        处理图表图片数据

        Args:
            image_data: Base64编码的图片数据（前端已移除前缀）

        Returns:
            str: 处理后的图片数据URL
        """
        # 检查是否已有前缀，如果没有则添加
        if not image_data.startswith("data:image/png;base64,"):
            return f"data:image/png;base64,{image_data}"
        return image_data

    def generate_markdown_report(
        self, statistics: Dict[str, Any], chart_images: Dict[str, str]
    ) -> str:
        """生成Markdown格式的报告

        Args:
            statistics: 统计数据
            chart_images: 图表图片数据

        Returns:
            str: Markdown格式的报告内容
        """
        # 处理图表图片
        processed_images = {}
        for key, image_data in chart_images.items():
            processed_images[key] = self.process_chart_image(image_data)

        # 生成报告标题
        report = "# 2025届校园招聘情况说明\n\n"

        # 第一部分：招聘整体情况
        report += "## 一、2025届校园招聘整体情况\n\n"
        
        # 动态生成招聘人数描述
        total_count = statistics["total_count"]
        bilateral_count = statistics["bilateral_count"]
        trilateral_count = statistics["trilateral_count"]
        #current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_day = datetime.now().strftime('%Y-%m-%d')
        
        report += (
            '为深入贯彻人才工作会议精神，推进集团及公司"十四五"人力资源战略规划实施，'
            "持续提升公司能主动牵引业务，满足公司高质量度的人才储备需求，"
            "人力资源部根据公司生产经营和人力资源规划要求，制定2025年招聘计划，"
            "并根据计划在国内98所目标院校及海外专场招聘会中全力推进人才引进工作。"
            f"本届校园招聘，截止{current_day}公司累计签约{total_count}人，其中，"
            f"两方协议{bilateral_count}人，三方协议{trilateral_count}人。\n\n"
        )

        # 第二部分：引进人员情况
        report += "## 二、2025届校园招聘引进人员情况\n\n"

        # 1. 政治面貌分布
        report += "### 1. 政治面貌分布\n\n"
        political_data = statistics["political_status"]
        political_text = (
            f"2025届校园招聘引进人员中，共青团员{political_data[0]['count']}人，"
            f"占比{political_data[0]['percentage']}%；中国共产党员{political_data[1]['count']}人，"
            f"占比{political_data[1]['percentage']}%；群众{political_data[2]['count']}人，"
            f"占比{political_data[2]['percentage']}%。\n\n"
        )
        report += political_text
        if "political_status" in processed_images:
            report += f"![政治面貌分布图]({processed_images['political_status']})\n\n"

        # 2. 性别分布
        report += "### 2. 性别分布\n\n"
        gender_data = statistics["gender"]
        gender_text = (
            f"2025届校园招聘引进人员中，男{gender_data[0]['count']}人，"
            f"占比{gender_data[0]['percentage']}%；女{gender_data[1]['count']}人，"
            f"占比{gender_data[1]['percentage']}%。\n\n"
        )
        report += gender_text
        if "gender" in processed_images:
            report += f"![性别分布图]({processed_images['gender']})\n\n"

        # 3. 年龄分布
        report += "### 3. 年龄分布\n\n"
        age_data = statistics["age_distribution"]
        age_text = (
            f"2025届校园招聘引进人员中，00后{age_data[0]['count']}人，"
            f"占比{age_data[0]['percentage']}%；95后{age_data[1]['count']}人，"
            f"占比{age_data[1]['percentage']}%；90后{age_data[2]['count']}人，"
            f"占比{age_data[2]['percentage']}%。\n\n"
        )
        report += age_text
        if "age_distribution" in processed_images:
            report += f"![年龄分布图]({processed_images['age_distribution']})\n\n"

        # 4. 学历分布
        report += "### 4. 学历分布\n\n"
        education_data = statistics["education"]
        education_text = (
            f"2025届校园招聘引进人员中，硕士研究生{education_data[0]['count']}人，"
            f"占比{education_data[0]['percentage']}%；本科{education_data[1]['count']}人，"
            f"占比{education_data[1]['percentage']}%；博士研究生{education_data[2]['count']}人，"
            f"占比{education_data[2]['percentage']}%。\n\n"
        )
        report += education_text
        if "education" in processed_images:
            report += f"![学历分布图]({processed_images['education']})\n\n"

        # 5. 院校类别分布
        report += "### 5. 院校类别分布\n\n"
        institution_data = statistics["institution_category"]
        institution_text = (
            f"2025届校园招聘引进人员中，211高校{institution_data[0]['count']}人，"
            f"占比{institution_data[0]['percentage']}%；985高校{institution_data[1]['count']}人，"  # noqa: E501
            f"占比{institution_data[1]['percentage']}%；本分类院校{institution_data[2]['count']}人，"  # noqa: E501
            f"占比{institution_data[2]['percentage']}%。\n\n"
        )
        report += institution_text
        if "institution_category" in processed_images:
            report += (
                f"![院校类别分布图]({processed_images['institution_category']})\n\n"
            )
        
        # 重点院校统计
        if "special_institutions" in statistics:
            special_data = statistics["special_institutions"]
            report += "#### 重点院校统计\n\n"
            report += "引进重点院校人员情况如下："
            
            # 清华大学和北京大学
            if special_data.get("清华大学", 0) > 0:
                report += f"清华大学{special_data['清华大学']}人、"
            if special_data.get("北京大学", 0) > 0:
                report += f"北京大学{special_data['北京大学']}人、"
            
            # C9联盟
            if special_data.get("C9联盟", 0) > 0:
                report += f"C9联盟（除清华北大外）{special_data['C9联盟']}人、"
            
            # 其他重点院校
            other_schools = ["同济大学", "中南大学", "北京交通大学", "西南交通大学", "兰州交通大学", "大连交通大学", "华东交通大学"]
            for school in other_schools:
                if special_data.get(school, 0) > 0:
                    report += f"{school}{special_data[school]}人、"
            
            # 移除最后的顿号并添加句号
            if report.endswith("、"):
                report = report[:-1] + "。\n\n"
            else:
                report += "\n\n"

        # 6. 专业类型分布
        report += "### 6. 专业类型分布\n\n"
        major_data = statistics["major_type"]
        if len(major_data) >= 3:
            major_text = (
                f"2025届校园招聘引进人员中，{major_data[0]['name']}"
                f"{major_data[0]['count']}人，占比{major_data[0]['percentage']}%；"
                f"{major_data[1]['name']}{major_data[1]['count']}人，"
                f"占比{major_data[1]['percentage']}%；{major_data[2]['name']}"
                f"{major_data[2]['count']}人，占比{major_data[2]['percentage']}%。\n\n"
            )
        elif len(major_data) >= 2:
            major_text = (
                f"2025届校园招聘引进人员中，{major_data[0]['name']}"
                f"{major_data[0]['count']}人，占比{major_data[0]['percentage']}%；"
                f"{major_data[1]['name']}{major_data[1]['count']}人，"
                f"占比{major_data[1]['percentage']}%。\n\n"
            )
        elif len(major_data) >= 1:
            major_text = (
                f"2025届校园招聘引进人员中，{major_data[0]['name']}"
                f"{major_data[0]['count']}人，占比{major_data[0]['percentage']}%。\n\n"
            )
        else:
            major_text = "暂无专业类型数据。\n\n"
        report += major_text
        if "major_type" in processed_images:
            report += f"![专业类型分布图]({processed_images['major_type']})\n\n"

        # 7. 籍贯分布
        report += "### 7. 籍贯分布\n\n"
        province_data = statistics["province_distribution"]
        if len(province_data) >= 3:
            province_text = (
                f"2025届校园招聘引进人员中，{province_data[0]['name']}"
                f"{province_data[0]['count']}人，占比{province_data[0]['percentage']}%；"
                f"{province_data[1]['name']}{province_data[1]['count']}人，"
                f"占比{province_data[1]['percentage']}%；{province_data[2]['name']}"
                f"{province_data[2]['count']}人，占比{province_data[2]['percentage']}%。\n\n"
            )
        elif len(province_data) >= 2:
            province_text = (
                f"2025届校园招聘引进人员中，{province_data[0]['name']}"
                f"{province_data[0]['count']}人，占比{province_data[0]['percentage']}%；"
                f"{province_data[1]['name']}{province_data[1]['count']}人，"
                f"占比{province_data[1]['percentage']}%。\n\n"
            )
        elif len(province_data) >= 1:
            province_text = (
                f"2025届校园招聘引进人员中，{province_data[0]['name']}"
                f"{province_data[0]['count']}人，占比{province_data[0]['percentage']}%。\n\n"
            )
        else:
            province_text = "暂无籍贯分布数据。\n\n"
        report += province_text
        if "province_distribution" in processed_images:
            report += f"![籍贯分布图]({processed_images['province_distribution']})\n\n"

        # 添加报告生成时间
        report += "---\n"
        report += f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return report

    def generate_html_report(
        self, statistics: Dict[str, Any], chart_images: Dict[str, str]
    ) -> str:
        """生成HTML格式的报告

        Args:
            statistics: 统计数据
            chart_images: 图表图片数据

        Returns:
            str: HTML格式的报告内容
        """
        # 先生成Markdown报告
        markdown_content = self.generate_markdown_report(statistics, chart_images)

        # 转换为HTML
        from .pdf_converter import PDFConverter

        converter = PDFConverter()
        html_content = converter.markdown_to_html(markdown_content)

        # 添加HTML头部和样式
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025届校园招聘分析报告</title>
    <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&display=swap'
        );
        body {{
            font-family: 'Noto Serif SC', serif; /* 思源宋体 */
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f9f9f9;
            font-size: 14px; /* 缩小基础字体大小 */
        }}
        .container {{
            max-width: 210mm; /* A4宽度 */
            margin: 0 auto;
            background: white;
            padding: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 24px;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 600;
            color: #1a1a1a;
        }}
        h2 {{
            font-size: 18px;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            color: #0066cc;
        }}
        h3 {{
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        p {{
            margin-bottom: 16px;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #eee;
        }}
        hr {{
            border: none;
            border-top: 1px solid #eaecef;
            margin: 20px 0;
        }}
        .report-footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
        <div class="report-footer">
            <p>本报告由中车株机人力资源部校园招聘数据分析平台自动生成，数据内部使用，严禁转载外发</p>
        </div>
    </div>
</body>
</html>
"""

        return html
# <p>本报告由中车株机人力资源部校园招聘数据分析平台自动生成</p>

    def save_html_report(self, html_content: str) -> str:
        """保存HTML报告到文件

        Args:
            html_content: HTML报告内容

        Returns:
            str: 保存的文件路径
        """
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"校园招聘分析报告_{timestamp}.html"
        file_path = os.path.join("reports", filename)

        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path
