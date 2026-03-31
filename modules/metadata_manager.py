"""
元数据管理与输出：生成 Excel 表格、日志等
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetadataManager:
    """管理和输出元数据"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logs_dir = self.output_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.data = []
    
    def add_record(self, record: Dict):
        """添加一条元数据记录"""
        self.data.append(record)
    
    def add_records(self, records: List[Dict]):
        """批量添加记录"""
        self.data.extend(records)
    
    def save_to_excel(
        self,
        filename: str = "metadata.xlsx",
        sheet_name: str = "文献与图版"
    ) -> Path:
        """
        保存为 Excel 表格
        
        Args:
            filename: 输出文件名
            sheet_name: 工作表名
        
        Returns:
            输出文件路径
        """
        if not self.data:
            logger.warning("没有数据可保存")
            return None
        
        try:
            df = pd.DataFrame(self.data)
            
            output_file = self.output_dir / filename
            
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 调整列宽
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"元数据已保存：{output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"保存 Excel 失败：{e}")
            return None
    
    def save_to_csv(
        self,
        filename: str = "metadata.csv"
    ) -> Path:
        """保存为 CSV"""
        if not self.data:
            logger.warning("没有数据可保存")
            return None
        
        try:
            df = pd.DataFrame(self.data)
            output_file = self.output_dir / filename
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            logger.info(f"元数据已保存：{output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"保存 CSV 失败：{e}")
            return None
    
    def save_error_log(self, errors: List[Dict]):
        """保存错误日志"""
        error_log_path = self.logs_dir / "errors.log"
        
        try:
            with open(error_log_path, 'w', encoding='utf-8') as f:
                f.write("=== 处理错误日志 ===\n")
                f.write(f"生成时间：{datetime.now().isoformat()}\n\n")
                
                for error in errors:
                    f.write(f"文献：{error.get('paper_id', 'Unknown')}\n")
                    f.write(f"错误：{error.get('error', '')}\n")
                    f.write(f"时间：{error.get('timestamp', '')}\n")
                    f.write("-" * 50 + "\n")
            
            logger.info(f"错误日志已保存：{error_log_path}")
        
        except Exception as e:
            logger.error(f"保存错误日志失败：{e}")
    
    def save_processing_report(self, stats: Dict) -> Path:
        """保存处理报告"""
        report_path = self.logs_dir / "processing_report.txt"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("="*50 + "\n")
                f.write("文献采集处理报告\n")
                f.write("="*50 + "\n\n")
                
                f.write(f"运行时间：{datetime.now().isoformat()}\n\n")
                
                f.write("统计信息：\n")
                f.write(f"  - 从网络采集：{stats.get('from_web', 0)} 篇\n")
                f.write(f"  - 从本地扫描：{stats.get('from_local', 0)} 篇\n")
                f.write(f"  - 去重后总计：{stats.get('total_unique', 0)} 篇\n")
                f.write(f"  - 处理成功：{stats.get('success', 0)} 篇\n")
                f.write(f"  - 处理失败：{stats.get('failed', 0)} 篇\n")
                f.write(f"  - 提取图版总数：{stats.get('total_figures', 0)} 张\n\n")
                
                f.write("详细信息：\n")
                for key, value in stats.items():
                    if key not in ['from_web', 'from_local', 'total_unique', 'success', 'failed', 'total_figures']:
                        f.write(f"  - {key}: {value}\n")
            
            logger.info(f"处理报告已保存：{report_path}")
            return report_path
        
        except Exception as e:
            logger.error(f"保存处理报告失败：{e}")
            return None
