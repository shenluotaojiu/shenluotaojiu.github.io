#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客发布脚本
用法: python3 build.py [--watch] [--serve]

功能:
1. 扫描 content/ 目录下的所有 Markdown 文件
2. 解析 Front Matter 获取元数据
3. 转换 Markdown 为 HTML
4. 根据模板生成最终 HTML 文件
5. 静态生成 blog.html 和 notes.html
6. 启动本地服务器预览
"""

import os
import re
import json
import argparse
import hashlib
import signal
import socket
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import html

# ==================== 配置 ====================
BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR / "content"
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_POSTS_DIR = BASE_DIR / "posts"
OUTPUT_NOTES_DIR = BASE_DIR / "notes"
DATA_DIR = BASE_DIR / "data"
POSTS_JSON = DATA_DIR / "posts.json"


def get_asset_version() -> str:
    """基于静态资源文件内容生成版本号（只有文件变化时才会改变）"""
    files_to_hash = [
        BASE_DIR / "css" / "style.css",
        BASE_DIR / "js" / "main.js",
    ]
    hasher = hashlib.md5()
    for f in files_to_hash:
        if f.exists():
            hasher.update(f.read_bytes())
    return hasher.hexdigest()[:8]


# 静态资源版本号（基于文件内容哈希）
ASSET_VERSION = get_asset_version()

# 阅读速度配置
CHINESE_READING_SPEED = 400  # 字/分钟
ENGLISH_READING_SPEED = 200  # 词/分钟


# ==================== Front Matter 解析 ====================
def parse_front_matter(content: str) -> Tuple[Dict, str]:
    """解析 Markdown 文件的 Front Matter"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return {}, content
    
    front_matter_text = match.group(1)
    body = match.group(2)
    
    # 简单的 YAML 解析（支持基本格式）
    meta = {}
    current_key = None
    current_list = None
    
    for line in front_matter_text.split('\n'):
        line = line.rstrip()
        
        # 空行跳过
        if not line.strip():
            continue
        
        # 列表项
        if line.startswith('  - '):
            if current_list is not None:
                current_list.append(line.strip()[2:])
            continue
        
        # 键值对
        if ':' in line:
            # 如果之前有列表，保存它
            if current_key and current_list is not None:
                meta[current_key] = current_list
            
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value:
                meta[key] = value
                current_key = None
                current_list = None
            else:
                # 可能是列表的开始
                current_key = key
                current_list = []
    
    # 保存最后一个列表
    if current_key and current_list is not None:
        meta[current_key] = current_list
    
    return meta, body


# ==================== 字数统计 ====================
def strip_markdown(text: str) -> str:
    """移除 Markdown 语法"""
    text = re.sub(r'```[\s\S]*?```', '', text)  # 代码块
    text = re.sub(r'`[^`]+`', '', text)  # 行内代码
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # 链接
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)  # 图片
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # 标题
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)  # 粗斜体
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # 粗体
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # 斜体
    text = re.sub(r'~~(.*?)~~', r'\1', text)  # 删除线
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)  # 引用
    text = re.sub(r'^[\*\-\+]\s+', '', text, flags=re.MULTILINE)  # 无序列表
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # 有序列表
    text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)  # 表格
    text = re.sub(r'^---$', '', text, flags=re.MULTILINE)  # 分割线
    text = re.sub(r'\s+', ' ', text)  # 清理空格
    return text.strip()


def count_words(text: str) -> Tuple[int, int, int]:
    """统计字数：返回 (中文字数, 英文词数, 总字数)"""
    clean_text = strip_markdown(text)
    
    # 中文字符
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]', clean_text)
    chinese_count = len(chinese_chars)
    
    # 英文单词
    text_without_chinese = re.sub(r'[\u4e00-\u9fa5]', ' ', clean_text)
    english_words = re.findall(r'[a-zA-Z]+', text_without_chinese)
    english_count = len(english_words)
    
    total = chinese_count + english_count
    return chinese_count, english_count, total


