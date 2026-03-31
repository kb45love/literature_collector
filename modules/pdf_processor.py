"""
PDF 处理：提取文本、元数据、图片
"""

import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)


class PDFProcessor:
    """处理 PDF 文件"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc = None
        self.text = None
        self.metadata = None
    
    def open(self) -> bool:
        """打开 PDF 文件"""
        try:
            self.doc = fitz.open(self.pdf_path)
            logger.info(f"已打开 PDF：{self.pdf_path}")
            return True
        except Exception as e:
            logger.error(f"无法打开 PDF {self.pdf_path}: {e}")
            return False
    
    def extract_metadata(self) -> Dict:
        """提取 PDF 元数据"""
        if not self.doc:
            return {}
        
        try:
            metadata = self.doc.metadata
            
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": str(metadata.get("creationDate", "")),
                "modification_date": str(metadata.get("modDate", "")),
                "pages": len(self.doc)
            }
        
        except Exception as e:
            logger.warning(f"提取元数据失败：{e}")
            return {}
    
    def extract_text(self) -> str:
        """提取全文"""
        if not self.doc:
            return ""
        
        try:
            text = ""
            for page_num, page in enumerate(self.doc, start=1):
                text += f"\n--- 第 {page_num} 页 ---\n"
                text += page.get_text()
            
            return text
        
        except Exception as e:
            logger.error(f"提取文本失败：{e}")
            return ""
    
    def extract_images(self, output_dir: str = None, min_size: Tuple[int, int] = (100, 100)) -> List[Dict]:
        """
        提取 PDF 中的图片
        
        Args:
            output_dir: 图片输出目录
            min_size: 最小图片尺寸
        
        Returns:
            图片信息列表
        """
        if not self.doc:
            return []
        
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        images = []
        image_count = 0
        
        try:
            for page_num, page in enumerate(self.doc, start=1):
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list, start=1):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(self.doc, xref)
                        
                        if pix.width < min_size[0] or pix.height < min_size[1]:
                            continue
                        
                        image_count += 1
                        filename = f"page_{page_num}_img_{img_index}.png"
                        
                        if output_dir:
                            filepath = Path(output_dir) / filename
                            pix.save(str(filepath))
                        else:
                            filepath = None
                        
                        images.append({
                            "page": page_num,
                            "index": image_count,
                            "width": pix.width,
                            "height": pix.height,
                            "filename": filename,
                            "path": str(filepath) if filepath else None
                        })
                    
                    except Exception as e:
                        logger.warning(f"提取页 {page_num} 的图片失败：{e}")
                        continue
        
        except Exception as e:
            logger.error(f"提取图片失败：{e}")
        
        logger.info(f"提取图片完成：共 {image_count} 张")
        return images
    
    def close(self):
        """关闭 PDF"""
        if self.doc:
            self.doc.close()
            logger.debug("已关闭 PDF")
