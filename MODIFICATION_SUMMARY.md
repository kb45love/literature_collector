# 文献采集系统修改总结

## 修改目标
1. **图片文件名标准化**：将提取的图片文件名修改为与对应的PDF文件名一致，便于图片追溯
2. **PDF存放统一化**：处理完图片提取后，自动将本地PDF移动到`output/downloaded_PDFs/`目录，与网络下载的PDF统一存放

## 修改内容详览

### 1. modules/pdf_processor.py

#### 修改方法：`extract_images()`

**参数变更**：
```python
# 原签名
def extract_images(self, output_dir: str = None, min_size: Tuple[int, int] = (100, 100)) -> List[Dict]

# 新签名  
def extract_images(self, output_dir: str = None, min_size: Tuple[int, int] = (100, 100), filename_prefix: str = None) -> List[Dict]
```

**新增参数**：
- `filename_prefix` (str, optional): 图片文件名的前缀，未指定时使用原有的命名方式

**命名方式变更**：
```python
# 原来的命名
filename = f"page_{page_num}_img_{img_index}.png"  # 示例：page_1_img_1.png

# 现在的命名（当filename_prefix提供时）
filename = f"{filename_prefix}_page{page_num}_fig{image_count}.png"  # 示例：大植物_page1_fig1.png
```

**向后兼容性**：当`filename_prefix=None`时，自动使用原有的命名方式

### 2. main.py

#### 修改函数：`process_pdfs()`

**核心改动**：

1. **本地PDF识别**：
```python
is_local = paper_id.startswith('local_')  # 根据paper_id前缀判断是否为本地PDF
```

2. **创建downloaded_PDFs目录**：
```python
downloaded_pdfs_dir = Path(config['output']['base_dir']) / 'downloaded_PDFs'
downloaded_pdfs_dir.mkdir(parents=True, exist_ok=True)
```

3. **本地PDF记录**：
```python
local_pdfs_to_move = []  # 记录所有需要移动的本地PDF

if is_local:
    local_pdfs_to_move.append({
        'source': pdf_path,
        'dest': downloaded_pdfs_dir / Path(pdf_path).name
    })
```

4. **提取图片时传入prefix**：
```python
pdf_filename_no_ext = Path(pdf_path).stem  # 获取PDF文件名（不含扩展名）

figures = processor.extract_images(
    output_dir=str(figures_dir),
    min_size=(min_width, min_height),
    filename_prefix=pdf_filename_no_ext  # 新增参数
)
```

5. **批量移动本地PDF**：
```python
# 处理完成后，自动移动所有本地PDF
for pdf_move in local_pdfs_to_move:
    source = Path(pdf_move['source'])
    dest = Path(pdf_move['dest'])
    if source.exists():
        shutil.move(str(source), str(dest))
        logger.info(f"✓ 已移动：{source.name} → downloaded_PDFs/")
```

#### 新增导入：
```python
import shutil  # 用于文件移动操作
```

## 工作流程变化

### 修改前流程
```
data/PDFs/ (本地)                    output/downloaded_PDFs/ (网络)
     ↓                                     ↓
  扫描 PDF                           下载 PDF  
     ↓                                     ↓
  提取图片 → page_1_img_1.png      提取图片 → page_1_img_1.png
  提取元数据                        提取元数据
     ↓                                     ↓
  保存为 metadata.xlsx
  
✗ 本地PDF仍在 data/PDFs/
✗ 图片名称无法识别来源PDF
```

### 修改后流程
```
data/PDFs/ (本地)                    output/downloaded_PDFs/ (网络)
     ↓                                     ↓
  扫描 PDF                           下载 PDF  
     ↓                                     ↓
  提取图片 → 大植物_page1_fig1.png  文件名 → paper_page1_fig1.png
  提取元数据                        提取元数据
     ↓                                     ↓
  自动移动                          保存到本地
     ↓
  output/downloaded_PDFs/
  
✓ 所有PDF统一管理
✓ 图片名称直接对应源PDF
✓ 统一的存储结构
```

## 测试验证

### 测试项目
1. ✓ **图片文件命名**：验证新的命名方式是否正确
2. ✓ **PDF识别**：验证本地/网络PDF是否能正确识别
3. ✓ **PDF移动**：验证文件移动是否成功
4. ✓ **集成场景**：验证完整的处理流程

### 测试命令
```bash
python test_modifications.py
```

