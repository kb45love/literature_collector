"""
快速测试脚本：验证所有依赖和模块是否正确安装
"""

import sys
from pathlib import Path

def test_imports():
    """测试所有必要的导入"""
    print("=" * 60)
    print("模块导入测试")
    print("=" * 60)
    
    modules = [
        ("requests", "requests"),
        ("bs4", "BeautifulSoup4"),
        ("fitz", "PyMuPDF"),
        ("pdfplumber", "pdfplumber"),
        ("pandas", "pandas"),
        ("yaml", "PyYAML"),
        ("PIL", "Pillow"),
    ]
    
    missing = []
    for module, package_name in modules:
        try:
            __import__(module)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} (缺失)")
            missing.append(package_name)
    
    print()
    if missing:
        print(f"缺失的包：{', '.join(missing)}")
        print("请运行：pip install -r requirements.txt")
        return False
    
    print("✓ 所有依赖包已安装")
    return True


def test_config():
    """测试配置文件"""
    print("\n" + "=" * 60)
    print("配置文件测试")
    print("=" * 60)
    
    import yaml
    
    config_file = Path("config.yaml")
    if not config_file.exists():
        print(f"✗ 配置文件不存在：{config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"✓ 配置文件已加载")
        print(f"  - 网络采集启用：{config['sources']['web']['enabled']}")
        print(f"  - 本地扫描启用：{config['sources']['local']['enabled']}")
        print(f"  - 输出目录：{config['output']['base_dir']}")
        
        return True
    
    except Exception as e:
        print(f"✗ 配置文件读取失败：{e}")
        return False


def test_directories():
    """测试必要目录"""
    print("\n" + "=" * 60)
    print("目录结构测试")
    print("=" * 60)
    
    required_dirs = [
        "modules",
        "data/PDFs",
        "output",
        "output/logs",
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"⚠ {dir_path}/ (缺失，运行时会自动创建)")
    
    return True


def test_modules():
    """测试自定义模块"""
    print("\n" + "=" * 60)
    print("自定义模块测试")
    print("=" * 60)
    
    try:
        from modules import (
            Deduplicator,
            LiteratureDownloader,
            LocalPDFReader,
            PDFProcessor,
            FigureExtractor,
            MetadataManager
        )
        
        print("✓ Deduplicator")
        print("✓ LiteratureDownloader")
        print("✓ LocalPDFReader")
        print("✓ PDFProcessor")
        print("✓ FigureExtractor")
        print("✓ MetadataManager")
        
        return True
    
    except ImportError as e:
        print(f"✗ 模块导入失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n")
    print("🧪 植物考古学文献采集系统 - 环境验证")
    print()
    
    tests = [
        ("导入测试", test_imports),
        ("配置测试", test_config),
        ("目录测试", test_directories),
        ("模块测试", test_modules),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name}：{e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ 环境检查完成！所有检查都通过了")
        print("\n现在可以运行采集系统：")
        print("  python main.py")
        print("  python main.py --web-only")
        print("  python main.py --local-only")
        sys.exit(0)
    else:
        print("❌ 环境检查未完全通过，请解决上述问题")
        sys.exit(1)


if __name__ == "__main__":
    main()
