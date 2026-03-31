"""
文献采集与图版提取系统
"""

__version__ = "1.0.0"
__author__ = "Literature Collector"

from .deduplicator import Deduplicator
from .downloader import LiteratureDownloader
from .local_reader import LocalPDFReader
from .pdf_processor import PDFProcessor
from .figure_extractor import FigureExtractor
from .metadata_manager import MetadataManager

__all__ = [
    'Deduplicator',
    'LiteratureDownloader',
    'LocalPDFReader',
    'PDFProcessor',
    'FigureExtractor',
    'MetadataManager',
]
