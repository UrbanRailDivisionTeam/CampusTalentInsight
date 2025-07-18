"""文件管理模块

这个模块负责处理文件上传、保存、历史记录管理等功能。
主要包含FileManager类用于管理上传的Excel文件。
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
from fastapi import UploadFile
from pydantic import BaseModel

from ..core.config import AppConfig


class UploadRecord(BaseModel):
    """上传记录数据模型
    
    用于记录每次文件上传的详细信息，包括文件名、描述、上传时间等。
    """
    filename: str  # 文件名
    description: str  # 文件描述
    upload_time: str  # 上传时间
    file_size: int  # 文件大小（字节）
    original_name: str  # 原始文件名


class FileManager:
    """文件管理器
    
    负责管理上传文件的保存、读取、历史记录等功能。
    这是一个工具类，帮助我们更好地组织文件操作。
    """
    
    def __init__(self):
        """初始化文件管理器
        
        设置上传目录和历史记录文件路径。
        """
        self.uploads_dir = AppConfig.UPLOADS_DIR
        self.history_file = self.uploads_dir / "upload_history.json"
        
        # 确保上传目录存在
        self.uploads_dir.mkdir(exist_ok=True, parents=True)
    
    async def save_uploaded_file(self, file: UploadFile, description: str) -> Tuple[str, pd.DataFrame]:
        """保存上传的文件并读取数据
        
        Args:
            file: FastAPI上传的文件对象
            description: 文件描述信息
            
        Returns:
            Tuple[str, pd.DataFrame]: 返回保存的文件名和读取的DataFrame数据
            
        Raises:
            Exception: 当文件保存或读取失败时抛出异常
        """
        # 生成唯一的文件名（加上时间戳避免重名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        filename = f"{timestamp}_{file.filename}"
        file_path = self.uploads_dir / filename
        
        try:
            # 保存文件到磁盘
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 读取Excel文件数据
            df = pd.read_excel(file_path)
            
            # 记录上传历史
            upload_record = UploadRecord(
                filename=filename,
                description=description,
                upload_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                file_size=file_path.stat().st_size,
                original_name=file.filename
            )
            self._add_to_history(upload_record)
            
            return filename, df
            
        except Exception as e:
            # 如果出错，删除已保存的文件
            if file_path.exists():
                file_path.unlink()
            raise Exception(f"文件保存失败: {str(e)}")
    
    def get_latest_file(self) -> Optional[Tuple[str, pd.DataFrame]]:
        """获取最新上传的文件
        
        Returns:
            Optional[Tuple[str, pd.DataFrame]]: 如果有文件则返回文件名和数据，否则返回None
        """
        history = self.get_upload_history()
        if not history:
            return None
        
        # 获取最新的记录
        latest_record = history[0]  # 历史记录按时间倒序排列
        file_path = self.uploads_dir / latest_record["filename"]
        
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_excel(file_path)
            return latest_record["filename"], df
        except Exception:
            return None
    
    def get_upload_history(self) -> List[dict]:
        """获取上传历史记录
        
        Returns:
            List[dict]: 上传历史记录列表，按时间倒序排列
        """
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            # 按上传时间倒序排列
            return sorted(history, key=lambda x: x["upload_time"], reverse=True)
        except Exception:
            return []
    
    def clear_upload_history(self) -> None:
        """清除所有上传历史记录
        
        删除历史记录文件和所有上传的文件。
        """
        # 删除历史记录文件
        if self.history_file.exists():
            self.history_file.unlink()
        
        # 删除所有上传的文件（保留.gitkeep文件）
        for file_path in self.uploads_dir.iterdir():
            if file_path.is_file() and file_path.name != ".gitkeep":
                file_path.unlink()
    
    def _add_to_history(self, record: UploadRecord) -> None:
        """添加记录到历史文件
        
        Args:
            record: 上传记录对象
        """
        history = self.get_upload_history()
        
        # 添加新记录
        history.append(record.dict())
        
        # 限制历史记录数量
        if len(history) > AppConfig.MAX_HISTORY_RECORDS:
            # 删除最旧的记录对应的文件
            oldest_records = history[AppConfig.MAX_HISTORY_RECORDS:]
            for old_record in oldest_records:
                old_file_path = self.uploads_dir / old_record["filename"]
                if old_file_path.exists():
                    old_file_path.unlink()
            
            # 保留最新的记录
            history = history[:AppConfig.MAX_HISTORY_RECORDS]
        
        # 保存到文件
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")