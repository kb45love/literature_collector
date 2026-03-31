# 项目完整生成报告

按照你的需求，我已为你生成了一个**完整的、生产级别的**植物考古学文献采集与图版提取系统。

## 📦 项目结构

```
literature_collector/
│
├── 🚀 主程序
│   ├── main.py                      # 核心执行脚本
│   ├── test_setup.py                # 环境检查脚本
│   ├── init_project.py              # 项目初始化
│   └── install_dependencies.py      # 自动依赖安装
│
├── ⚙️ 配置文件
│   ├── config.yaml                  # 主配置（支持双源、去重、图版识别）
│   ├── requirements.txt             # 严格版本依赖
│   └── requirements_flexible.txt    # 灵活版本依赖
│
├── 📚 核心模块
│   └── modules/
│       ├── __init__.py
│       ├── deduplicator.py          # 去重管理（MD5 + 相似度）
│       ├── downloader.py            # 网络下载器（Google Scholar + CNKI）
│       ├── local_reader.py          # 本地 PDF 扫描器
│       ├── pdf_processor.py         # PDF 处理（提取文本、图片、元数据）
│       ├── figure_extractor.py      # 图版识别（中英文图注识别）
│       └── metadata_manager.py      # 元数据管理与输出（Excel + CSV）
│
├── 📖 文档
│   ├── README.md                    # 完整功能说明
│   ├── QUICK_START.md               # 5 分钟快速开始
│   └── PROJECT_SUMMARY.md           # 本文件
│
├── 📁 数据目录
│   ├── data/PDFs/                   # 本地 PDF 存储（用户填充）
│   └── output/                      # 输出结果
│       ├── metadata.xlsx            # 元数据表格（主要输出）
│       ├── metadata.csv             # CSV 格式
│       ├── figures/                 # 提取的图版
│       ├── logs/                    # 日志
│       │   ├── collector.log
│       │   ├── errors.log
│       │   └── processing_report.txt
│       └── cache/
│           └── collection_db.json   # 去重数据库
│
└── 🔧 配置
    └── .gitignore                   # Git 忽略配置
```

## ✨ 核心功能清单

### ✅ 1. 双源文献采集
- **网络采集**
  - Google Scholar：自动搜索与下载
  - 知网（CNKI）：中文学术数据库支持
  - 自由定义搜索关键词和采集数量
  
- **本地扫描**
  - 递归扫描本地 PDF 目录
  - 智能路径识别
  - 支持大规模批量处理

### ✅ 2. 智能去重系统
- **三层去重机制**
  1. MD5 哈希检查：100% 准确识别重复文件
  2. 标题相似度：基于 SequenceMatcher 的相似度判断
  3. URL + 作者信息：元数据层面的去重
  
- **可配置参数**
  - 相似度阈值（0-1）
  - 去重算法选择
  - 持久化缓存数据库

### ✅ 3. 数量可控采集
```yaml
collection:
  max_from_web: 50      # 网络最多 50 篇
  max_from_local: 100   # 本地最多 100 篇
  total_limit: 150      # 总共最多 150 篇（-1 为无限）
```

### ✅ 4. 智能图版识别与提取
- **图注识别**
  - 中文：图 1、图 1.1、插图 1 等
  - 英文：Figure 1、Fig. 1、Fig 1 等
  - 混合语言支持
  - 自定义正则表达式模式

- **图版提取**
  - 自动识别 PDF 中的所有图片
  - 可配置最小尺寸过滤
  - PNG/JPEG 输出格式
  - DPI 分辨率设置

- **图注提取**
  - 根据图号从文本中提取图注
  - 上下文感知的图注匹配
  - 支持图注文本的自定义长度范围

### ✅ 5. 完整的元数据管理
输出格式：
- **Excel 表格**（metadata.xlsx）：
  - 纵列：paper_id, filename, title, author, year, url, md5_hash
  - 图版信息：page_num, figure_id, figure_caption, figure_path
  - 用户注释：species, status, notes
  
- **CSV 格式**（metadata.csv）：便于其他工具导入

### ✅ 6. 详细的日志记录
```
output/logs/
├── collector.log          # 完整操作日志（DEBUG/INFO/WARNING/ERROR）
├── errors.log             # 处理失败记录
└── processing_report.txt  # 统计报告
```

### ✅ 7. 故障恢复能力
- **缓存机制**：记录已处理文献的 MD5、元数据
- **断点记录**：支持中断后继续（通过 collection_db.json）
- **错误追踪**：详细的异常日志和错误报告

## 🔧 配置参数详解

### sources（采集来源）
```yaml
sources:
  local:
    enabled: true                # 是否启用本地扫描
    root_dir: "./data/PDFs"      # 本地 PDF 目录
    recursive: true              # 递归扫描子目录
  
  web:
    enabled: true                # 是否启用网络采集
    engines:
      google_scholar:
        enabled: true
        delay: 3                 # 请求之间的延迟（秒）
      cnki:
        enabled: true
        delay: 2
```

### collection（采集参数）
```yaml
collection:
  max_from_web: 50               # 网络最多采集数
  max_from_local: 100            # 本地最多扫描数
  total_limit: 150               # 总采集限制（-1=无限）
  keywords:
    - "植物考古学"
    - "植物遗迹"
    - "识别技术"
  language:
    - "zh-CN"                    # 中文
    - "en"                       # 英文
```

