"""
模块初始化脚本 - 确保必要目录存在
"""

from pathlib import Path

def init_directories():
    """初始化项目目录结构"""
    directories = [
        "data/PDFs",
        "output/logs",
        "output/figures",
        "output/cache",
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print(f"✓ 项目目录已初始化")


if __name__ == "__main__":
    init_directories()
    print("项目已准备就绪！")
    print("接下来运行：python main.py")