def calculate_reading_time(text: str) -> int:
    """计算阅读时间（分钟）"""
    chinese, english, _ = count_words(text)
    chinese_time = chinese / CHINESE_READING_SPEED
    english_time = english / ENGLISH_READING_SPEED
    total_time = max(1, round(chinese_time + english_time))
    return total_time


# ==================== Markdown 转 HTML ====================
class MarkdownRenderer:
    """Markdown 转 HTML 渲染器"""
    
    def render(self, markdown: str) -> str:
        """将 Markdown 转换为 HTML"""
        html_content = markdown
        
        # 先提取代码块并用占位符替换，避免代码块内的 # 被误识别为标题
        code_blocks = []
        def save_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2).strip()
            escaped_code = html.escape(code)
            # 添加 language 类名和 data-language 属性用于高亮和显示语言标签
            lang_attr = f' class="language-{lang}" data-language="{lang}"' if lang else ''
            code_html = f'<pre><code{lang_attr}>{escaped_code}</code></pre>'
            code_blocks.append(code_html)
            return f'___CODE_BLOCK_{len(code_blocks) - 1}___'
        
        html_content = re.sub(r'```(\w*)\n([\s\S]*?)```', save_code_block, html_content)
        
        # 处理引用
        html_content = self._process_blockquotes(html_content)
        
        # 处理表格
        html_content = self._process_tables(html_content)
        
        # 处理列表
        html_content = self._process_lists(html_content)
        
        # 处理标题（从 h6 到 h1 顺序处理，避免误匹配）
        html_content = re.sub(r'^###### (.*)$', r'<h6>\1</h6>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^##### (.*)$', r'<h5>\1</h5>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#### (.*)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # 处理粗体和斜体
        html_content = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html_content)
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        
        # 处理删除线
        html_content = re.sub(r'~~(.*?)~~', r'<del>\1</del>', html_content)
        
        # 处理行内代码
        html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
        
        # 处理链接
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html_content)
        
        # 处理图片
        html_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', html_content)
        
        # 处理分割线
        html_content = re.sub(r'^---$', r'<hr>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^\*\*\*$', r'<hr>', html_content, flags=re.MULTILINE)
        
        # 处理段落
        html_content = self._process_paragraphs(html_content)
        
        # 恢复代码块
        for i, code_html in enumerate(code_blocks):
            html_content = html_content.replace(f'___CODE_BLOCK_{i}___', code_html)
        
        return html_content
    
    def _process_code_blocks(self, text: str) -> str:
        """处理代码块"""
        def replace_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2).strip()
            escaped_code = html.escape(code)
            lang_attr = f' class="language-{lang}"' if lang else ''
            return f'<pre><code{lang_attr}>{escaped_code}</code></pre>'
        
        return re.sub(r'```(\w*)\n([\s\S]*?)```', replace_code_block, text)
    
    def _process_blockquotes(self, text: str) -> str:
        """处理引用"""
        lines = text.split('\n')
        result = []
        in_blockquote = False
        blockquote_content = []
        
        for line in lines:
            if line.startswith('> '):
                if not in_blockquote:
                    in_blockquote = True
                    blockquote_content = []
                blockquote_content.append(line[2:])
            else:
                if in_blockquote:
                    result.append('<blockquote>' + '<br>'.join(blockquote_content) + '</blockquote>')
                    in_blockquote = False
                    blockquote_content = []
                result.append(line)
        
        if in_blockquote:
            result.append('<blockquote>' + '<br>'.join(blockquote_content) + '</blockquote>')
        
        return '\n'.join(result)
    
    def _process_tables(self, text: str) -> str:
        """处理表格"""
        def replace_table(match):
            table = match.group(1).strip()
            rows = table.split('\n')
            html_rows = ['<table>']
            
            for i, row in enumerate(rows):
                if i == 1 and re.match(r'^\|[\-\|: ]+\|$', row):
                    continue  # 跳过分隔行
                
                cells = [c.strip() for c in row.split('|') if c.strip()]
                tag = 'th' if i == 0 else 'td'
                html_rows.append('<tr>')
                for cell in cells:
                    html_rows.append(f'<{tag}>{cell}</{tag}>')
                html_rows.append('</tr>')
            
            html_rows.append('</table>')
            return '\n'.join(html_rows)
        
        return re.sub(r'(\|.+\|\n\|[\-\|: ]+\|\n(?:\|.+\|\n?)+)', replace_table, text)
    
    def _process_lists(self, text: str) -> str:
        """处理列表"""
        # 无序列表
        def replace_ul(match):
            items = match.group(0).strip().split('\n')
            html_items = ['<ul>']
            for item in items:
                content = re.sub(r'^[\*\-\+] ', '', item)
                html_items.append(f'<li>{content}</li>')
            html_items.append('</ul>')
            return '\n'.join(html_items) + '\n'
        
        text = re.sub(r'(?:^[\*\-\+] .+\n?)+', replace_ul, text, flags=re.MULTILINE)
        
        # 有序列表
        def replace_ol(match):
            items = match.group(0).strip().split('\n')
            html_items = ['<ol>']
            for item in items:
                content = re.sub(r'^\d+\. ', '', item)
                html_items.append(f'<li>{content}</li>')
            html_items.append('</ol>')
            return '\n'.join(html_items) + '\n'
        
        text = re.sub(r'(?:^\d+\. .+\n?)+', replace_ol, text, flags=re.MULTILINE)
        
        return text
    
    def _process_paragraphs(self, text: str) -> str:
        """处理段落"""
        # 分割成块
        blocks = text.split('\n\n')
        result = []
        
        block_tags = ['<h1', '<h2', '<h3', '<h4', '<h5', '<h6', 
                      '<pre', '<ul', '<ol', '<blockquote', '<table', '<hr']
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            # 检查是否已经是块级元素
            is_block_element = any(block.startswith(tag) for tag in block_tags)
            
            if is_block_element:
                result.append(block)
            else:
                # 将换行转换为 <br>
                block = block.replace('\n', '<br>')
                result.append(f'<p>{block}</p>')
        
        return '\n\n'.join(result)


