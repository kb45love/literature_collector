"""
本地 PDF 读取器：扫描并注册本地 PDF 文件
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LocalPDFReader:
    """扫描本地 PDF 目录"""
    
    def __init__(self, root_dir: str, recursive: bool = True):
        self.root_dir = Path(root_dir)
        self.recursive = recursive
    
    def scan_directory(self) -> List[Dict]:
        """
        扫描 PDF 目录
        
        Returns:
            PDF 文件列表 [{"filename": "...", "path": "...", "size": ...}]
        """
        if not self.root_dir.exists():
            logger.warning(f"目录不存在：{self.root_dir}")
            return []
        
        pdf_files = []
        
        pattern = "**/*.pdf" if self.recursive else "*.pdf"
        
        for pdf_path in self.root_dir.glob(pattern):
            try:
                size = pdf_path.stat().st_size
                
                pdf_files.append({
                    "filename": pdf_path.name,
                    "path": str(pdf_path),
                    "size": size,
                    "paper_id": f"local_{len(pdf_files):04d}"
                })
            
            except Exception as e:
                logger.warning(f"无法读取文件 {pdf_path}: {e}")
                continue
        
        logger.info(f"扫描完成：找到 {len(pdf_files)} 个 PDF 文件")
        return pdf_files
