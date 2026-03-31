"""
网络文献采集与处理程序
仅从网络下载文献，无本地扫描功能
"""

import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys

# 导入各模块
from modules import (
    Deduplicator, 
    LiteratureDownloader,
    PDFProcessor, 
    FigureExtractor, 
    MetadataManager
)

# ========================
# 日志初始化
# ========================

def setup_logging(config: Dict):
    """设置日志系统"""
    log_dir = Path(config['output']['base_dir']) / config['output']['structure']['logs_dir']
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "web_collector.log"
    
    logging.basicConfig(
        level=getattr(logging, config['logging']['level']),
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout) if config['logging']['console_output'] else logging.NullHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("网络文献采集与处理系统启动")
    logger.info("=" * 60)
    
    return logger


# ========================
# 核心采集逻辑
# ========================

def load_config(config_file: str = "config_web.yaml") -> Dict:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✓ 配置文件已加载：{config_file}")
        return config
    except FileNotFoundError:
        print(f"✗ 配置文件不存在：{config_file}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 加载配置文件失败：{e}")
        sys.exit(1)


def collect_from_web(
    downloader: LiteratureDownloader,
    config: Dict,
    deduplicator: Deduplicator,
    logger
) -> List[Dict]:
    """从网络采集文献"""
    logger.info("=" * 60)
    logger.info("开始网络采集...")
    logger.info("=" * 60)
    
    keywords = config['collection']['keywords']
    max_count = config['collection']['max_from_web']
    
    all_papers = []
    
    # Google Scholar 搜索
    if config['sources']['web']['engines']['google_scholar']['enabled']:
        logger.info(f"正在搜索 Google Scholar，关键词：{keywords}")
        try:
            google_results = downloader.search_google_scholar(keywords, max_results=max_count)
            all_papers.extend(google_results)
        except Exception as e:
            logger.error(f"Google Scholar 搜索异常：{e}")
    
    # CNKI 搜索
    if config['sources']['web']['engines']['cnki']['enabled']:
        logger.info(f"正在搜索 CNKI，关键词：{keywords}")
        try:
            cnki_results = downloader.search_cnki(keywords, max_results=max_count)
            all_papers.extend(cnki_results)
        except Exception as e:
            logger.error(f"CNKI 搜索异常：{e}")
    
    # 去重
    unique_papers = []
    for paper in all_papers:
        is_dup, dup_id = deduplicator.is_duplicate_by_metadata(
            title=paper.get('title'),
            url=paper.get('url'),
            threshold=config['deduplication']['similarity_threshold']
        )
        if not is_dup:
            unique_papers.append(paper)
        else:
            logger.info(f"跳过重复文献：{paper.get('title', 'Unknown')}")
    
    logger.info(f"网络采集完成：搜索到 {len(all_papers)} 篇，去重后 {len(unique_papers)} 篇")
    
    # 批量下载
    if unique_papers:
        downloaded = downloader.batch_download(unique_papers, paper_id_prefix="web")
        logger.info(f"下载完成：{len(downloaded)} 篇成功")
        return downloaded
    
    return []


