# 测试文档

## 测试概述

本测试套件覆盖了 EPUB 阅读器应用的核心功能，包括：

- **阅读功能** - 图书馆页面、阅读器页面、目录导航
- **翻页跳转** - 章节导航、前后翻页、TOC 点击跳转
- **导出功能** - Markdown 单文件、Markdown 章节、PDF 导出
- **图片处理** - 图片服务、base64 编码
- **错误处理** - 404 错误、无效参数处理

## 测试文件结构

```
backend/tests/
├── __init__.py                 # 测试包初始化
├── conftest.py                 # Pytest 配置和 fixtures
├── test_reading.py             # 阅读功能测试
├── test_export.py              # 导出功能测试
├── test_image_processor.py     # 图片处理测试
├── test_export_service.py      # 导出服务测试
└── README.md                   # 本文件
```

## 安装测试依赖

```bash
pip install pytest pytest-cov httpx beautifulsoup4
```

或使用 uv：

```bash
uv pip install pytest pytest-cov httpx beautifulsoup4
```

## 运行测试

### 运行所有测试

```bash
pytest backend/tests/
```

### 运行特定测试文件

```bash
# 测试阅读功能
pytest backend/tests/test_reading.py

# 测试导出功能
pytest backend/tests/test_export.py

# 测试图片处理
pytest backend/tests/test_image_processor.py

# 测试导出服务
pytest backend/tests/test_export_service.py
```

### 运行特定测试类

```bash
# 测试图书馆视图
pytest backend/tests/test_reading.py::TestLibraryView

# 测试 Markdown 导出
pytest backend/tests/test_export.py::TestMarkdownExport

# 测试 PDF 导出
pytest backend/tests/test_export.py::TestPDFExport
```

### 运行特定测试用例

```bash
pytest backend/tests/test_reading.py::TestLibraryView::test_library_page_loads
```

### 显示详细输出

```bash
pytest backend/tests/ -v
```

### 显示打印输出

```bash
pytest backend/tests/ -s
```

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest backend/tests/ --cov=. --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 只运行失败的测试

```bash
pytest backend/tests/ --lf
```

## 测试覆盖范围

### test_reading.py

#### TestLibraryView

- ✅ 图书馆页面加载
- ✅ 显示书籍列表
- ✅ 阅读按钮存在
- ✅ 导出按钮存在

#### TestReaderView

- ✅ 阅读器页面加载
- ✅ 显示书籍内容
- ✅ 侧边栏存在
- ✅ 目录显示
- ✅ JavaScript spineMap 生成
- ✅ 导出菜单存在

#### TestNavigation

- ✅ 重定向到第一章
- ✅ 下一页按钮
- ✅ 上一页按钮（首章禁用）
- ✅ 章节导航
- ✅ 无效章节返回 404
- ✅ 无效书籍返回 404

#### TestImageServing

- ✅ 图片路由工作
- ✅ 正确的 Content-Type
- ✅ 不存在的图片返回 404

### test_export.py

#### TestMarkdownExport

- ✅ 单文件导出端点
- ✅ 导出内容完整
- ✅ YAML frontmatter
- ✅ 目录包含
- ✅ 图片 base64 嵌入
- ✅ 章节导出端点
- ✅ ZIP 文件有效性
- ✅ README.md 存在
- ✅ 多个章节文件
- ✅ 无效模式参数

#### TestPDFExport

- ✅ PDF 导出端点
- ✅ PDF 内容完整
- ✅ PDF 格式有效
- ✅ 正确的下载头

#### TestExportErrors

- ✅ 不存在的书籍返回 404
- ✅ 无效格式处理

#### TestExportFilenames

- ✅ Markdown 文件名清理
- ✅ PDF 文件名清理
- ✅ ZIP 文件名清理

#### TestExportIntegration

- ✅ 同一本书多种格式导出
- ✅ 不同书籍导出

### test_image_processor.py

#### TestImageProcessor

- ✅ 初始化
- ✅ MIME 类型检测（JPG, PNG, GIF）
- ✅ Base64 data URI 格式
- ✅ 缓存机制
- ✅ 不存在的图片处理
- ✅ Base64 编码有效性

### test_export_service.py

#### TestFilenameSanitization

- ✅ 移除特殊字符
- ✅ 替换空格
- ✅ 长度限制
- ✅ 空字符串处理
- ✅ 保留有效字符

#### TestBookLoading

- ✅ 加载现有书籍
- ✅ 不存在的书籍抛出错误
- ✅ 元数据存在
- ✅ Spine 存在
- ✅ TOC 存在

#### TestExportBook

- ✅ Markdown 单文件导出
- ✅ Markdown 章节导出
- ✅ PDF 导出
- ✅ 不存在的书籍错误
- ✅ 无效格式错误
- ✅ 创建导出目录

## 前置条件

测试需要以下条件：

1. **测试数据**：至少有一本已处理的书籍在 `books/` 目录

   - 默认使用：`学会提问（原书第12版）_data`
   - 备用书籍：`关键跃升：新任管理者成事的底层逻辑_data`

2. **环境变量**：macOS 上需要设置 `DYLD_LIBRARY_PATH`

   ```bash
   export DYLD_LIBRARY_PATH=/opt/homebrew/lib
   ```

3. **依赖库**：确保所有依赖已安装
   ```bash
   pip install -r requirements.txt
   ```

## 持续集成

可以将测试集成到 CI/CD 流程中：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -r requirements.txt
      - name: Run tests
        run: pytest backend/tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 故障排查

### 测试失败：找不到书籍

确保 `books/` 目录中有测试书籍：

```bash
ls books/学会提问（原书第12版）_data/book.pkl
```

如果没有，运行：

```bash
python -m backend.cli epubs/学会提问（原书第12版）.epub
```

### 测试失败：WeasyPrint 错误

确保设置了环境变量：

```bash
export DYLD_LIBRARY_PATH=/opt/homebrew/lib
pytest backend/tests/
```

### 测试失败：导入错误

确保从项目根目录运行测试：

```bash
cd /path/to/reader3
pytest backend/tests/
```

## 添加新测试

### 测试命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 示例测试

```python
def test_my_feature(client, test_book_id):
    """Test description."""
    response = client.get(f"/my-endpoint/{test_book_id}")
    assert response.status_code == 200
    assert "expected content" in response.text
```

### 使用 Fixtures

```python
@pytest.fixture
def my_fixture():
    """Fixture description."""
    # Setup
    data = create_test_data()
    yield data
    # Teardown
    cleanup_test_data(data)
```

## 测试最佳实践

1. **独立性**：每个测试应该独立运行
2. **可重复性**：测试结果应该一致
3. **清晰性**：测试名称应该描述测试内容
4. **快速性**：测试应该快速执行
5. **覆盖性**：测试应该覆盖主要功能和边界情况

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
