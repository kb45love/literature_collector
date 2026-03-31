"""
图版识别：识别图注模式，匹配图片与图注
"""

import re
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class FigureExtractor:
    """识别和提取图版信息"""
    
    # 默认图注识别模式
    DEFAULT_PATTERNS = {
        "zh": [
            r"图\s*(\d+)",              # 图 1
            r"图\s*(\d+)\s*[-·]\s*(\d+)",  # 图 1-2 或 图 1·2
            r"插图\s*(\d+)",            # 插图 1
        ],
        "en": [
            r"Figure\s+(\d+)",          # Figure 1
            r"Fig\.\s*(\d+)",           # Fig. 1
            r"Fig\s+(\d+)",             # Fig 1
        ]
    }
    
    def __init__(self, language: str = "mixed"):
        """
        Args:
            language: 识别语言 ('zh' | 'en' | 'mixed')
        """
        self.language = language
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[Tuple[str, re.Pattern]]:
        """编译正则表达式"""
        patterns = []
        
        if self.language in ("zh", "mixed"):
            for pattern in self.DEFAULT_PATTERNS["zh"]:
                patterns.append(("zh", re.compile(pattern, re.IGNORECASE)))
        
        if self.language in ("en", "mixed"):
            for pattern in self.DEFAULT_PATTERNS["en"]:
                patterns.append(("en", re.compile(pattern, re.IGNORECASE)))
        
        return patterns
    
    def extract_figures_from_text(self, text: str) -> List[Dict]:
        """
        从文本中识别图版号
        
        Args:
            text: PDF 提取的全文
        
        Returns:
            图版列表 [{"figure_id": "1", "language": "zh", "positions": [...]}]
        """
        figures = {}
        
        for lang, pattern in self.patterns:
            for match in pattern.finditer(text):
                figure_id = match.group(1)
                full_match = match.group(0)
                
                if figure_id not in figures:
                    figures[figure_id] = {
                        "figure_id": figure_id,
                        "language": lang,
                        "raw_text": full_match,
                        "positions": []
                    }
                
                figures[figure_id]["positions"].append({
                    "start": match.start(),
                    "end": match.end(),
                    "matched_text": full_match
                })
        
        result = list(figures.values())
        logger.info(f"识别出 {len(result)} 个图版")
        return result
    
    def extract_captions_from_text(
        self,
        text: str,
        figure_ids: List[str],
        context_length: int = 500
    ) -> Dict[str, str]:
        """
        从文本中提取图注
        
        Args:
            text: 全文
            figure_ids: 图版号列表
            context_length: 提取上下文长度
        
        Returns:
            {figure_id: caption_text}
        """
        captions = {}
        
        for lang, pattern in self.patterns:
            for match in pattern.finditer(text):
                figure_id = match.group(1)
                
                if figure_id not in captions:
                    # 提取匹配点周围的文本作为图注
                    start = max(0, match.start() - context_length)
                    end = min(len(text), match.end() + context_length)
                    
                    caption = text[start:end].strip()
                    captions[figure_id] = caption
        
        logger.info(f"提取 {len(captions)} 个图注")
        return captions
    
    def get_figure_index(self, figure_id: str) -> int:
        """获取图版序号（用于排序）"""
        try:
            return int(figure_id.split('.')[0])
        except:
            return 999
    
    def sort_figures(self, figures: List[Dict]) -> List[Dict]:
        """按图版号排序"""
        return sorted(figures, key=lambda x: self.get_figure_index(x["figure_id"]))
