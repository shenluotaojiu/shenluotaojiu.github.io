# 神洛桃玖的技术博客

基于 Markdown 的静态博客系统，使用 One Dark 主题。

🔗 **在线预览**: [https://shenluotaojiu.github.io/shenluotaojiu/](https://shenluotaojiu.github.io/shenluotaojiu/)

## 🌐 GitHub Pages 部署

### 自动部署（推荐）

项目已配置 GitHub Actions，推送到 `main` 分支后会自动部署。

**首次设置步骤**：

1. 进入 GitHub 仓库 → **Settings** → **Pages**
2. 在 **Build and deployment** 部分：
   - **Source** 选择 `GitHub Actions`
3. 推送代码到 `master` 分支
4. 等待 Actions 运行完成（约 1-2 分钟）
5. 访问 `https://shenluotaojiu.github.io/shenluotaojiu/`

### 手动部署

如果不想用 Actions，也可以：

1. 在 **Settings** → **Pages** 中：
   - **Source** 选择 `Deploy from a branch`
   - **Branch** 选择 `main` / `/(root)`
2. 保存后等待几分钟即可

## 🚀 快速开始

### 写文章

1. 在 `content/posts/` 目录创建博客文章（`.md` 文件）
2. 在 `content/notes/` 目录创建学习笔记（`.md` 文件）

### 发布

```bash
# 一次性构建
./publish.sh

# 或者使用 Python 直接运行
python3 build.py
```

### 本地预览

```bash
# 构建并启动服务器
./publish.sh serve

# 然后访问 http://localhost:8888
```

## 📁 项目结构

```text
shenluotaojiu/
├── content/                # 📝 Markdown 源文件（只需编辑这里！）
│   ├── posts/              # 博客文章
│   │   ├── go-best-practices.md
│   │   └── frontend-performance.md
│   └── notes/              # 学习笔记
│       └── go-concurrency.md
│
├── templates/              # 📄 HTML 模板
│   └── article.html        # 文章页面模板
│
├── posts/                  # 🔧 生成的博客 HTML（自动生成，勿手动编辑）
├── notes/                  # 🔧 生成的笔记 HTML（自动生成，勿手动编辑）
├── data/                   # 🔧 配置文件（自动生成）
│   └── posts.json          # 文章列表配置
│
├── css/style.css           # 样式文件
├── js/main.js              # JavaScript 功能
├── index.html              # 首页
├── blog.html               # 博客列表
├── notes.html              # 笔记列表
├── skills.html             # 技能页面
│
├── build.py                # 构建脚本
└── publish.sh              # 发布脚本
```

## ✍️ 文章格式

每篇 Markdown 文章需要包含 **Front Matter** 头部信息：

```markdown
---
title: 文章标题
date: 2026-04-07
category: 分类名称
tags:
  - 标签1
  - 标签2
type: post   # post=博客, note=笔记
---

这里是文章正文...

## 二级标题

内容...
```

### Front Matter 字段说明

| 字段     | 必填 | 说明                                              |
| -------- | ---- | ------------------------------------------------- |
| title    | ✅   | 文章标题                                          |
| date     | ✅   | 发布日期，格式：YYYY-MM-DD                        |
| category | ✅   | 分类名称                                          |
| tags     | ❌   | 标签列表                                          |
| type     | ❌   | 类型：`post`（博客）或 `note`（笔记），默认 post  |

### 示例

```markdown
---
title: Go 并发编程笔记
date: 2026-04-02
category: 编程语言
tags:
  - Go
  - 并发
  - Goroutine
type: note
---

Go 语言天生支持并发，通过 goroutine 和 channel 提供了简洁而强大的并发编程模型。

## Goroutine

Goroutine 是 Go 的轻量级线程...
```

## 🛠️ 命令说明

```bash
# 构建（生成 HTML）
./publish.sh

# 监听模式（文件变化时自动重建）
./publish.sh watch

# 构建并启动本地服务器
./publish.sh serve

# 开发模式
./publish.sh dev
```

## ✨ 自动功能

构建脚本会自动：

1. **解析 Front Matter** - 提取标题、日期、分类、标签
2. **统计字数** - 分别统计中文字符和英文单词
3. **计算阅读时间** - 中文 400 字/分钟，英文 200 词/分钟
4. **转换 Markdown** - 支持代码块、表格、列表、引用等
5. **生成 HTML** - 应用模板生成最终页面
6. **更新配置** - 自动更新 `data/posts.json`

## 📌 工作流程

```text
编写 Markdown (content/)
        ↓
   运行 build.py
        ↓
   ┌────┴────┐
   ↓         ↓
生成 HTML   更新 posts.json
(posts/notes/)  (data/)
        ↓
   本地预览 / 部署
```

## 🎨 主题

使用 One Dark 配色方案，模拟代码编辑器风格。

## 📝 添加新文章步骤

1. 在 `content/posts/` 或 `content/notes/` 创建 `.md` 文件
2. 添加 Front Matter 头部信息
3. 编写 Markdown 内容
4. 运行 `./publish.sh`
5. 访问 `http://localhost:8888` 预览

就这么简单！🎉
