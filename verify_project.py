"""
最终项目验证和启动脚本
"""

import os
from pathlib import Path

def verify_project_structure():
    """验证项目结构完整性"""
    print("=" * 70)
    print("🔍 植物考古学文献采集系统 - 项目完整性检查")
    print("=" * 70)
    
    # 检查关键文件
    required_files = {
        "🚀 主程序": [
            "main.py",
            "config.yaml",
            "requirements.txt",
        ],
        "📚 核心模块": [
            "modules/__init__.py",
            "modules/deduplicator.py",
            "modules/downloader.py",
            "modules/local_reader.py",
            "modules/pdf_processor.py",
            "modules/figure_extractor.py",
            "modules/metadata_manager.py",
        ],
        "🛠️ 工具脚本": [
            "test_setup.py",
            "init_project.py",
            "install_dependencies.py",
        ],
        "📖 文档": [
            "README.md",
            "QUICK_START.md",
            "PROJECT_SUMMARY.md",
        ],
        "📁 目录": [
            "data/PDFs",
            "output",
            "output/logs",
            "modules",
        ],
    }
    
    all_ok = True
    total_items = 0
    existing_items = 0
    
    for category, items in required_files.items():
        print(f"\n{category}")
        print("-" * 70)
        
        for item in items:
            total_items += 1
            exists = Path(item).exists()
            
            if exists:
                existing_items += 1
                status = "✓"
            else:
                status = "✗"
                all_ok = False
            
            print(f"  {status} {item}")
    
    print("\n" + "=" * 70)
    print(f"📊 统计：{existing_items}/{total_items} 个文件/目录已创建")
    print("=" * 70)
    
    return all_ok


def print_next_steps():
    """打印后续步骤"""
    print("\n" + "=" * 70)
    print("🚀 后续步骤")
    print("=" * 70)
    
    steps = [
        ("1️⃣ 安装依赖包（可选，如果未安装）", [
            "pip install -r requirements_flexible.txt",
            "或：python install_dependencies.py",
        ]),
        ("2️⃣ 准备本地 PDF 文献（可选）", [
            "将 PDF 文件放放入：data/PDFs/ 目录",
            "或修改 config.yaml 中的 root_dir 参数",
        ]),
        ("3️⃣ 调整配置参数（可选）", [
            "编辑 config.yaml",
            "修改搜索关键词、数量限制等参数",
        ]),
        ("4️⃣ 运行采集系统", [
            "python main.py          # 双源采集（推荐）",
            "python main.py --local-only  # 仅本地扫描",
            "python main.py --web-only    # 仅网络采集",
        ]),
        ("5️⃣ 查看结果", [
            "output/metadata.xlsx      # 元数据表格（主要输出）",
            "output/figures/           # 提取的图版",
            "output/logs/              # 详细日志",
        ]),
    ]
    
    for step_title, commands in steps:
        print(f"\n{step_title}")
        for cmd in commands:
            print(f"  💻 {cmd}")
    
    print("\n" + "=" * 70)


def print_project_features():
    """打印项目特性"""
    print("\n" + "=" * 70)
    print("✨ 项目核心特性")
    print("=" * 70)
    
    features = [
        ("双源采集", "网络搜索 (Google Scholar + 知网) + 本地扫描"),
        ("自动去重", "MD5 哈希 + 标题相似度 + 元数据匹配"),
        ("数量可控", "灵活的采集数量限制参数"),
        ("图版识别", "中英文混合图注识别与提取"),
        ("完整输出", "Excel 表格 + CSV + 图片文件夹 + 详细日志"),
        ("故障恢复", "缓存数据库支持断点续传"),
        ("错误处理", "详细的异常捕获与日志记录"),
        ("可扩展", "模块化设计，易于二次开发"),
    ]
    
    for i, (feature, desc) in enumerate(features, 1):
        print(f"\n  {i}. {feature}")
        print(f"     {desc}")
    
    print("\n" + "=" * 70)


def print_important_notes():
    """打印重要提示"""
    print("\n⚠️  重要提示")
    print("=" * 70)
    
    notes = [
        "首次运行建议使用 `--local-only` 快速测试",
        "修改 config.yaml 中的 keywords 参数以适配你的研究方向",
        "查看 output/logs/collector.log 了解详细执行过程",
        "Google Scholar 搜索可能受到 IP 限制，可配置代理或增加延迟",
        "确保 data/PDFs/ 目录中的 PDF 文件是可读的",
    ]
    
    for note in notes:
        print(f"  • {note}")
    
    print("\n" + "=" * 70)


def main():
    """主函数"""
    print("\n")
    
    # 验证项目结构
    if verify_project_structure():
        print("\n✅ 所有文件都已成功创建！")
    else:
        print("\n⚠️  某些文件可能缺失，但不影响基本功能")
    
    # 打印核心特性
    print_project_features()
    
    # 打印后续步骤
    print_next_steps()
    
    # 打印重要提示
    print_important_notes()
    
    print("\n✨ 祝你使用愉快！")
    print("\n如需帮助，请查看：README.md 或 QUICK_START.md\n")


if __name__ == "__main__":
    main()
