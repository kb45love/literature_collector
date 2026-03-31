"""
网络文献下载器：支持 Google Scholar、知网等
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional
import logging
import time
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class LiteratureDownloader:
    """从学术网站下载文献"""
    
    def __init__(
        self,
        output_dir: str = "./data/PDFs",
        max_retries: int = 3,
        timeout: int = 30,
        delay: float = 2.0,
        proxy: Optional[Dict] = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.timeout = timeout
        self.delay = delay
        self.proxy = proxy
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建带重试机制的 HTTP 会话"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if self.proxy:
            session.proxies.update(self.proxy)
        
        return session
    
    def search_google_scholar(
        self,
        keywords: List[str],
        max_results: int = 20
    ) -> List[Dict]:
        """
        搜索 Google Scholar
        
        Args:
            keywords: 搜索关键词列表
            max_results: 最大结果数
        
        Returns:
            论文列表 [{"title": "...", "authors": "...", "url": "...", ...}]
        """
        query = " ".join(keywords)
        search_url = "https://scholar.google.com/scholar"
        
        results = []
        try:
            time.sleep(self.delay)
            
            response = self.session.get(
                search_url,
                params={"q": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析搜索结果
            for item in soup.find_all('div', class_='gs_ri')[:max_results]:
                try:
                    title_elem = item.find('h3')
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                    
                    # 提取 URL
                    link = item.find('a')
                    url = link['href'] if link else None
                    
                    # 提取摘要
                    snippet = item.find('div', class_='gs_rs')
                    snippet_text = snippet.get_text(strip=True) if snippet else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet_text,
                        "source": "Google Scholar"
                    })
                
                except Exception as e:
                    logger.warning(f"解析搜索结果失败: {e}")
                    continue
            
            logger.info(f"Google Scholar 搜索完成，找到 {len(results)} 篇文献")
        
        except Exception as e:
            logger.error(f"Google Scholar 搜索失败: {e}")
        
        return results
    
    def search_cnki(
        self,
        keywords: List[str],
        max_results: int = 20
    ) -> List[Dict]:
        """
        搜索中国知网 (CNKI)
        
        Args:
            keywords: 搜索关键词列表
            max_results: 最大结果数
        
        Returns:
            论文列表
        """
        query = " ".join(keywords)
        search_url = "https://www.cnki.net/new/Search"
        
        results = []
        try:
            time.sleep(self.delay)
            
            response = self.session.post(
                search_url,
                data={"keyWord": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"CNKI 搜索完成，找到若干结果")
            
            # 注：实际实现需要根据 CNKI 页面结构调整
            # 这里为示例框架
        
        except Exception as e:
            logger.error(f"CNKI 搜索失败: {e}")
        
        return results
    
    def download_pdf(
        self,
        url: str,
        paper_id: str
    ) -> Optional[Path]:
        """
        下载 PDF 文件
        
        Args:
            url: 文件 URL
            paper_id: 论文 ID
        
        Returns:
            本地文件路径，失败返回 None
        """
        if not url:
            logger.warning(f"{paper_id}: 无有效 URL")
            return None
        
        file_path = self.output_dir / f"{paper_id}.pdf"
        
        try:
            time.sleep(self.delay)
            
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # 检查 Content-Type
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type:
                logger.warning(f"{paper_id}: 下载内容不是 PDF (type: {content_type})")
                return None
            
            # 写入文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"下载成功: {paper_id} -> {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"下载失败 {paper_id}: {e}")
            return None
    
    def batch_download(
        self,
        papers: List[Dict],
        paper_id_prefix: str = "web"
    ) -> List[Dict]:
        """
        批量下载多篇论文
        
        Args:
            papers: 论文信息列表
            paper_id_prefix: ID 前缀
        
        Returns:
            下载成功的论文列表（含本地路径）
        """
        downloaded = []
        
        for idx, paper in enumerate(papers, start=1):
            paper_id = f"{paper_id_prefix}_{idx:04d}"
            file_path = self.download_pdf(paper.get("url"), paper_id)
            
            if file_path:
                paper["paper_id"] = paper_id
                paper["local_path"] = str(file_path)
                downloaded.append(paper)
        
        logger.info(f"批量下载完成：{len(downloaded)}/{len(papers)} 成功")
        return downloaded