# ==================== 模板渲染 ====================
def render_template(template_path: Path, context: Dict) -> str:
    """简单的模板渲染"""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 处理 {{#each tags}}...{{/each}}
    each_pattern = r'\{\{#each (\w+)\}\}(.*?)\{\{/each\}\}'
    
    def replace_each(match):
        key = match.group(1)
        inner = match.group(2)
        items = context.get(key, [])
        result = []
        for item in items:
            result.append(inner.replace('{{this}}', str(item)))
        return ''.join(result)
    
    template = re.sub(each_pattern, replace_each, template, flags=re.DOTALL)
    
    # 处理 {{#if key}}...{{/if}}
    if_pattern = r'\{\{#if (\w+)\}\}(.*?)\{\{/if\}\}'
    
    def replace_if(match):
        key = match.group(1)
        inner = match.group(2)
        if context.get(key):
            return inner
        return ''
    
    template = re.sub(if_pattern, replace_if, template, flags=re.DOTALL)
    
    # 处理简单变量 {{key}}
    for key, value in context.items():
        if isinstance(value, str):
            template = template.replace('{{' + key + '}}', value)
        elif isinstance(value, (int, float)):
            template = template.replace('{{' + key + '}}', str(value))
    
    return template


# ==================== 主构建逻辑 ====================
def generate_sidebar_list(articles: List[Dict], current_id: str, article_type: str) -> str:
    """生成左侧文章列表 HTML"""
    # 过滤同类型文章
    same_type = [a for a in articles if a.get('type', 'post') == article_type]
    
    html_parts = []
    
    if article_type == 'note':
        # 笔记页：按分类分组，不显示年份，支持折叠
        by_category = {}
        for article in same_type:
            cat = article.get('category', '其他')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)
        
        # 分类图标映射
        category_icons = {
            '技术分享': 'fa-share-alt',
            '编程语言': 'fa-code',
            '前端开发': 'fa-palette',
            '后端开发': 'fa-server',
            '数据库': 'fa-database',
            '运维部署': 'fa-cloud',
            '工具使用': 'fa-tools',
            '其他': 'fa-folder',
        }
        
        for idx, category in enumerate(sorted(by_category.keys())):
            articles_in_cat = by_category[category]
            icon = category_icons.get(category, 'fa-folder')
            category_id = f'sidebar-cat-{idx}'
            
            # 分类标题（可折叠）
            html_parts.append(
                f'<div class="sidebar-category" data-toggle="{category_id}">'
                f'<i class="fas fa-chevron-down sidebar-cat-arrow"></i>'
                f'<i class="fas {icon}"></i>'
                f'<span>{category}</span>'
                f'<span class="sidebar-cat-count">{len(articles_in_cat)}</span>'
                f'</div>'
            )
            html_parts.append(f'<div class="sidebar-cat-items" id="{category_id}">')
            
            # 按更新时间倒序
            sorted_articles = sorted(articles_in_cat, key=lambda x: x.get('updated') or x.get('created', ''), reverse=True)
            for article in sorted_articles:
                active = ' active' if article['id'] == current_id else ''
                html_parts.append(
                    f'<a href="{article["id"]}.html" class="sidebar-item{active}">{article["title"]}</a>'
                )
            html_parts.append('</div>')
    else:
        # 博客页：按创建时间的年份分组
        by_year = {}
        for article in same_type:
            date = article.get('created', article.get('date', ''))
            year = date[:4] if len(date) >= 4 else '其他'
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(article)
        
        # 按年份倒序
        for year in sorted(by_year.keys(), reverse=True):
            html_parts.append(f'<div class="sidebar-year">{year}</div>')
            # 按创建时间倒序
            articles_in_year = sorted(by_year[year], key=lambda x: x.get('created', ''), reverse=True)
            for article in articles_in_year:
                active = ' active' if article['id'] == current_id else ''
                html_parts.append(
                    f'<a href="{article["id"]}.html" class="sidebar-item{active}">{article["title"]}</a>'
                )
    
    return '\n'.join(html_parts)


def build_article(md_path: Path, md_renderer: MarkdownRenderer, all_articles: List[Dict] = None) -> Optional[Dict]:
    """构建单篇文章"""
    print(f"  处理: {md_path.name}")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析 Front Matter
    meta, body = parse_front_matter(content)
    
    if not meta.get('title'):
        print(f"    ⚠️  跳过: 缺少 title")
        return None
    
    # 统计字数和阅读时间
    _, _, word_count = count_words(body)
    reading_time = calculate_reading_time(body)
    
    # 处理时间：支持 created/updated 或兼容旧的 date
    created = meta.get('created', meta.get('date', ''))
    updated = meta.get('updated', '')
    
    # 确定文章类型和输出目录
    article_type = meta.get('type', 'post')
    if article_type == 'note':
        output_dir = OUTPUT_NOTES_DIR
        back_link = 'notes'
        back_text = '笔记列表'
        is_note = True
        is_blog = False
        sidebar_title = '所有笔记'
    else:
        output_dir = OUTPUT_POSTS_DIR
        back_link = 'blog'
        back_text = '博客列表'
        is_note = False
        is_blog = True
        sidebar_title = '所有文章'
    
    # 生成侧边栏列表
    sidebar_list = ''
    if all_articles:
        sidebar_list = generate_sidebar_list(all_articles, md_path.stem, article_type)
    
    # 渲染 Markdown
    html_content = md_renderer.render(body)
    
    # 渲染模板
    template_path = TEMPLATE_DIR / 'article.html'
    context = {
        'title': meta.get('title', ''),
        'created': created,
        'updated': updated,
        'category': meta.get('category', ''),
        'tags': meta.get('tags', []),
        'wordCount': word_count,
        'readingTime': reading_time,
        'content': html_content,
        'backLink': back_link,
        'backText': back_text,
        'isNote': is_note,
        'isBlog': is_blog,
        'sidebarTitle': sidebar_title,
        'sidebarList': sidebar_list,
        'assetVersion': ASSET_VERSION,
    }
    
    final_html = render_template(template_path, context)
    
    # 输出文件
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{md_path.stem}.html"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"    ✅ 生成: {output_path.name} ({word_count} 字, {reading_time} 分钟)")
    
    # 返回文章信息
    return {
        'id': md_path.stem,
        'title': meta.get('title', ''),
        'created': created,
        'updated': updated,
        'category': meta.get('category', ''),
        'tags': meta.get('tags', []),
        'type': article_type,
        'wordCount': word_count,
        'readingTime': reading_time,
    }


def generate_list_html(articles: List[Dict], page_type: str) -> str:
    """生成文章列表 HTML（简洁时间线样式）"""
    # 过滤对应类型
    if page_type == 'blog':
        filtered = [a for a in articles if a.get('type', 'post') != 'note']
        folder = 'posts'
    else:
        filtered = [a for a in articles if a.get('type', 'post') == 'note']
        folder = 'notes'
    
    # 按更新时间排序（没有 updated 的用 created）
    filtered.sort(key=lambda x: x.get('updated') or x.get('created', ''), reverse=True)
    
    # 按分类分组
    by_category = {}
    for article in filtered:
        cat = article.get('category', '其他')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(article)
    
    # 分类图标映射
    category_icons = {
        '技术分享': 'fa-share-alt',
        '编程语言': 'fa-code',
        '前端开发': 'fa-palette',
        '后端开发': 'fa-server',
        '数据库': 'fa-database',
        '运维部署': 'fa-cloud',
        '其他': 'fa-folder',
    }
    
    html_parts = []
    
    for idx, category in enumerate(sorted(by_category.keys())):
        posts = by_category[category]
        icon = category_icons.get(category, 'fa-folder')
        category_id = f'category-{idx}'
        
        # 分类标题（可折叠）
        html_parts.append(f'''
                <div class="post-category-title" data-toggle="{category_id}">
                    <i class="fas fa-chevron-down category-arrow"></i>
                    <i class="fas {icon}"></i>
                    <span>{category}</span>
                    <span class="category-count">{len(posts)}</span>
                </div>
                <div class="category-posts" id="{category_id}">''')
        
        for post in posts:
            created = post.get('created', '')
            updated = post.get('updated', '')
            
            # 显示更新时间（如果有），否则显示创建时间
            if updated and updated != created:
                date_html = f'<span class="post-date updated"><i class="far fa-edit"></i> {updated}</span>'
            else:
                date_html = f'<span class="post-date"><i class="far fa-calendar"></i> {created}</span>'
            
            # 标签（只显示前2个）
            tags = post.get('tags', [])[:2]
            tags_html = ''.join(f'<span class="post-tag">{tag}</span>' for tag in tags)
            
            html_parts.append(f'''
                    <a href="{folder}/{post['id']}.html" class="post-item">
                        <span class="post-title">{post['title']}</span>
                        <div class="post-meta">
                            {date_html}
                        </div>
                        <div class="post-tags">{tags_html}</div>
                    </a>''')
        
        html_parts.append('                </div>')
    
    return '\n'.join(html_parts)


def build_blog_page(articles: List[Dict]):
    """构建 blog.html"""
    list_html = generate_list_html(articles, 'blog')
    blog_count = len([a for a in articles if a.get('type', 'post') != 'note'])
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>博客 | 神洛桃玖</title>
    <link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="css/fontawesome/all.min.css">
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="index.html" class="nav-logo">
                <img src="pic/pic-1.jpg" alt="神洛桃玖" class="logo-avatar">
                <span class="logo-text">神洛桃玖</span>
            </a>
            <div class="nav-menu">
                <a href="blog.html" class="nav-link active">
                    <i class="fas fa-blog"></i> <span>博客</span>
                </a>
                <a href="notes.html" class="nav-link">
                    <i class="fas fa-book"></i> <span>笔记</span>
                </a>
            </div>
        </div>
    </nav>

    <!-- 页面内容 -->
    <main class="page">
        <div class="page-container">
            <header class="page-header">
                <h1 class="page-title">
                    <i class="fas fa-blog"></i>
                    博客
                </h1>
                <p class="page-desc">// 记录技术思考与实践经验 · 共 {blog_count} 篇</p>
            </header>

            <div class="posts-container">
{list_html}
            </div>
        </div>
    </main>

    <!-- 回到顶部 -->
    <button class="back-to-top" id="backToTop">
        <i class="fas fa-arrow-up"></i>
    </button>

    <script src="js/main.js?v={ASSET_VERSION}"></script>
</body>
</html>'''
    
    with open(BASE_DIR / 'blog.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  ✅ 生成: blog.html ({blog_count} 篇博客)")


def build_notes_page(articles: List[Dict]):
    """构建 notes.html"""
    list_html = generate_list_html(articles, 'notes')
    notes_count = len([a for a in articles if a.get('type', 'post') == 'note'])
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>笔记 | 神洛桃玖</title>
    <link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="css/fontawesome/all.min.css">
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="index.html" class="nav-logo">
                <img src="pic/pic-1.jpg" alt="神洛桃玖" class="logo-avatar">
                <span class="logo-text">神洛桃玖</span>
            </a>
            <div class="nav-menu">
                <a href="blog.html" class="nav-link">
                    <i class="fas fa-blog"></i> <span>博客</span>
                </a>
                <a href="notes.html" class="nav-link active">
                    <i class="fas fa-book"></i> <span>笔记</span>
                </a>
            </div>
        </div>
    </nav>

    <!-- 页面内容 -->
    <main class="page">
        <div class="page-container">
            <header class="page-header">
                <h1 class="page-title">
                    <i class="fas fa-book"></i>
                    笔记
                </h1>
                <p class="page-desc">// 学习笔记与知识整理 · 共 {notes_count} 篇</p>
            </header>

            <div class="posts-container">
{list_html}
            </div>
        </div>
    </main>

    <!-- 回到顶部 -->
    <button class="back-to-top" id="backToTop">
        <i class="fas fa-arrow-up"></i>
    </button>

    <script src="js/main.js?v={ASSET_VERSION}"></script>
</body>
</html>'''
    
    with open(BASE_DIR / 'notes.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  ✅ 生成: notes.html ({notes_count} 篇笔记)")


def build_all():
    """构建所有文章"""
    print("🚀 开始构建...\n")
    
    md_renderer = MarkdownRenderer()
    
    # 第一遍：收集所有文章信息
    articles_info = []
    md_files = list(CONTENT_DIR.rglob('*.md'))
    
    print("📋 收集文章信息...")
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        meta, _ = parse_front_matter(content)
        if meta.get('title'):
            articles_info.append({
                'id': md_file.stem,
                'title': meta.get('title', ''),
                'created': meta.get('created', meta.get('date', '')),
                'updated': meta.get('updated', ''),
                'category': meta.get('category', ''),
                'tags': meta.get('tags', []),
                'type': meta.get('type', 'post'),
                'path': md_file,
            })
    
    # 第二遍：生成 HTML（带有侧边栏列表）
    print("\n📝 生成文章...")
    articles = []
    for md_file in md_files:
        result = build_article(md_file, md_renderer, articles_info)
        if result:
            articles.append(result)
    
    # 生成列表页面
    print("\n📄 生成列表页...")
    build_blog_page(articles)
    build_notes_page(articles)
    
    print(f"\n✨ 构建完成! 共处理 {len(articles)} 篇文章")


def watch_mode():
    """监听模式"""
    try:
        import time
        
        print("👀 监听模式启动，按 Ctrl+C 退出\n")
        
        # 记录文件修改时间
        file_mtimes = {}
        
        while True:
            changed = False
            
            for md_file in CONTENT_DIR.rglob('*.md'):
                mtime = md_file.stat().st_mtime
                if md_file not in file_mtimes or file_mtimes[md_file] != mtime:
                    file_mtimes[md_file] = mtime
                    changed = True
            
            if changed:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检测到变更，重新构建...")
                build_all()
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 监听模式已退出")


# ==================== 服务器功能 ====================
DEFAULT_PORT = 8888


def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_on_port(port: int) -> bool:
    """杀死占用指定端口的进程"""
    try:
        # 使用 lsof 查找占用端口的进程
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().split('\n')
        
        if pids and pids[0]:
            for pid in pids:
                if pid:
                    print(f"  🔄 终止占用端口 {port} 的进程 (PID: {pid})...")
                    os.kill(int(pid), signal.SIGTERM)
            # 等待进程终止
            import time
            time.sleep(0.5)
            return True
    except Exception as e:
        print(f"  ⚠️  无法终止进程: {e}")
    return False


def start_server(port: int = DEFAULT_PORT):
    """启动本地 HTTP 服务器"""
    print(f"\n🌐 启动本地服务器...")
    
    # 检查端口是否被占用
    if is_port_in_use(port):
        print(f"  ⚠️  端口 {port} 已被占用")
        kill_process_on_port(port)
        
        # 再次检查
        if is_port_in_use(port):
            print(f"  ❌ 无法释放端口 {port}，请手动关闭占用进程")
            return
    
    print(f"  📡 服务器运行在: http://localhost:{port}")
    print(f"  按 Ctrl+C 停止服务器\n")
    
    # 切换到项目目录并启动服务器
    os.chdir(BASE_DIR)
    
    try:
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        
        server = HTTPServer(('', port), SimpleHTTPRequestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")


def serve_mode(port: int = DEFAULT_PORT, watch: bool = False):
    """服务器模式（可选同时监听文件变化）"""
    import threading
    
    # 先构建一次
    build_all()
    
    if watch:
        # 在后台线程运行监听
        def watch_thread():
            try:
                import time
                file_mtimes = {}
                
                while True:
                    changed = False
                    
                    for md_file in CONTENT_DIR.rglob('*.md'):
                        mtime = md_file.stat().st_mtime
                        if md_file not in file_mtimes or file_mtimes[md_file] != mtime:
                            file_mtimes[md_file] = mtime
                            changed = True
                    
                    if changed and file_mtimes:  # 跳过首次扫描
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检测到变更，重新构建...")
                        build_all()
                    
                    time.sleep(1)
            except Exception as e:
                print(f"监听线程异常: {e}")
        
        watcher = threading.Thread(target=watch_thread, daemon=True)
        watcher.start()
        print("👀 文件监听已启动")
    
    # 启动服务器（阻塞主线程）
    start_server(port)


def main():
    parser = argparse.ArgumentParser(description='博客构建脚本')
    parser.add_argument('--watch', '-w', action='store_true', help='监听模式')
    parser.add_argument('--serve', '-s', action='store_true', help='启动本地服务器')
    parser.add_argument('--port', '-p', type=int, default=DEFAULT_PORT, help=f'服务器端口 (默认: {DEFAULT_PORT})')
    args = parser.parse_args()
    
    if args.serve:
        serve_mode(args.port, args.watch)
    elif args.watch:
        watch_mode()
    else:
        build_all()


if __name__ == '__main__':
    main()
