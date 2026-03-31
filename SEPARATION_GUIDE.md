# 架构调整说明

## 📋 变更目的

本项目已经将**本地PDF处理**和**网络文献采集**完全分离，避免混合在一个代码中，提高代码可维护性和清晰性。

---

## 🔄 新的架构设计

### 原有设计（已废弃）
```
main.py
├── 本地扫描逻辑
├── 网络采集逻辑  
└── 共享处理逻辑
   └── --local-only / --web-only 开关切换
```
**问题**：功能混杂在一个文件中，修改一个功能时容易影响另一个

### 新的设计（推荐使用）
```
run_local.py          运行本地PDF扫描处理
├── config_local.yaml 仅包含本地相关配置
└── 不依赖网络模块

run_web.py            运行网络文献采集处理
├── config_web.yaml   仅包含网络相关配置
└── 不依赖本地扫描模块

modules/              共享的处理模块（保持不变）
```

**优势**：
- ✅ 功能完全独立，不会相互干扰
- ✅ 配置清晰明确，无冗余选项
- ✅ 代码易于维护和扩展
- ✅ 可以独立运行、测试和部署
- ✅ 清晰的职责分离

---

## 🚀 使用方法

### 1️⃣ 本地PDF扫描和提取

**仅处理已有的本地PDF文件，不涉及网络操作**

```bash
# 使用默认配置
python run_local.py

# 使用自定义配置文件
python run_local.py --config config_local.yaml
```

**功能**：
- 扫描 `data/PDFs` 目录中的所有PDF
- 提取元数据、文本和图版
- 去重处理
- 生成元数据表格和图版文件

**输出**：
- `output/figures/`      - 提取的图版
- `output/metadata.csv`  - 元数据表格
- `output/logs/local_collector.log` - 运行日志

---

### 2️⃣ 网络文献采集和提取

**从Google Scholar、CNKI等网络源搜索和下载文献**

```bash
# 使用默认配置
python run_web.py

# 使用自定义配置文件
python run_web.py --config config_web.yaml
```

**功能**：
- 根据关键词搜索文献（Google Scholar、CNKI）
- 批量下载PDF文件
- 去重处理
- 提取元数据、文本和图版
- 生成元数据表格和图版文件

**输出**：
- `output/downloaded_PDFs/` - 下载的PDF文件
- `output/figures/`         - 提取的图版
- `output/metadata.csv`     - 元数据表格
- `output/logs/web_collector.log` - 运行日志

---

## ⚙️ 配置说明

### config_local.yaml（本地模式专用）

```yaml
sources:
  local:
    root_dir: "./data/PDFs"    # 本地PDF目录
    recursive: true             # 是否递归扫描子目录

collection:
  max_from_local: 100           # 最多扫描文件数

# ... 其他处理配置
```

**仅包含**：
- 本地扫描参数
- PDF处理参数
- 图注识别参数
- 日志配置

**不包含**：
- ❌ 网络引擎配置
- ❌ 网络代理配置
- ❌ 搜索关键词配置

---

### config_web.yaml（网络模式专用）

```yaml
sources:
  web:
    engines:
      google_scholar:
        enabled: true
        delay: 3
      cnki:
        enabled: true
        delay: 2

collection:
  max_from_web: 50
  keywords:
    - "植物考古学"
    - "植物遗迹"

# ... 其他处理配置

proxy:
  enabled: true
  http: "http://127.0.0.1:7897"
  https: "http://127.0.0.1:7897"
```

**仅包含**：
- 网络引擎配置
- 搜索关键词配置
- 网络代理设置
- PDF处理参数
- 图注识别参数
- 日志配置

**不包含**：
- ❌ 本地扫描路径
- ❌ 本地文件处理参数

---

## 🔧 如何修改配置

### 修改本地扫描目录
编辑 `config_local.yaml`：
```yaml
sources:
  local:
    root_dir: "./your_custom_pdf_path"  # 改为你的路径
```

### 修改搜索关键词
编辑 `config_web.yaml`：
```yaml
collection:
  keywords:
    - "你的关键词1"
    - "你的关键词2"
    - "你的关键词3"
```

### 修改最大采集数量
编辑相应的配置文件：
```yaml
collection:
  max_from_web: 100    # 网络采集最多数量
  max_from_local: 50   # 本地扫描最多数量
```

