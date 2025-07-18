#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块
定义所有的API接口路由
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..core.data_processor import DataProcessor
from ..utils.file_manager import FileManager, UploadRecord
from ..utils.report_generator import ReportGenerator


class StatisticsResponse(BaseModel):
    """统计结果响应模型"""

    upload_time: str
    description: str
    total_count: int
    bilateral_count: int
    trilateral_count: int
    political_status: list[Dict[str, Any]]
    gender: list[Dict[str, Any]]
    age_distribution: list[Dict[str, Any]]
    education: list[Dict[str, Any]]
    institution_category: list[Dict[str, Any]]
    major_type: list[Dict[str, Any]]
    province_distribution: list[Dict[str, Any]]
    special_institutions: Dict[str, int]


class DataManager:
    """数据管理器 - 管理当前加载的数据状态"""

    def __init__(self):
        self.current_data: Optional[pd.DataFrame] = None
        self.current_description: str = ""
        self.current_upload_time: str = ""

    def update_data(
        self, data: pd.DataFrame, description: str, upload_time: str
    ) -> None:
        """更新当前数据

        Args:
            data: 数据DataFrame
            description: 描述信息
            upload_time: 上传时间
        """
        self.current_data = data
        self.current_description = description
        self.current_upload_time = upload_time

    def has_data(self) -> bool:
        """检查是否有数据

        Returns:
            bool: 是否有数据
        """
        return self.current_data is not None

    def get_statistics(self) -> StatisticsResponse:
        """获取统计数据

        Returns:
            StatisticsResponse: 统计结果

        Raises:
            HTTPException: 无数据时抛出
        """
        if not self.has_data():
            raise HTTPException(status_code=404, detail="请先上传数据文件")

        try:
            stats = DataProcessor.generate_statistics(self.current_data)

            return StatisticsResponse(
                upload_time=self.current_upload_time,
                description=self.current_description,
                total_count=stats["total_count"],
                bilateral_count=stats["bilateral_count"],
                trilateral_count=stats["trilateral_count"],
                political_status=stats["political_status"],
                gender=stats["gender"],
                age_distribution=stats["age_distribution"],
                education=stats["education"],
                institution_category=stats["institution_category"],
                major_type=stats["major_type"],
                province_distribution=stats["province_distribution"],
                special_institutions=stats["special_institutions"],
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"统计数据生成失败: {str(e)}")


# 全局数据管理器实例
_global_data_manager = DataManager()


def get_data_manager() -> DataManager:
    """获取全局数据管理器实例

    Returns:
        DataManager: 全局数据管理器实例
    """
    return _global_data_manager


