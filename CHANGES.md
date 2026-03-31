# 用途修改说明

## 修改内容

### 1. **图片文件名修改** 
修改了图片提取时的文件命名方式，使图片名称与对应的PDF文件名一致。

#### 文件：`modules/pdf_processor.py`

**修改类**：`PDFProcessor.extract_images()`方法

**改变内容**：
- 新增参数：`filename_prefix: str = None` - 用于指定图片文件名的前缀
- 原来的命名方式：`page_{page_num}_img_{img_index}.png`（如：page_1_img_1.png）
- **新的命名方式**：`{filename_prefix}_page{page_num}_fig{image_count}.png`（如：大植物_page1_fig1.png）

**示例**：
```python
# 原来
filename = f"page_{page_num}_img_{img_index}.png"  # page_1_img_1.png

# 现在
filename = f"{filename_prefix}_page{page_num}_fig{image_count}.png"  # 大植物_page1_fig1.png
```

### 2. **本地PDF统一管理**
修改了PDF处理流程，在提取完图片后，将本地PDF自动移动到`output/downloaded_PDFs`文件夹中，统一与网络下载的PDF一起存放。

#### 文件：`main.py`

**修改内容**：

1. **process_pdfs() 函数**：
   - 新增参数：`is_local` - 根据paper_id前缀判断是否为本地PDF
   - 新增变量：`local_pdfs_to_move` - 记录需要移动的本地PDF列表
   - 在提取图片时，同时创建`downloaded_PDFs`文件夹
   - 在图片提取时，传入PDF文件名（不含扩展名）作为`filename_prefix`参数
   
2. **PDF移动逻辑**：
   ```python
   # 处理后的本地PDF会被记录
   if is_local:
       local_pdfs_to_move.append({
           'source': pdf_path,
           'dest': downloaded_pdfs_dir / Path(pdf_path).name
       })
   ```
   
3. **批量移动**：
   - 在所有PDF处理完成后，自动将所有本地PDF从`data/PDFs/`移动到`output/downloaded_PDFs/`
   - 详细的移动日志会记录在日志文件中

## 工作流程变化

### 原来的流程：
```
本地PDF (data/PDFs/)
    ↓ 扫描 ↓
    图片提取 → 输出到 output/figures/ (page_1_img_1.png)
    └─ 元数据保存到 output/metadata.xlsx
    
网络下载PDF (output/downloaded_PDFs/)
    ↓ 下载并处理 ↓
    图片提取 → 输出到 output/figures/ (page_1_img_1.png)
    └─ 元数据保存到 output/metadata.xlsx

本地PDF仍保留在 data/PDFs/
```

### 新的流程：
```
本地PDF (data/PDFs/)
    ↓ 扫描 ↓
    图片提取 → 输出到 output/figures/ (大植物_page1_fig1.png)
    └─ 元数据保存到 output/metadata.xlsx
    ↓ 处理完成后 ↓
    自动移动到 output/downloaded_PDFs/

网络下载PDF (output/downloaded_PDFs/)
    ↓ 下载并处理 ↓
    图片提取 → 输出到 output/figures/ (paper_name_page1_fig1.png)
    └─ 元数据保存到 output/metadata.xlsx

✓ 所有PDF统一存放在 output/downloaded_PDFs/
```

## 使用示例

### 运行本地扫描
```bash
python main.py --local-only
```

处理完成后：
- ✓ 图片文件：`output/figures/大植物_page1_fig1.png` 等
- ✓ PDF文件：已移动到 `output/downloaded_PDFs/大植物.pdf`
- ✓ 元数据：已保存到 `output/metadata.xlsx`

### 运行双源采集
```bash
python main.py
```

处理完成后：
- ✓ 所有PDF（本地+网络）统一存放在 `output/downloaded_PDFs/`
- ✓ 所有图片文件名与对应的PDF文件名保持一致
- ✓ 完整的元数据已保存

## 关键变化总结

| 方面 | 原来 | 现在 |
|------|------|------|
| **图片文件名** | `page_1_img_1.png` | `filename_page1_fig1.png` |
| **本地PDF存放** | `data/PDFs/` | `data/PDFs/` → **自动移动到** `output/downloaded_PDFs/` |
| **PDF统一存放** | 分散（本地和网络分开） | **统一在** `output/downloaded_PDFs/` |
| **日志输出** | 无移动信息 | 详细的PDF移动日志 |

## 好处

1. **图片追溯性更好**：图片名称直接对应源PDF文件，便于追溯
2. **统一管理**：所有已处理的PDF统一存放，易于管理和备份
3. **清晰的数据流**：`data/PDFs/` 作为临时输入目录，`output/downloaded_PDFs/` 作为最终输出目录
4. **自动化程度高**：无需手动整理本地PDF，系统自动管理

## 技术细节

### 本地PDF识别
```python
# 根据paper_id的前缀判断
is_local = paper_id.startswith('local_')

# 或者通过路径判断
is_local = 'local_path' not in pdf_info and 'local' in str(pdf_info.get('path', '')).lower()
```

### 文件移动实现
```python
import shutil
shutil.move(str(source), str(dest))
```

### 兼容性
- 当`filename_prefix = None`时，图片提取会使用原来的命名方式：`page_{page_num}_img_{img_index}.png`
- 这确保向后兼容，不会破坏现有的代码逻辑