### 启用/禁用代理
编辑 `config_web.yaml`：
```yaml
proxy:
  enabled: false       # 设为 false 不使用代理
```

---

## 📊 输出结构

两个脚本的输出目录结构相同：

```
output/
├── figures/                    # 提取的图版
│   ├── pdf_filename_001.png
│   └── pdf_filename_002.png
├── downloaded_PDFs/            # 下载的PDF（仅web模式）
│   ├── paper1.pdf
│   └── paper2.pdf
├── metadata.csv                # 元数据（CSV格式）
├── metadata.xlsx               # 元数据（Excel格式）
├── cache/
│   └── collection_db.json      # 去重数据库
└── logs/
    ├── local_collector.log     # 本地模式日志
    └── web_collector.log       # 网络模式日志
```

---

## 🔄 迁移指南（从旧版本）

### 如果之前使用 `main.py --web-only`
改用 `python run_web.py`

### 如果之前使用 `main.py --local-only`
改用 `python run_local.py`

### 如果之前使用 `main.py`（两个都运行）
需要分别运行：
```bash
python run_local.py   # 先运行本地
python run_web.py     # 后运行网络
```

---

## ⚡ 快速开始

### 只处理本地PDF
```bash
# 1. 将PDF放入 data/PDFs 目录
# 2. 运行本地扫描
python run_local.py
# 3. 在 output/ 目录查看结果
```

### 只采集网络文献
```bash
# 1. 编辑 config_web.yaml，修改搜索关键词
# 2. 运行网络采集
python run_web.py
# 3. 在 output/ 目录查看结果
```

### 同时运行两个模式
```bash
# 方案1：按顺序运行
python run_local.py && python run_web.py

# 方案2：在不同终端并行运行
# 终端1：python run_local.py
# 终端2：python run_web.py
```

---

## 🐛 故障排查

### 运行 `run_local.py` 时提示"没有找到任何本地PDF文件"
- ✅ 检查 `data/PDFs` 目录是否存在
- ✅ 检查目录中是否有PDF文件
- ✅ 确认 `config_local.yaml` 中的 `root_dir` 路径正确

### 运行 `run_web.py` 时网络超时
- ✅ 检查网络连接
- ✅ 检查代理设置是否正确
- ✅ 尝试在 `config_web.yaml` 中禁用代理或修改代理地址

### 图版提取失败
- ✅ 确保PDF文件有效且包含图像
- ✅ 检查 `config_*.yaml` 中的图像最小尺寸设置
- ✅ 查看日志文件了解具体错误信息

---

## 📝 原 main.py 的状态

原 `main.py` 已保留以供参考，但**不推荐使用**。建议：
- ✅ 使用 `run_local.py` 处理本地PDF
- ✅ 使用 `run_web.py` 采集网络文献
- ⚠️ 避免使用原 `main.py`

如果还需要使用原脚本，可以继续运行，但新增功能和bug修复将在新脚本中进行。

---

## 💡 常见问题

**Q: 两个脚本的输出会冲突吗？**
A: 不会。默认都输出到 `output/` 目录，但日志分别保存为 `local_collector.log` 和 `web_collector.log`。如果需要分离输出，可以修改 `config_*.yaml` 中的 `output.base_dir` 参数。

**Q: 可以同时编辑两个配置文件后运行两个脚本吗？**
A: 可以，完全独立。可以并行运行，也可以顺序运行。

**Q: 如何禁用某个搜索引擎？**
A: 在 `config_web.yaml` 中修改：
```yaml
sources:
  web:
    engines:
      google_scholar:
        enabled: false      # 禁用 Google Scholar
      cnki:
        enabled: true       # 启用 CNKI
```

---

## 📚 相关文件

- [`run_local.py`](run_local.py) - 本地处理脚本
- [`run_web.py`](run_web.py) - 网络采集脚本
- [`config_local.yaml`](config_local.yaml) - 本地配置
- [`config_web.yaml`](config_web.yaml) - 网络配置
- [`main.py`](main.py) - 原脚本（不推荐，仅供参考）

---

**版本信息**：本说明适用于架构分离版本（包含 `run_local.py` 和 `run_web.py`）

最后更新：2026-03-31