def create_api_router() -> APIRouter:
    """创建API路由器

    Returns:
        APIRouter: 配置好的路由器
    """
    router = APIRouter(prefix="/api")

    # 初始化管理器
    file_manager = FileManager()
    data_manager = get_data_manager()

    @router.post("/upload")
    async def upload_file(
        file: UploadFile = File(...), description: str = Form(..., max_length=500)
    ):
        """文件上传接口

        Args:
            file: 上传的Excel文件
            description: 文件描述信息

        Returns:
            dict: 上传结果
        """
        # 保存文件并读取数据
        filename, df = await file_manager.save_uploaded_file(file, description)

        # 验证文件格式
        errors = DataProcessor.validate_excel_format(df)
        if errors:
            # 删除无效文件
            file_path = file_manager.uploads_dir / filename
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail="\n".join(errors))

        # 数据增强处理
        df_enhanced = DataProcessor.enhance_data(df)

        # 更新数据管理器
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_manager.update_data(df_enhanced, description, upload_time)

        return {
            "message": "文件上传成功",
            "filename": filename,
            "record_count": len(df_enhanced),
            "upload_time": upload_time,
        }

    @router.get("/statistics", response_model=StatisticsResponse)
    async def get_statistics():
        """获取统计数据接口

        Returns:
            StatisticsResponse: 统计结果
        """
        return data_manager.get_statistics()

    @router.get("/upload-history")
    async def get_upload_history():
        """获取上传历史记录

        Returns:
            dict: 历史记录
        """
        history = file_manager.get_upload_history()
        return {"history": history}

    @router.delete("/clear-history")
    async def clear_upload_history():
        """清除所有上传历史记录

        Returns:
            dict: 操作结果
        """
        file_manager.clear_upload_history()
        return {"message": "历史记录已清除"}

    # 添加启动时自动加载最新文件的功能
    def auto_load_latest_file():
        """自动加载最新上传的Excel文件"""
        try:
            result = file_manager.get_latest_file()
            if result is None:
                print("未找到已上传的Excel文件")
                return

            latest_file, df = result

            # 数据增强处理
            df_enhanced = DataProcessor.enhance_data(df)

            # 更新数据管理器
            timestamp = latest_file.stem.split("_")[0]
            upload_time = datetime.fromtimestamp(int(timestamp)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            data_manager.update_data(df_enhanced, "自动加载的历史数据", upload_time)

            print(f"已自动加载最新Excel文件: {latest_file.name}")

        except Exception as e:
            print(f"自动加载Excel文件失败: {str(e)}")

    # 初始化报告生成器
    report_generator = ReportGenerator()

    @router.post("/generate-report")
    async def generate_report(request: Request):
        """生成Markdown报告"""
        from ..utils.logger import get_logger

        logger = get_logger("report_generator")

        try:
            logger.info("📝 开始生成Markdown报告")

            # 检查是否有数据
            if not data_manager.has_data():
                logger.warning("⚠️ 没有可用的数据")
                raise HTTPException(status_code=400, detail="没有可用的数据")

            # 获取请求数据
            body = await request.json()
            chart_images = body.get("chart_images", {})
            logger.info(f"📊 接收到图表数据: {len(chart_images)}个图表")

            # 获取统计数据
            statistics = data_manager.get_statistics()
            logger.info(f"📈 获取统计数据成功，总记录数: {statistics.total_count}")

            # 生成Markdown内容
            markdown_content = report_generator.generate_markdown_report(
                statistics, chart_images
            )
            logger.info(f"✅ Markdown内容生成成功，长度: {len(markdown_content)}字符")

            # 保存报告文件
            file_path = report_generator.save_markdown_report(markdown_content)
            logger.info(f"💾 Markdown报告保存成功: {file_path}")

            return {
                "success": True,
                "message": "Markdown报告生成成功",
                "file_path": file_path,
                "filename": os.path.basename(file_path),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Markdown报告生成失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Markdown报告生成失败: {str(e)}"
            )

    @router.post("/generate-html-report")
    async def generate_html_report(request: Request):
        """生成HTML报告"""
        from ..utils.logger import get_logger

        logger = get_logger("report_generator")

        try:
            logger.info("🌐 开始生成HTML报告")

            # 检查是否有数据
            if not data_manager.has_data():
                logger.warning("⚠️ 没有可用的数据")
                raise HTTPException(status_code=400, detail="没有可用的数据")

            # 获取请求数据
            body = await request.json()
            chart_images = body.get("chart_images", {})
            logger.info(f"📊 接收到图表数据: {len(chart_images)}个图表")

            # 获取统计数据
            statistics_obj = data_manager.get_statistics()
            logger.info(f"📈 获取统计数据成功，总记录数: {statistics_obj.total_count}")

            # 将StatisticsResponse对象转换为字典
            statistics = {
                "upload_time": statistics_obj.upload_time,
                "description": statistics_obj.description,
                "total_count": statistics_obj.total_count,
                "bilateral_count": statistics_obj.bilateral_count,
                "trilateral_count": statistics_obj.trilateral_count,
                "political_status": statistics_obj.political_status,
                "gender": statistics_obj.gender,
                "age_distribution": statistics_obj.age_distribution,
                "education": statistics_obj.education,
                "institution_category": statistics_obj.institution_category,
                "major_type": statistics_obj.major_type,
                "province_distribution": statistics_obj.province_distribution,
                "special_institutions": statistics_obj.special_institutions,
            }

            # 生成HTML内容
            html_content = report_generator.generate_html_report(
                statistics, chart_images
            )
            logger.info(f"✅ HTML内容生成成功，长度: {len(html_content)}字符")

            # 保存报告文件
            file_path = report_generator.save_html_report(html_content)
            logger.info(f"💾 HTML报告保存成功: {file_path}")

            return {
                "success": True,
                "message": "HTML报告生成成功",
                "file_path": file_path,
                "filename": os.path.basename(file_path),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ HTML报告生成失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"HTML报告生成失败: {str(e)}")

    @router.post("/generate-pdf-report")
    async def generate_pdf_report(request: Request):
        """生成PDF报告"""
        from ..utils.logger import get_logger

        logger = get_logger("report_generator")

        try:
            logger.info("📄 开始生成PDF报告")

            # 检查是否有数据
            if not data_manager.has_data():
                logger.warning("⚠️ 没有可用的数据")
                raise HTTPException(status_code=400, detail="没有可用的数据")

            # 获取请求数据
            body = await request.json()
            chart_images = body.get("chart_images", {})
            logger.info(f"📊 接收到图表数据: {len(chart_images)}个图表")

            # 获取统计数据
            statistics = data_manager.get_statistics()
            logger.info(f"📈 获取统计数据成功，总记录数: {statistics.total_count}")

            # 生成PDF报告
            file_path = report_generator.generate_pdf_report(statistics, chart_images)
            logger.info(f"💾 PDF报告生成成功: {file_path}")

            return {
                "success": True,
                "message": "PDF报告生成成功",
                "file_path": file_path,
                "filename": os.path.basename(file_path),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ PDF报告生成失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"PDF报告生成失败: {str(e)}")

    @router.get("/download-report/{filename}")
    async def download_report(filename: str):
        """下载报告文件

        Args:
            filename: 文件名

        Returns:
            FileResponse: 文件下载响应
        """
        try:
            file_path = os.path.join("reports", filename)

            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="报告文件不存在")

            return FileResponse(
                path=file_path, filename=filename, media_type="text/markdown"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")

    # 将自动加载函数绑定到路由器
    router.auto_load_latest_file = auto_load_latest_file

    return router


def create_main_router() -> APIRouter:
    """创建主路由器

    Returns:
        APIRouter: 主路由器
    """
    router = APIRouter()

    @router.get("/")
    async def root():
        """根路径，返回前端页面"""
        return FileResponse("static/index.html")
    
    @router.post("/auth/login")
    async def login(request: Request):
        """登录接口
        
        这个接口由AuthMiddleware处理，这里只是占位
        实际的登录逻辑在中间件中实现
        """
        # 这个路由实际上不会被执行，因为AuthMiddleware会拦截处理
        pass
    
    @router.post("/auth/logout")
    async def logout():
        """登出接口
        
        清除认证cookie，让用户退出登录状态
        
        Returns:
            dict: 登出结果
        """
        from fastapi.responses import JSONResponse
        
        response = JSONResponse(
            content={"success": True, "message": "已成功退出登录"}
        )
        # 清除认证cookie
        response.delete_cookie(key="auth_token")
        
        return response

    return router