### deduplication（去重配置）
```yaml
deduplication:
  enabled: true                  # 启用去重
  check_by:
    - md5                        # 强度：最高（100% 准确）
    - title                      # 强度：中（相似度匹配）
    - authors                    # 强度：弱（列表匹配）
  similarity_threshold: 0.85     # 相似度（0-1）
  hash_algorithm: "md5"          # 哈希算法
```

### pdf_processing（PDF 处理）
```yaml
pdf_processing:
  extract_metadata: true         # 提取元数据（标题、作者等）
  extract_images: true           # 提取图片
  
  image_settings:
    min_width: 100               # 最小宽度（px）
    min_height: 100              # 最小高度
    format: "png"                # 输出格式
    dpi: 150                     # 分辨率
  
  ocr:
    enabled: false               # OCR 识别（需安装 Tesseract）
```

### figure_recognition（图版识别）
```yaml
figure_recognition:
  language: "mixed"              # zh | en | mixed
  split_subfigures: false        # 是否拆分 a, b, c 等子图
```

## 📊 使用示例

### 基础使用
```bash
# 1. 安装依赖
pip install -r requirements_flexible.txt

# 2. 初始化项目
python init_project.py

# 3. 运行采集
python main.py
```

### 高级用法
```bash
# 仅本地扫描（更快，用于测试）
python main.py --local-only

# 仅网络采集
python main.py --web-only

# 指定配置文件
python main.py --config config.yaml
```

### 输出示例
```
output/
├── metadata.xlsx
│   ├── paper_id: web_0001, web_0002, local_0001
│   ├── title: [论文标题]
│   ├── figure_id: 1, 2, 1.1, 2.1
│   └── figure_path: ./output/figures/page_1_img_1.png
│
├── figures/
│   ├── page_1_img_1.png        # 第 1 页的第 1 张图
│   ├── page_2_img_1.png
│   └── page_2_img_2.png
│
└── logs/
    ├── collector.log           # [2026-03-31 10:30:45] [INFO] 采集完成
    ├── errors.log
    └── processing_report.txt   # 统计：采集 150 篇，提取 487 张图
```

## 🎯 关键特性

| 特性 | 实现方式 | 优势 |
|------|---------|------|
| 双源采集 | requests + BeautifulSoup | 灵活，支持多平台 |
| 自动去重 | MD5 + SequenceMatcher | 准确，无遗漏 |
| 图版识别 | 正则表达式 | 快速，可自定义 |
| 图片提取 | PyMuPDF | 高质量，无损 |
| 元数据输出 | pandas + openpyxl | 结构化，易导入 |
| 日志记录 | Python logging | 详细，便于调试 |
| 错误恢复 | JSON 缓存 | 支持断点续传 |

## 💡 扩展方向

1. **添加新的搜索引擎**：编辑 `modules/downloader.py`
2. **自定义图注模式**：编辑 `modules/figure_extractor.py`
3. **启用 OCR 识别**：配置 `config.yaml` + 安装 Tesseract
4. **多进程加速**：使用 multiprocessing 并行处理
5. **Web 界面**：适配 Flask 或 Django

## 📝 文件说明

| 文件 | 功能 | 重要性 |
|------|------|--------|
| main.py | 主程序入口 | ⭐⭐⭐⭐⭐ |
| config.yaml | 配置参数 | ⭐⭐⭐⭐⭐ |
| modules/* | 核心功能 | ⭐⭐⭐⭐⭐ |
| requirements.txt | 依赖声明 | ⭐⭐⭐⭐ |
| test_setup.py | 环境检查 | ⭐⭐⭐ |
| README.md | 详细文档 | ⭐⭐⭐ |
| QUICK_START.md | 快速入门 | ⭐⭐ |

## ✅ 已实现功能检查清单

- [x] 网络文献下载（Google Scholar + CNKI）
- [x] 本地 PDF 扫描
- [x] MD5 哈希去重
- [x] 元数据相似度去重
- [x] 可配置的采集数量限制
- [x] PDF 元数据提取
- [x] PDF 图片提取
- [x] 图注识别与提取（中英文）
- [x] Excel 元数据表格输出
- [x] CSV 导出
- [x] 详细日志记录
- [x] 错误日志记录
- [x] 处理报告生成
- [x] 缓存和断点恢复
- [x] 完整的配置系统
- [x] 环境检查工具

## 🚀 快速开始

```bash
# 1. 切换到项目目录
cd "e:\machine_learn\vibe coding\literature_collector"

# 2. 安装依赖（如果网络有问题，使用灵活版本）
pip install -r requirements_flexible.txt

# 3. 运行采集
python main.py
```

## 📞 故障排除

| 问题 | 解决方案 |
|------|---------|
| 依赖安装失败 | 使用 requirements_flexible.txt 或手动 pip install |
| Google Scholar 超时 | 增加 config.yaml 中的 delay 参数 |
| PDF 打不开 | 检查文件是否损坏，查看 collector.log |
| 去重不工作 | 删除 output/cache/collection_db.json 重新开始 |
| 内存溢出 | 减少 max_from_web/max_from_local 参数 |

---

**项目版本**：1.0.0  
**创建日期**：2026 年 3 月  
**维护者**：GitHub Copilot

## 下一步

1. 完成依赖安装
2. 阅读 QUICK_START.md
3. 修改 config.yaml 配置
4. 运行 `python main.py` 开始采集
5. 查看 output/ 目录中的结果
