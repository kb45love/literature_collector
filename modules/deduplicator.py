"""
去重模块：识别已收集的文献，避免重复下载和处理
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from difflib import SequenceMatcher
from datetime import datetime

logger = logging.getLogger(__name__)


class Deduplicator:
    """管理已收集文献的去重检查"""
    
    def __init__(self, db_file: str = "./output/cache/collection_db.json"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.collection_db = self._load_db()
    
    def _load_db(self) -> Dict:
        """加载已收集文献数据库"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载数据库失败，创建新数据库：{e}")
                return {"files": {}, "metadata": {}}
        return {"files": {}, "metadata": {}}
    
    def _save_db(self):
        """保存数据库"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.collection_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存数据库失败：{e}")
    
    def calculate_md5(self, file_path: str) -> str:
        """计算文件 MD5 哈希"""
        md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            logger.error(f"计算 MD5 失败 {file_path}：{e}")
            return ""
    
    def is_duplicate_by_md5(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        通过 MD5 哈希检查重复
        
        Returns:
            (is_duplicate, existing_paper_id)
        """
        md5_hash = self.calculate_md5(file_path)
        
        if not md5_hash:
            return False, None
        
        for paper_id, info in self.collection_db["files"].items():
            if info.get("md5_hash") == md5_hash:
                logger.warning(f"重复文件（MD5）：{file_path} 已存在为 {paper_id}")
                return True, paper_id
        
        return False, None
    
    def is_duplicate_by_metadata(
        self, 
        title: Optional[str] = None,
        authors: Optional[List[str]] = None,
        url: Optional[str] = None,
        threshold: float = 0.85
    ) -> Tuple[bool, Optional[str]]:
        """
        通过元数据（标题、作者、URL）检查重复
        
        Returns:
            (is_duplicate, existing_paper_id)
        """
        existing_papers = self.collection_db.get("metadata", {})
        
        # 检查 URL
        if url:
            for paper_id, meta in existing_papers.items():
                if meta.get("url") == url:
                    logger.warning(f"重复 URL：{url} 已存在为 {paper_id}")
                    return True, paper_id
        
        # 检查标题相似度
        if title:
            for paper_id, meta in existing_papers.items():
                existing_title = meta.get("title", "")
                similarity = self._calculate_similarity(title, existing_title)
                if similarity > threshold:
                    logger.warning(f"相似标题检测：'{title}' ≈ '{existing_title}' (相似度: {similarity:.2f})")
                    return True, paper_id
        
        return False, None
    
    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """计算两个字符串的相似度"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def register_paper(
        self,
        paper_id: str,
        file_path: str,
        metadata: Dict
    ):
        """注册已处理的文献"""
        md5_hash = self.calculate_md5(file_path)
        
        self.collection_db["files"][paper_id] = {
            "file_path": str(file_path),
            "md5_hash": md5_hash,
            "timestamp": datetime.now().isoformat()
        }
        
        self.collection_db["metadata"][paper_id] = metadata
        self._save_db()
        logger.info(f"已注册文献：{paper_id}")
    
    def get_registered_count(self) -> int:
        """获取已注册的文献总数"""
        return len(self.collection_db["files"])
    
    def is_collection_complete(self, target_count: int) -> bool:
        """检查是否达到采集目标"""
        current_count = self.get_registered_count()
        return current_count >= target_count
