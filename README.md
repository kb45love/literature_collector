# 植物考古学文献采集与图版提取系统

一个功能完整的、生产级别的学术文献采集系统，具备网络搜索、本地扫描、自动去重、图版提取等功能。

## 📋 项目概览

```
literature_collector/
├── main.py                 # 主程序入口
├── test_setup.py          # 环境检查脚本
├── config.yaml            # 配置文件
├── requirements.txt       # Python 依赖包
├── README.md              # 使用说明（本文件）
├── modules/               # 核心模块目录
│   ├── __init__.py
│   ├── deduplicator.py    # 去重管理
│   ├── downloader.py      # 网络下载器
│   ├── local_reader.py    # 本地扫描器
│   ├── pdf_processor.py   # PDF 处理
│   ├── figure_extractor.py    # 图版识别
│   └── metadata_manager.py    # 元数据管理
├── data/                  # 数据目录
│   └── PDFs/              # 本地 PDF 存储
├── output/                # 输出目录
│   ├── figures/           # 提取的图版
│   ├── logs/              # 日志文件
│   └── metadata.xlsx      # 元数据表格
└── .github/
    └── agents/            # Agent 配置
```

## 🚀 快速开始

⚠️ **重要**：本项目已升级为**分离架构**！请查看 [SEPARATION_GUIDE.md](SEPARATION_GUIDE.md) 了解新的使用方法。

### 新架构说明（推荐）

项目现在分为两个**完全独立**的运行模式：

| 模式 | 脚本 | 配置文件 | 用途 |
|-----|------|--------|------|
| **本地模式** | `run_local.py` | `config_local.yaml` | 处理已有的本地PDF |
| **网络模式** | `run_web.py` | `config_web.yaml` | 从网络搜索和下载文献 |

### ⚡ 最快上手（2分钟）

#### 仅处理本地PDF（推荐首先尝试）
```bash
# 1. 确保依赖已安装
pip install -r requirements.txt

# 2. 准备PDF文件到 data/PDFs 目录

# 3. 运行本地扫描
python run_local.py

# 4. 查看结果在 output/ 目录
```

#### 从网络采集文献
```bash
# 1. 编辑 config_web.yaml，修改搜索关键词

# 2. 运行网络采集
python run_web.py

# 3. 查看结果在 output/ 目录
```

### 📖 详细使用指南

请见 [SEPARATION_GUIDE.md](SEPARATION_GUIDE.md)，包含：
- ✅ 详细的架构说明
- ✅ 完整的配置参数说明
- ✅ 各种使用场景下的命令
- ✅ 常见问题解答
- ✅ 故障排查指南

### （已弃用）原 main.py 的使用

原 `main.py` 仍然可用，但**不推荐**使用。

若需使用原脚本：
```bash
# 双源采集（本地 + 网络）
python main.py

# 仅网络采集
python main.py --web-only

# 仅本地扫描
python main.py --local-only

# 指定配置文件
python main.py --config config.yaml
```

关于原 main.py 的详细说明，参考 [SEPARATION_GUIDE.md](SEPARATION_GUIDE.md) 中的"迁移指南"章节。

## 🎯 核心功能

### ✅ 多源采集
- **网络采集**：Google Scholar + 知网（CNKI）
- **本地扫描**：递归扫描本地 PDF 目录

### ✅ 自动去重
- **MD5 哈希去重**：识别完全相同的文件
- **元数据去重**：检测标题相似度、URL 和作者信息
- **可配置阈值**：自定义相似度判断标准

### ✅ 数量可控
- `max_from_web`：网络采集数量限制
- `max_from_local`：本地扫描数量限制
- `total_limit`：总采集数量限制

### ✅ 智能图版提取
- 自动识别图注（中英文混合）
- 提取图片和图注文本
- 支持自定义图注模式

### ✅ 完整的输出
- **Excel 元数据表格**：paper_id, 标题, 作者, 图版等
- **CSV 导出**：便于其他工具处理
- **图版文件夹**：按 page_num 组织的图片
- **详细日志**：处理过程和错误记录
- **处理报告**：统计信息和执行总结

### ✅ 故障恢复
- 缓存数据库：避免重复处理
- 断点记录：支持中断恢复
- 详细错误日志：快速定位问题

## 📖 详细使用说明

### 修改配置文件

关键配置参数：

```yaml
# 搜索关键词（支持多个）
collection:
  keywords:
    - "植物考古学"
    - "古植物"
    - "识别技术"

# 图注识别（中文和英文）
figure_recognition:
  language: "mixed"        # 识别中英文混合
  patterns:
    cn:
      - "图\\s*\\d+"       # 识别"图 1"
      - "图\\s*\\d+\\.\\d+" # 识别"图 1.1"
    en:
      - "Figure\\s+\\d+"
      - "Fig\\.\\s*\\d+"

# 输出目录
output:
  base_dir: "./output"     # 主输出目录
  structure:
    figures_dir: "figures" # 图版保存目录
    metadata_file: "metadata.xlsx"
```

### 输出文件说明

运行完成后，`output/` 目录下：

```
output/
├── metadata.xlsx          # Excel 表格（主输出）
├── metadata.csv           # CSV 格式
├── figures/               # 提取的图版
│   ├── page_1_img_1.png
│   ├── page_2_img_1.png
│   └── ...
├── logs/
│   ├── collector.log      # 详细日志
│   ├── errors.log         # 错误记录
│   └── processing_report.txt  # 处理报告
└── cache/
    └── collection_db.json # 去重数据库
```

