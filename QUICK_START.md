# 快速开始指南

## 5 分钟快速开始

### 步骤 1：安装依赖（2 分钟）

```bash
cd "E:\machine_learn\vibe coding\literature_collector"
pip install -r requirements.txt
```

### 步骤 2：验证环境（1 分钟）

```bash
python test_setup.py
```

预期输出：
```
✓ 所有依赖包已安装
✓ 配置文件已加载
✓ 所有模块正确导入
✅ 环境检查完成！
```

### 步骤 3：准备 PDF（准备工作）

将你的本地 PDF 文献放入：
```
data/PDFs/
```

或更新 `config.yaml` 中的路径。

### 步骤 4：运行采集（2 分钟）

```bash
# 推荐：双源采集
python main.py

# 或仅本地扫描
python main.py --local-only

# 或仅网络采集
python main.py --web-only
```

### 步骤 5：查看结果

采集完成后，检查输出目录：
```
output/
├── metadata.xlsx          # 📊 元数据表格（主要输出）
├── metadata.csv           # 📄 CSV 格式
├── figures/               # 🖼️ 提取的图版
└── logs/
    ├── collector.log      # 📋 详细日志
    ├── errors.log         # ⚠️ 错误记录
    └── processing_report.txt  # 📈 处理报告
```

## 常见命令

```bash
# 默认采集（读取 config.yaml）
python main.py

# 仅本地扫描（更快，用于开发）
python main.py --local-only

# 仅网络搜索
python main.py --web-only

# 指定配置文件
python main.py --config config.yaml

# 显示帮助
python main.py --help
```

## 基础配置修改

编辑 `config.yaml`：

```yaml
collection:
  max_from_web: 20          # 网络采集篇数
  max_from_local: 50        # 本地扫描篇数
  keywords:                 # 搜索关键词
    - "植物考古学"
    - "古植物"
    - "识别方法"

sources:
  local:
    root_dir: "./data/PDFs" # 本地 PDF 路径
```

## 输出文件解读

### metadata.xlsx（最重要）

这是一个 Excel 表格，包含每个提取的图版信息：

| 列名 | 说明 | 示例 |
|------|------|------|
| paper_id | 论文编号 | web_0001 |
| filename | 原始文件名 | plant_fossil.pdf |
| title | 论文标题 | 新生代植物化石鉴定 |
| page_num | 图版在第几页 | 3 |
| figure_id | 图版号 | 1, 2.1 等 |
| figure_caption | 图注（图版说明）| 叶片化石显微图 |
| figure_path | 图片保存位置 | ./output/figures/... |
| status | 处理状态 | ✓ 成功 |

### figures/ 目录

示例：
```
figures/
├── page_1_img_1.png       # 第 1 页第 1 张图
├── page_2_img_1.png       # 第 2 页第 1 张图
├── page_2_img_2.png       # 第 2 页第 2 张图
└── page_4_img_1.png
```

### collector.log（调试参考）

记录所有操作过程，包括：
- ✓ 已成功处理
- ✗ 处理失败原因
- ⚠️ 检测到重复
- 📊 统计数据

## 故障快速诊断

如果运行失败：

1. **检查环境**
   ```bash
   python test_setup.py
   ```

2. **查看日志**
   ```bash
   cat output/logs/collector.log
   ```

3. **常见问题**
   - PDF 打不开：检查文件是否损坏
   - 网络超时：检查代理配置或增加 delay
   - 内存不足：减少 max_from_* 参数

## 下一步

- 详细配置：查看 README.md
- 高级用法：参考 modules/ 源代码中的 docstring
- 自定义开发：编辑 config.yaml 和对应模块

---

💡 **提示**：首次运行时建议用 `--local-only` 快速测试