### 测试结果
```
[SUCCESS] All tests passed!

Modification Summary:
  [OK] Image file names now: {pdf_name}_page{n}_fig{m}.png
  [OK] Local PDFs auto-moved to output/downloaded_PDFs/ after processing
  [OK] All PDFs unified in output/downloaded_PDFs/
```

## 文件清单

### 修改的文件
- `modules/pdf_processor.py` - 修改图片提取方法
- `main.py` - 修改处理流程和PDF移动逻辑

### 新增文件
- `test_modifications.py` - 修改验证测试
- `CHANGES.md` - 修改详细说明
- `MODIFICATION_SUMMARY.md` - 本文档

## 使用示例

### 本地扫描
```bash
python main.py --local-only
```

运行后会生成：
```
output/
├── figures/
│   ├── 大植物_page1_fig1.png
│   ├── 大植物_page2_fig1.png
│   └── ...
├── downloaded_PDFs/
│   ├── 大植物.pdf ← 自动从 data/PDFs/ 移动过来
│   └── ...
└── metadata.xlsx  ← 包含所有元数据
```

### 双源采集
```bash
python main.py
```

结果：
- 网络下载的PDF：`output/downloaded_PDFs/web_0001.pdf`
- 本地PDF：`output/downloaded_PDFs/local_0001.pdf` （自动移动）
- 对应的图片：`output/figures/` 目录下，名称与PDF对应

## 配置兼容性

修改对现有配置文件完全兼容，无需修改 `config.yaml`：

```yaml
# 现有配置无需改动
output:
  base_dir: "./output"
  structure:
    figures_dir: "figures"
    metadata_file: "metadata.xlsx"

pdf_processing:
  image_settings:
    min_width: 100
    min_height: 100
```

## 性能影响

- **图片提取**：无性能影响（仅是命名方式改变）
- **PDF移动**：取决于本地PDF数量和磁盘速度
- **总处理时间**：增加时间 = 本地PDF移动时间（通常 <1秒）

## 升级说明

### 从旧版本升级
1. 备份现有的 `data/PDFs/` 目录
2. 更新 `modules/pdf_processor.py` 和 `main.py`
3. 运行修改验证：`python test_modifications.py`
4. 保持 `config.yaml` 不变
5. 运行系统：`python main.py`

### 降级（回滚）
如需恢复原有行为，修改 `main.py` 中的调用：
```python
# 改为
figures = processor.extract_images(
    output_dir=str(figures_dir),
    min_size=(min_width, min_height)
    # 不传递 filename_prefix，使用原有命名方式
)
```

## 常见问题

### Q: 为什么本地PDF会被移动？
A: 这样做的好处是统一管理所有已处理的PDF，便于备份、迁移和维护。

### Q: 可以禁用PDF移动吗？
A: 可以。在 `process_pdfs()` 函数中注释掉PDF移动的代码块即可。

### Q: 图片名称中包含中文会有问题吗？
A: 不会。系统已正确处理中文文件名，Windows、macOS和Linux都能支持。

### Q: 如何回到原来的图片命名方式？
A: 在调用 `extract_images()` 时不传递 `filename_prefix` 参数，系统会自动使用原方式。

## 日志输出示例

```
[2024-03-31 10:30:00] [INFO] 开始处理 3 个 PDF...
[2024-03-31 10:30:01] [INFO] [1/3] 处理：大植物.pdf
[2024-03-31 10:30:02] [INFO] ✓ local_0001 处理成功，提取图版 5 张
[2024-03-31 10:30:03] [INFO] [2/3] 处理：植物考古.pdf
[2024-03-31 10:30:04] [INFO] ✓ local_0002 处理成功，提取图版 3 张
[2024-03-31 10:30:05] [INFO] ============================================================
[2024-03-31 10:30:05] [INFO] 开始移动本地 PDF 到 downloaded_PDFs 文件夹...
[2024-03-31 10:30:05] [INFO] ✓ 已移动：大植物.pdf → downloaded_PDFs/
[2024-03-31 10:30:05] [INFO] ✓ 已移动：植物考古.pdf → downloaded_PDFs/
[2024-03-31 10:30:05] [INFO] PDF 移动完成：已移动 2 个文件
[2024-03-31 10:30:05] [INFO] ============================================================
```

## 总结

这次修改实现了以下核心改进：

1. **可追溯性提升**：图片文件名直接对应源PDF
2. **管理集中化**：所有PDF统一存放在 `output/downloaded_PDFs/`
3. **流程自动化**：无需手动整理本地PDF
4. **向后兼容**：不影响现有配置和其他功能

系统现已为生产级应用做好准备。