def process_pdfs(
    pdf_list: List[Dict],
    config: Dict,
    deduplicator: Deduplicator,
    metadata_manager: MetadataManager,
    logger
) -> tuple:
    """处理 PDF 并提取信息"""
    logger.info("=" * 60)
    logger.info(f"开始处理 {len(pdf_list)} 个 PDF...")
    logger.info("=" * 60)
    
    figures_dir = Path(config['output']['base_dir']) / config['output']['structure']['figures_dir']
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    total_figures = 0
    errors = []
    
    for idx, pdf_info in enumerate(pdf_list, start=1):
        pdf_path = pdf_info.get('local_path') or pdf_info.get('path')
        paper_id = pdf_info.get('paper_id', f"web_{idx:04d}")
        
        logger.info(f"[{idx}/{len(pdf_list)}] 处理：{Path(pdf_path).name}")
        
        try:
            # 打开 PDF
            processor = PDFProcessor(pdf_path)
            if not processor.open():
                raise Exception("无法打开 PDF")
            
            # 提取元数据
            metadata = processor.extract_metadata()
            
            # 提取文本
            text = processor.extract_text()
            
            # 获取 PDF 文件名（不含扩展名）用作图片前缀
            pdf_filename_no_ext = Path(pdf_path).stem
            
            # 提取图片
            figures = processor.extract_images(
                output_dir=str(figures_dir),
                min_size=(
                    config['pdf_processing']['image_settings']['min_width'],
                    config['pdf_processing']['image_settings']['min_height']
                ),
                filename_prefix=pdf_filename_no_ext
            )
            
            # 识别图注
            extractor = FigureExtractor(language=config['figure_recognition']['language'])
            figure_info = extractor.extract_figures_from_text(text)
            captions = extractor.extract_captions_from_text(
                text, 
                [f['figure_id'] for f in figure_info]
            )
            
            # 关闭 PDF
            processor.close()
            
            # 生成元数据记录
            for figure in figures:
                figure_id_str = captions.get(str(figure['index']), f"Figure {figure['index']}")
                
                record = {
                    'paper_id': paper_id,
                    'filename': Path(pdf_path).name,
                    'title': metadata.get('title', ''),
                    'author': metadata.get('author', ''),
                    'year': '',
                    'url': pdf_info.get('url', ''),
                    'md5_hash': deduplicator.calculate_md5(pdf_path),
                    'page_num': figure['page'],
                    'figure_id': str(figure['index']),
                    'figure_caption': figure_id_str,
                    'figure_path': figure['path'],
                    'species': '',
                    'status': '✓ 成功'
                }
                
                metadata_manager.add_record(record)
                total_figures += 1
            
            # 注册到去重数据库
            deduplicator.register_paper(
                paper_id=paper_id,
                file_path=pdf_path,
                metadata={
                    'title': metadata.get('title', ''),
                    'authors': [metadata.get('author', '')],
                    'url': pdf_info.get('url', '')
                }
            )
            
            success_count += 1
            logger.info(f"✓ {paper_id} 处理成功，提取图版 {len(figures)} 张")
        
        except Exception as e:
            failed_count += 1
            logger.error(f"✗ {paper_id} 处理失败：{e}")
            
            errors.append({
                'paper_id': paper_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    logger.info("=" * 60)
    logger.info(f"PDF 处理完成：成功 {success_count}，失败 {failed_count}，提取图版 {total_figures} 张")
    logger.info("=" * 60)
    
    return success_count, failed_count, total_figures, errors


def main():
    """主函数 - 网络模式"""
    parser = argparse.ArgumentParser(description='网络文献采集与处理系统')
    parser.add_argument('--config', default='config_web.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    logger = setup_logging(config)
    
    try:
        # 初始化各模块
        deduplicator = Deduplicator(
            db_file=f"{config['output']['base_dir']}/cache/collection_db.json"
        )
        downloader = LiteratureDownloader(
            output_dir=f"{config['output']['base_dir']}/downloaded_PDFs",
            delay=config['sources']['web']['engines']['google_scholar']['delay'],
            proxy=config['proxy'] if config['proxy']['enabled'] else None
        )
        metadata_manager = MetadataManager(output_dir=config['output']['base_dir'])
        
        # 网络采集
        web_papers = collect_from_web(downloader, config, deduplicator, logger)
        
        if not web_papers:
            logger.warning("没有采集到任何文献")
            print("⚠️  没有采集到任何文献")
            return
        
        # 处理 PDF
        success, failed, figures, errors = process_pdfs(
            web_papers, config, deduplicator, metadata_manager, logger
        )
        
        # 保存输出
        metadata_manager.save_to_excel(filename=config['output']['structure']['metadata_file'])
        metadata_manager.save_to_csv(filename="metadata.csv")
        if errors:
            metadata_manager.save_error_log(errors)
        
        stats = {
            'from_web': len(web_papers),
            'from_local': 0,
            'total_unique': len(web_papers),
            'success': success,
            'failed': failed,
            'total_figures': figures
        }
        metadata_manager.save_processing_report(stats)
        
        # 最终报告
        logger.info("=" * 60)
        logger.info("网络采集系统已完成")
        logger.info(f"  ✓ 网络采集：{stats['from_web']} 篇")
        logger.info(f"  ✓ 处理成功：{stats['success']} 篇")
        logger.info(f"  ✓ 处理失败：{stats['failed']} 篇")
        logger.info(f"  ✓ 提取图版：{stats['total_figures']} 张")
        logger.info("=" * 60)
        
        print("\n✅ 网络采集完成！")
        print(f"📊 统计信息：")
        print(f"   网络采集：{stats['from_web']} 篇")
        print(f"   处理成功：{stats['success']} 篇")
        print(f"   处理失败：{stats['failed']} 篇")
        print(f"   提取图版：{stats['total_figures']} 张")
        
    except Exception as e:
        logger.error(f"系统出错：{e}", exc_info=True)
        print(f"\n❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
