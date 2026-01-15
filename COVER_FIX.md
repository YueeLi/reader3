# 封面显示问题修复

## 问题 1：阅读页面封面未显示 ✅

### 原因

阅读页面（reader.html）没有渲染封面图片

### 解决方案

1. **修改 server.py**：在 `read_chapter` 函数中动态添加封面路径到 book.metadata
2. **修改 reader.html**：在侧边栏顶部添加封面图片展示

### 实现细节

```python
# server.py - 动态添加封面路径
cover_path = None
if os.path.exists(images_dir):
    for cover_name in ["cover.jpeg", "cover.jpg", "cover.png"]:
        potential_cover = os.path.join(images_dir, cover_name)
        if os.path.exists(potential_cover):
            cover_path = f"/books/{book_id}/images/{cover_name}"
            break

book.metadata.cover_path = cover_path
```

```html
<!-- reader.html - 侧边栏显示封面 -->
{% if book.metadata.cover_path %}
<div style="margin-bottom: 20px; text-align: center;">
  <img
    src="{{ book.metadata.cover_path }}"
    alt="{{ book.metadata.title }}"
    style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"
    onerror="this.style.display='none'"
  />
</div>
{% endif %}
```

## 问题 2：Library 封面图被裁剪 ✅

### 原因

使用 `object-fit: cover` 会裁剪图片以填充容器，导致封面上下部分被遮挡

### 解决方案

改用 `object-fit: contain` 保持图片完整显示，不裁剪

### 修改内容

#### 桌面端

```css
.book-cover {
  height: 420px; /* 从 380px 增加到 420px */
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover img {
  object-fit: contain; /* 从 cover 改为 contain */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

#### 移动端

```css
@media (max-width: 768px) {
  .book-cover {
    height: 360px; /* 从 320px 增加到 360px */
  }
}
```

## 效果对比

### 修复前

- ❌ 阅读页面无封面
- ❌ Library 封面被裁剪，看不到完整图片
- ❌ 封面上下部分被遮挡

### 修复后

- ✅ 阅读页面侧边栏显示封面
- ✅ Library 封面完整显示，不裁剪
- ✅ 封面居中对齐，保持原始比例
- ✅ 渐变背景填充空白区域

## 技术要点

1. **object-fit: contain**

   - 保持图片原始宽高比
   - 完整显示图片内容
   - 空白区域显示背景色

2. **object-fit: cover**（旧方案）

   - 填充整个容器
   - 裁剪超出部分
   - 可能丢失重要内容

3. **容器高度优化**

   - 增加高度以更好展示封面
   - 桌面端：420px
   - 移动端：360px

4. **居中对齐**
   - 使用 flexbox 居中
   - 视觉效果更佳

## 测试建议

访问以下页面验证修复：

1. Library 首页：http://127.0.0.1:8123/
2. 任意书籍阅读页：http://127.0.0.1:8123/read/{book_id}/0

检查项：

- [ ] Library 封面完整显示，无裁剪
- [ ] 阅读页面侧边栏显示封面
- [ ] 封面加载失败时优雅降级
- [ ] 移动端封面显示正常
