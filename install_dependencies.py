"""
一键依赖安装脚本
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """安装 requirements.txt 中的所有依赖"""
    print("=" * 60)
    print("🚀 正在安装依赖包...")
    print("=" * 60)
    
    try:
        # 运行 pip install
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-U"],
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ 依赖包安装完成！")
            return True
        else:
            print("\n❌ 安装过程中出现错误")
            return False
    
    except Exception as e:
        print(f"❌ 安装失败：{e}")
        return False


def verify_installation():
    """验证所有依赖是否安装成功"""
    print("\n" + "=" * 60)
    print("✓ 验证依赖包...")
    print("=" * 60)
    
    packages = [
        ("requests", "requests"),
        ("bs4", "beautifulsoup4"),
        ("fitz", "pymupdf"),
        ("pdfplumber", "pdfplumber"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("yaml", "pyyaml"),
        ("PIL", "pillow"),
    ]
    
    all_ok = True
    for import_name, package_name in packages:
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (缺失)")
            all_ok = False
    
    print()
    return all_ok


def main():
    print("\n")
    print("🧪 文献采集系统 - 依赖安装向导")
    print("=" * 60)
    
    # 检查 requirements.txt 存在
    if not Path("requirements.txt").exists():
        print("❌ 错误：requirements.txt 不存在")
        return
    
    # 安装依赖
    if not install_requirements():
        print("\n⚠️  请手动运行：pip install -r requirements.txt")
        return
    
    # 验证安装
    if verify_installation():
        print("✅ 所有依赖已成功安装！")
        print("\n现在可以运行：python main.py")
    else:
        print("⚠️  某些依赖未安装，请重新运行此脚本")


if __name__ == "__main__":
    main()
