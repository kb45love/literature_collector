"""
本地PDF扫描与处理程序
仅处理本地已有的PDF文件，无网络功能
"""

import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys
import shutil

# 导入各模块
from modules import (
    Deduplicator, 
    LocalPDFReader,
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
    
    log_file = log_dir / "local_collector.log"
    
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
    logger.info("本地PDF扫描与处理系统启动")
    logger.info("=" * 60)
    
    return logger


# ========================
# 核心采集逻辑
# ========================

def load_config(config_file: str = "config_local.yaml") -> Dict:
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


def collect_from_local(
    local_reader: LocalPDFReader,
    config: Dict,
    deduplicator: Deduplicator,
    logger
) -> List[Dict]:
    """从本地扫描文献"""
    logger.info("=" * 60)
    logger.info("开始本地扫描...")
    logger.info("=" * 60)
    
    max_count = config['collection']['max_from_local']
    
    pdf_files = local_reader.scan_directory()
    
    # 限制数量
    if max_count > 0:
        pdf_files = pdf_files[:max_count]
        logger.info(f"已应用数量限制，仅处理前 {max_count} 个文件")
    
    # 去重
    unique_files = []
    for pdf in pdf_files:
        is_dup, dup_id = deduplicator.is_duplicate_by_md5(pdf['path'])
        if not is_dup:
            unique_files.append(pdf)
        else:
            logger.info(f"跳过重复文件（MD5）：{pdf['filename']}")
    
    logger.info(f"本地扫描完成：找到 {len(pdf_files)} 个 PDF，去重后 {len(unique_files)} 个")
    
    return unique_files


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
    
    downloaded_pdfs_dir = Path(config['output']['base_dir']) / 'downloaded_PDFs'
    downloaded_pdfs_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    total_figures = 0
    errors = []
    local_pdfs_to_move = []
    
    for idx, pdf_info in enumerate(pdf_list, start=1):
        pdf_path = pdf_info.get('local_path') or pdf_info.get('path')
        paper_id = pdf_info.get('paper_id', f"local_{idx:04d}")
        
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
                    'url': '',
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
                    'url': ''
                }
            )
            
            # 记录本地 PDF 需要移动
            local_pdfs_to_move.append({
                'source': pdf_path,
                'dest': downloaded_pdfs_dir / Path(pdf_path).name
            })
            
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
    
    # 移动本地 PDF 到 downloaded_PDFs 文件夹
    logger.info("=" * 60)
    logger.info(f"开始移动本地 PDF 到 downloaded_PDFs 文件夹...")
    moved_count = 0
    for pdf_move in local_pdfs_to_move:
        try:
            source = Path(pdf_move['source'])
            dest = Path(pdf_move['dest'])
            if source.exists():
                shutil.move(str(source), str(dest))
                logger.info(f"✓ 已移动：{source.name} → downloaded_PDFs/")
                moved_count += 1
        except Exception as e:
            logger.warning(f"✗ 移动失败 {pdf_move['source']}：{e}")
    
    logger.info(f"PDF 移动完成：已移动 {moved_count} 个文件")
    logger.info("=" * 60)
    logger.info(f"PDF 处理完成：成功 {success_count}，失败 {failed_count}，提取图版 {total_figures} 张")
    logger.info("=" * 60)
    
    return success_count, failed_count, total_figures, errors


def main():
    """主函数 - 本地模式"""
    parser = argparse.ArgumentParser(description='本地PDF扫描与处理系统')
    parser.add_argument('--config', default='config_local.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    logger = setup_logging(config)
    
    try:
        # 初始化各模块
        deduplicator = Deduplicator(
            db_file=f"{config['output']['base_dir']}/cache/collection_db.json"
        )
        local_reader = LocalPDFReader(
            root_dir=config['sources']['local']['root_dir'],
            recursive=config['sources']['local']['recursive']
        )
        metadata_manager = MetadataManager(output_dir=config['output']['base_dir'])
        
        # 本地扫描
        local_papers = collect_from_local(local_reader, config, deduplicator, logger)
        
        if not local_papers:
            logger.warning("没有找到任何本地 PDF 文件")
            print("⚠️  没有找到任何本地 PDF 文件")
            return
        
        # 处理 PDF
        success, failed, figures, errors = process_pdfs(
            local_papers, config, deduplicator, metadata_manager, logger
        )
        
        # 保存输出
        metadata_manager.save_to_excel(filename=config['output']['structure']['metadata_file'])
        metadata_manager.save_to_csv(filename="metadata.csv")
        if errors:
            metadata_manager.save_error_log(errors)
        
        stats = {
            'from_web': 0,
            'from_local': len(local_papers),
            'total_unique': len(local_papers),
            'success': success,
            'failed': failed,
            'total_figures': figures
        }
        metadata_manager.save_processing_report(stats)
        
        # 最终报告
        logger.info("=" * 60)
        logger.info("本地扫描系统已完成")
        logger.info(f"  ✓ 本地扫描：{stats['from_local']} 篇")
        logger.info(f"  ✓ 处理成功：{stats['success']} 篇")
        logger.info(f"  ✓ 处理失败：{stats['failed']} 篇")
        logger.info(f"  ✓ 提取图版：{stats['total_figures']} 张")
        logger.info("=" * 60)
        
        print("\n✅ 本地扫描完成！")
        print(f"📊 统计信息：")
        print(f"   本地扫描：{stats['from_local']} 篇")
        print(f"   处理成功：{stats['success']} 篇")
        print(f"   处理失败：{stats['failed']} 篇")
        print(f"   提取图版：{stats['total_figures']} 张")
        
    except Exception as e:
        logger.error(f"系统出错：{e}", exc_info=True)
        print(f"\n❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