### 元数据表格字段

Excel 表格 `metadata.xlsx` 包含以下列：

| 字段 | 说明 | 示例 |
|------|------|------|
| paper_id | 文献 ID | web_0001 / local_0001 |
| filename | PDF 文件名 | paper.pdf |
| title | 论文标题 | 植物考古学识别方法 |
| author | 作者 | 张三 |
| year | 发表年份 | 2023 |
| url | 文献链接 | https://... |
| md5_hash | 文件哈希 | abc123... |
| page_num | 图版所在页码 | 2 |
| figure_id | 图版号 | 1, 2, 1.1 等 |
| figure_caption | 图注文本 | 植物遗迹示意图 |
| figure_path | 图片本地路径 | ./output/figures/... |
| species | 物种信息 | 空字段（需手动填充） |
| status | 处理状态 | ✓ 成功 |

## ⚙️ 高级配置

### 启用网络代理

如果需要翻墙或使用代理：

```yaml
proxy:
  enabled: true
  http: "http://127.0.0.1:7897"
  https: "http://127.0.0.1:7897"
```

### 调整去重策略

```yaml
deduplication:
  check_by:
    - md5          # 文件哈希（强）
    - title        # 标题相似度（中）
    - authors      # 作者信息（弱）
  
  similarity_threshold: 0.85  # 0-1，越低越容易被认为重复
```

### 图片提取参数

```yaml
pdf_processing:
  image_settings:
    min_width: 100    # 最小宽度（像素）
    min_height: 100   # 最小高度
    format: "png"     # 输出格式
    dpi: 150          # 分辨率
```

### 日志级别

```yaml
logging:
  level: "DEBUG"    # DEBUG | INFO | WARNING | ERROR
```

## 🔍 故障排除

### 问题 1：依赖包安装失败

```bash
# 更新 pip
python -m pip install --upgrade pip

# 重新安装所有依赖
pip install -r requirements.txt --upgrade
```

### 问题 2：Google Scholar 无法访问

- 可能的原因：IP 被限制、网络问题
- 解决方案：
  1. 配置代理
  2. 增加搜索延迟：`delay: 5`
  3. 使用 `--local-only` 仅本地扫描

### 问题 3：PDF 无法打开

- 检查 PDF 是否损坏：`test_setup.py`
- 查看日志文件：`output/logs/collector.log`
- 确保 PyMuPDF 正确安装

### 问题 4：去重不工作

检查 `config.yaml` 的去重配置：
- 确保 `deduplication.enabled: true`
- 检查 `collection_db.json` 是否存在
- 清除缓存重新运行（删除 `output/cache/collection_db.json`）

### 问题 5：内存占用过高

- 减少 `max_from_web` 和 `max_from_local`
- 更新依赖包：`pip install --upgrade pymupdf pandas`
- 分批处理（多次运行，手动去重）

## 📊 性能优化

### 批量处理大量 PDF

```bash
# 第一批
python main.py --local-only --config config_batch1.yaml

# 第二批（修改 data dir）
python main.py --local-only --config config_batch2.yaml
```

### 并行处理（多核）

在 `main.py` 中添加多进程支持（需要修改代码）

### 减少网络延迟

```yaml
sources:
  web:
    engines:
      google_scholar:
        delay: 1        # 减少延迟（小心被限制）
```

## 🎓 扩展开发

### 添加新的搜索引擎

编辑 `modules/downloader.py`，添加新方法：

```python
def search_arxiv(self, keywords: List[str], max_results: int = 20) -> List[Dict]:
    """搜索 arXiv"""
    # 实现搜索逻辑
    pass
```

### 自定义图注模式

编辑 `modules/figure_extractor.py`：

```python
DEFAULT_PATTERNS = {
    "zh": [
        r"附图\s*(\d+)",    # 新增：附图
        r"【图(\d+)】",     # 新增：【图1】格式
    ],
    "en": [...]
}
```

### 添加 OCR 识别

编辑 `config.yaml` 和 `modules/pdf_processor.py`：

```python
if config['pdf_processing']['ocr']['enabled']:
    import pytesseract
    # 添加 OCR 逻辑
```

## 📝 规范说明

### 日志级别说明

- **DEBUG**：详细的调试信息，包括所有关键步骤
- **INFO**：重要的业务信息，如采集进度
- **WARNING**：警告信息，如重复检测
- **ERROR**：错误信息，如处理失败

### 文件命名规范

- 论文 ID：`web_0001`, `local_0001`（从 0001 开始）
- 图片：`page_1_img_1.png`（页数_图片序号）
- 日志：`collector.log`, `errors.log`

## 🔐 数据安全

- 缓存数据库：`output/cache/collection_db.json`
- 去重记录：保存论文的 MD5 和元数据
- 建议定期备份 `output/` 目录

## 📞 支持

遇到问题？

1. 查看日志：`output/logs/collector.log`
2. 运行诊断：`python test_setup.py`
3. 检查配置：`config.yaml`
4. 阅读本 README

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有开源项目的支持：
- PyMuPDF (fitz)
- Beautiful Soup
- pandas
- requests

---

**版本**：1.0.0  
**最后更新**：2026 年 3 月
