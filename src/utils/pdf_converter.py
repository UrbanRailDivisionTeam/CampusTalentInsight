# -*- coding: utf-8 -*-
"""
PDF转换器模块
负责将Markdown报告转换为PDF格式
"""

import os
import tempfile
from pathlib import Path
from typing import Optional


class PDFConverter:
    """PDF转换器类 - 将Markdown转换为PDF"""

    def __init__(self):
        """初始化PDF转换器"""
        pass

    def markdown_to_pdf_simple(self, markdown_content: str, output_path: str) -> bool:
        """简单的Markdown到PDF转换（使用HTML作为中间格式）

        Args:
            markdown_content: Markdown内容
            output_path: 输出PDF文件路径

        Returns:
            bool: 转换是否成功
        """
        try:
            # 这里提供一个简单的实现思路
            # 实际使用时可以集成更专业的PDF生成库

            # 将Markdown转换为HTML
            html_content = self._markdown_to_html(markdown_content)

            # 创建一个简单的HTML文件用于转换
            # html_template 变量已移除，直接使用内联HTML
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>校园招聘分析报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'SimSun', sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h1 {{
            font-size: 28px;
            text-align: center;
            margin-bottom: 30px;
        }}
        h2 {{
            font-size: 24px;
            margin-top: 30px;
        }}
        h3 {{
            font-size: 20px;
            margin-top: 25px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            background: #f9f9f9;
        }}
        .page-break {{
            page-break-before: always;
        }}
        @media print {{
            body {{
                margin: 20px;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
            """

            # 尝试使用WeasyPrint生成真正的PDF
            if self.create_pdf_with_weasyprint(markdown_content, output_path):
                print(f"✅ PDF报告已生成: {output_path}")
                return True
            else:
                # WeasyPrint失败时使用HTML替代方案
                print("⚠️ WeasyPrint不可用，使用HTML替代方案")
                return self.create_pdf_with_html_fallback(markdown_content, output_path)

        except Exception as e:
            print(f"PDF转换失败: {str(e)}")
            return False

    def markdown_to_html(self, markdown_content: str) -> str:
        """将Markdown内容转换为HTML（公有方法）

        Args:
            markdown_content: Markdown内容

        Returns:
            str: HTML内容
        """
        return self._markdown_to_html(markdown_content)

    def _markdown_to_html(self, markdown_content: str) -> str:
        """将Markdown内容转换为HTML（私有方法）

        Args:
            markdown_content: Markdown内容

        Returns:
            str: HTML内容
        """
        try:
            import markdown

            from .logger import get_logger

            logger = get_logger("pdf_converter")

            logger.info("🔄 开始将Markdown转换为HTML")

            # 不需要修复图片URL，因为在report_generator.py中已经处理了

            html = markdown.markdown(markdown_content, extensions=["tables"])
            logger.info("✅ Markdown转换为HTML成功")
            return html

        except ImportError:
            # 如果markdown库不可用，使用简单的替代方案
            print("⚠️ markdown库不可用，使用简单的替代方案")
            # 简单的Markdown到HTML转换
            html_content = markdown_content

            # 转换标题
            html_content = html_content.replace("### ", "<h3>").replace(
                "\n### ", "</h3>\n<h3>"
            )
            html_content = html_content.replace("## ", "<h2>").replace(
                "\n## ", "</h2>\n<h2>"
            )
            html_content = html_content.replace("# ", "<h1>").replace(
                "\n# ", "</h1>\n<h1>"
            )

            # 处理段落
            lines = html_content.split("\n")
            processed_lines = []
            in_paragraph = False

            for line in lines:
                line = line.strip()
                if not line:
                    if in_paragraph:
                        processed_lines.append("</p>")
                        in_paragraph = False
                    processed_lines.append("")
                elif line.startswith("<h") or line.startswith("!["):
                    if in_paragraph:
                        processed_lines.append("</p>")
                        in_paragraph = False
                    processed_lines.append(line)
                else:
                    if not in_paragraph:
                        processed_lines.append("<p>")
                        in_paragraph = True
                    processed_lines.append(line)

            if in_paragraph:
                processed_lines.append("</p>")

            html_content = "\n".join(processed_lines)

            # 处理图片
            import re

            img_pattern = r"!\[([^\]]*)\]\(data:image/png;base64,([^\)]+)\)"
            html_content = re.sub(
                img_pattern,
                r'<img src="data:image/png;base64,\2" alt="\1" />',
                html_content,
            )

            # 处理粗体和斜体
            html_content = re.sub(
                r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", html_content
            )
            html_content = re.sub(r"\*([^\*]+)\*", r"<em>\1</em>", html_content)

            # 处理分隔线
            html_content = html_content.replace("---", "<hr>")

            return html_content
        except Exception as e:
            print(f"❌ Markdown转换为HTML失败: {str(e)}")
            # 出错时返回原始内容
            return f"<pre>{markdown_content}</pre>"

    def create_pdf_with_weasyprint(
        self, markdown_content: str, output_path: str
    ) -> bool:
        """使用WeasyPrint创建PDF（Windows系统可能不兼容）

        Args:
            markdown_content: Markdown内容
            output_path: 输出PDF文件路径

        Returns:
            bool: 转换是否成功
        """
        try:
            # WeasyPrint在Windows系统上可能缺少依赖库
            from weasyprint import CSS, HTML

            # 将Markdown转换为HTML
            html_content = self._markdown_to_html(markdown_content)

            # 创建完整的HTML文档
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>校园招聘分析报告</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: 'Microsoft YaHei', 'SimSun', sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h1 {{
            font-size: 28px;
            text-align: center;
            margin-bottom: 30px;
        }}
        h2 {{
            font-size: 24px;
            margin-top: 30px;
        }}
        h3 {{
            font-size: 20px;
            margin-top: 25px;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
            """

            # 创建HTML对象并生成PDF
            html_doc = HTML(string=html_template)
            html_doc.write_pdf(output_path)

            return True

        except ImportError:
            print("WeasyPrint未安装或缺少系统依赖")
            return False
        except Exception as e:
            print(f"WeasyPrint PDF转换失败: {str(e)}")
            print("提示：WeasyPrint在Windows系统上可能需要额外的系统依赖")
            return False

    def create_pdf_with_html_fallback(
        self, markdown_content: str, output_path: str
    ) -> bool:
        """使用HTML文件作为PDF的替代方案（Windows兼容）

        Args:
            markdown_content: Markdown内容
            output_path: 输出PDF文件路径

        Returns:
            bool: 转换是否成功
        """
        try:
            # 将Markdown转换为HTML
            html_content = self._markdown_to_html(markdown_content)

            # 创建适合打印的HTML模板
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>校园招聘分析报告</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                margin: 0;
                font-size: 12pt;
            }}
            .no-print {{
                display: none;
            }}
        }}
        body {{
            font-family: 'Microsoft YaHei', 'SimSun', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h1 {{
            font-size: 28px;
            text-align: center;
            margin-bottom: 30px;
        }}
        h2 {{
            font-size: 24px;
            margin-top: 30px;
        }}
        h3 {{
            font-size: 20px;
            margin-top: 25px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            background: #f9f9f9;
        }}
        .print-instruction {{
            background: #e8f4fd;
            border: 1px solid #3498db;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }}
        .print-instruction h3 {{
            margin-top: 0;
            color: #2980b9;
            border: none;
        }}
        @media print {{
            .print-instruction {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="print-instruction no-print">
        <h3>📄 PDF生成说明</h3>
        <p>由于系统兼容性问题，已生成HTML格式的报告文件。</p>
        <p><strong>如需PDF格式：</strong>请在浏览器中打开此文件，按 <kbd>Ctrl+P</kbd> 选择"另存为PDF"</p>
    </div>

{html_content}
</body>
</html>
            """

            # 保存为HTML文件（使用.html扩展名）
            html_path = output_path.replace(".pdf", ".html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_template)

            print(f"📄 报告已生成为HTML格式: {html_path}")
            print("💡 提示：在浏览器中打开HTML文件，按Ctrl+P可转换为PDF")

            return True

        except Exception as e:
            print(f"HTML报告生成失败: {str(e)}")
            return False
