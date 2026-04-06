// ====================
// Main JavaScript
// ====================

document.addEventListener('DOMContentLoaded', function() {
    initTypingEffect();
    initBackToTop();
    initCategoryToggle();
});

// ====================
// Typing Effect (Home Page)
// ====================
function initTypingEffect() {
    const typingElement = document.querySelector('.typed-text');
    if (!typingElement) return;

    const texts = [
        'std::cout << "Hello World";',
        '欲买桂花同载酒，终不似，少年游',
        '广告位招租'
    ];

    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 80;

    function type() {
        const currentText = texts[textIndex];

        if (isDeleting) {
            typingElement.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
            typingSpeed = 40;
        } else {
            typingElement.textContent = currentText.substring(0, charIndex + 1);
            charIndex++;
            typingSpeed = 80;
        }

        if (!isDeleting && charIndex === currentText.length) {
            isDeleting = true;
            typingSpeed = 2000;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            textIndex = (textIndex + 1) % texts.length;
            typingSpeed = 500;
        }

        setTimeout(type, typingSpeed);
    }

    type();
}

// ====================
// Back to Top
// ====================
function initBackToTop() {
    const backToTop = document.getElementById('backToTop');
    if (!backToTop) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ====================
// Category Toggle (Blog/Notes List and Sidebar)
// ====================
function initCategoryToggle() {
    // 通用的折叠处理函数
    function setupToggle(elements) {
        elements.forEach(titleEl => {
            const targetId = titleEl.getAttribute('data-toggle');
            const targetEl = document.getElementById(targetId);
            if (!targetEl) return;
            
            // 初始化高度
            targetEl.style.maxHeight = targetEl.scrollHeight + 'px';
            
            titleEl.addEventListener('click', () => {
                const isCollapsed = titleEl.classList.contains('collapsed');
                
                if (isCollapsed) {
                    // 展开
                    titleEl.classList.remove('collapsed');
                    targetEl.classList.remove('collapsed');
                    targetEl.style.maxHeight = targetEl.scrollHeight + 'px';
                } else {
                    // 折叠
                    titleEl.classList.add('collapsed');
                    targetEl.classList.add('collapsed');
                    targetEl.style.maxHeight = '0px';
                }
            });
        });
    }
    
    // 博客/笔记列表页的分类折叠
    setupToggle(document.querySelectorAll('.post-category-title[data-toggle]'));
    
    // 笔记详情页左侧栏分类折叠
    setupToggle(document.querySelectorAll('.sidebar-category[data-toggle]'));
}

// ====================
// Word Count & Reading Time
// ====================
class ArticleStats {
    constructor() {
        // 阅读速度：中文约 300-500 字/分钟，英文约 200-250 词/分钟
        this.chineseReadingSpeed = 400; // 字/分钟
        this.englishReadingSpeed = 200; // 词/分钟
    }

    /**
     * 计算文本字数
     * @param {string} text - 原始文本
     * @returns {object} - { chinese, english, total }
     */
    countWords(text) {
        // 移除 Markdown 语法
        let cleanText = this.stripMarkdown(text);

        // 统计中文字符（包括中文标点）
        const chineseChars = cleanText.match(/[\u4e00-\u9fa5]/g) || [];
        const chineseCount = chineseChars.length;

        // 移除中文字符后，统计英文单词
        const textWithoutChinese = cleanText.replace(/[\u4e00-\u9fa5]/g, ' ');
        const englishWords = textWithoutChinese.match(/[a-zA-Z]+/g) || [];
        const englishCount = englishWords.length;

        // 总字数 = 中文字符数 + 英文单词数
        const total = chineseCount + englishCount;

        return {
            chinese: chineseCount,
            english: englishCount,
            total: total
        };
    }

    /**
     * 移除 Markdown 语法
     */
    stripMarkdown(text) {
        return text
            // 移除代码块
            .replace(/```[\s\S]*?```/g, '')
            // 移除行内代码
            .replace(/`[^`]+`/g, '')
            // 移除链接
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
            // 移除图片
            .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
            // 移除标题符号
            .replace(/^#{1,6}\s+/gm, '')
            // 移除粗体/斜体
            .replace(/\*\*\*(.*?)\*\*\*/g, '$1')
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\*(.*?)\*/g, '$1')
            .replace(/___(.*?)___/g, '$1')
            .replace(/__(.*?)__/g, '$1')
            .replace(/_(.*?)_/g, '$1')
            // 移除删除线
            .replace(/~~(.*?)~~/g, '$1')
            // 移除引用
            .replace(/^>\s+/gm, '')
            // 移除列表标记
            .replace(/^[\*\-\+]\s+/gm, '')
            .replace(/^\d+\.\s+/gm, '')
            // 移除分割线
            .replace(/^---$/gm, '')
            .replace(/^\*\*\*$/gm, '')
            // 移除表格分隔符行
            .replace(/^\|[\-\|: ]+\|$/gm, '')
            // 移除表格边框
            .replace(/\|/g, ' ')
            // 清理多余空格
            .replace(/\s+/g, ' ')
            .trim();
    }

    /**
     * 计算预计阅读时间
     * @param {string} text - 原始文本
     * @returns {number} - 阅读时间（分钟）
     */
    calculateReadingTime(text) {
        const words = this.countWords(text);

        // 分别计算中英文阅读时间
        const chineseTime = words.chinese / this.chineseReadingSpeed;
        const englishTime = words.english / this.englishReadingSpeed;

        // 总时间，向上取整，最少 1 分钟
        const totalTime = Math.ceil(chineseTime + englishTime);
        return Math.max(1, totalTime);
    }

    /**
     * 格式化字数显示
     */
    formatWordCount(count) {
        if (count >= 10000) {
            return (count / 10000).toFixed(1) + ' 万字';
        } else if (count >= 1000) {
            return (count / 1000).toFixed(1) + 'k 字';
        }
        return count + ' 字';
    }

    /**
     * 格式化阅读时间显示
     */
    formatReadingTime(minutes) {
        if (minutes >= 60) {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return hours + ' 小时' + (mins > 0 ? ' ' + mins + ' 分钟' : '');
        }
        return minutes + ' 分钟';
    }
}

// 全局实例
const articleStats = new ArticleStats();

/**
 * 更新文章页面的统计信息
 * @param {string} contentElementId - 包含 Markdown 内容的元素 ID
 */
function updateArticleStats(contentElementId) {
    const contentElement = document.getElementById(contentElementId);
    if (!contentElement) return;

    const text = contentElement.textContent || contentElement.innerText;
    const words = articleStats.countWords(text);
    const readingTime = articleStats.calculateReadingTime(text);

    // 更新字数显示
    const wordCountEl = document.getElementById('word-count');
    if (wordCountEl) {
        wordCountEl.textContent = articleStats.formatWordCount(words.total);
    }

    // 更新阅读时间显示
    const readingTimeEl = document.getElementById('reading-time');
    if (readingTimeEl) {
        readingTimeEl.textContent = articleStats.formatReadingTime(readingTime);
    }

    return { words, readingTime };
}

// ====================
// Posts List Loader
// ====================
class PostsLoader {
    constructor() {
        this.postsData = null;
    }

    /**
     * 加载文章配置
     */
    async loadConfig() {
        if (this.postsData) return this.postsData;

        try {
            const response = await fetch('data/posts.json');
            this.postsData = await response.json();
            return this.postsData;
        } catch (error) {
            console.error('Failed to load posts config:', error);
            return null;
        }
    }

    /**
     * 渲染博客列表
     */
    async renderBlogList(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const data = await this.loadConfig();
        if (!data || !data.blog) return;

        let html = '';
        for (const [category, info] of Object.entries(data.blog)) {
            const posts = info.posts || [];
            if (posts.length === 0) continue;

            html += this.renderSection(category, info, posts, 'posts');
        }

        container.innerHTML = html;
    }

    /**
     * 渲染笔记列表
     */
    async renderNotesList(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const data = await this.loadConfig();
        if (!data || !data.notes) return;

        let html = '';
        for (const [category, info] of Object.entries(data.notes)) {
            const posts = info.posts || [];
            if (posts.length === 0) continue;

            html += this.renderSection(category, info, posts, 'notes');
        }

        container.innerHTML = html;
    }

    /**
     * 渲染一个分类区块
     */
    renderSection(category, info, posts, folder) {
        const iconStyle = info.color ? `style="background: ${info.color};"` : '';

        let itemsHtml = posts.map(post => `
            <a href="${folder}/${post.id}.html" class="content-item">
                <i class="fas fa-file-${folder === 'notes' ? 'code' : 'alt'} item-icon"></i>
                <span class="item-title">${post.title}</span>
                <span class="item-date">${post.date}</span>
            </a>
        `).join('');

        return `
            <section class="content-section">
                <div class="section-header">
                    <span class="section-icon" ${iconStyle}></span>
                    <h2 class="section-title">${category}</h2>
                    <span class="section-count">${posts.length} 篇</span>
                </div>
                <div class="content-list">
                    ${itemsHtml}
                </div>
            </section>
        `;
    }
}

// 全局实例
const postsLoader = new PostsLoader();

// ====================
// Markdown Renderer
// ====================
class MarkdownRenderer {
    constructor() {
        this.rules = [
            // Headers
            { pattern: /^### (.*$)/gm, replacement: '<h3>$1</h3>' },
            { pattern: /^## (.*$)/gm, replacement: '<h2>$1</h2>' },
            { pattern: /^# (.*$)/gm, replacement: '<h1>$1</h1>' },

            // Bold and Italic
            { pattern: /\*\*\*(.*?)\*\*\*/g, replacement: '<strong><em>$1</em></strong>' },
            { pattern: /\*\*(.*?)\*\*/g, replacement: '<strong>$1</strong>' },
            { pattern: /\*(.*?)\*/g, replacement: '<em>$1</em>' },
            { pattern: /\_\_\_(.*?)\_\_\_/g, replacement: '<strong><em>$1</em></strong>' },
            { pattern: /\_\_(.*?)\_\_/g, replacement: '<strong>$1</strong>' },
            { pattern: /\_(.*?)\_/g, replacement: '<em>$1</em>' },

            // Strikethrough
            { pattern: /~~(.*?)~~/g, replacement: '<del>$1</del>' },

            // Inline code
            { pattern: /`([^`]+)`/g, replacement: '<code>$1</code>' },

            // Links
            { pattern: /\[([^\]]+)\]\(([^)]+)\)/g, replacement: '<a href="$2" target="_blank">$1</a>' },

            // Images
            { pattern: /!\[([^\]]*)\]\(([^)]+)\)/g, replacement: '<img src="$2" alt="$1">' },

            // Horizontal rule
            { pattern: /^---$/gm, replacement: '<hr>' },
            { pattern: /^\*\*\*$/gm, replacement: '<hr>' },

            // Line breaks
            { pattern: /\n\n/g, replacement: '</p><p>' },
        ];
    }

    render(markdown) {
        let html = markdown;

        // Process code blocks first
        html = this.processCodeBlocks(html);

        // Process blockquotes
        html = this.processBlockquotes(html);

        // Process lists
        html = this.processLists(html);

        // Process tables
        html = this.processTables(html);

        // Apply inline rules
        for (const rule of this.rules) {
            html = html.replace(rule.pattern, rule.replacement);
        }

        // Wrap in paragraph tags
        html = '<p>' + html + '</p>';

        // Clean up empty paragraphs
        html = html.replace(/<p>\s*<\/p>/g, '');
        html = html.replace(/<p>\s*(<h[1-6]>)/g, '$1');
        html = html.replace(/(<\/h[1-6]>)\s*<\/p>/g, '$1');
        html = html.replace(/<p>\s*(<pre>)/g, '$1');
        html = html.replace(/(<\/pre>)\s*<\/p>/g, '$1');
        html = html.replace(/<p>\s*(<ul>)/g, '$1');
        html = html.replace(/(<\/ul>)\s*<\/p>/g, '$1');
        html = html.replace(/<p>\s*(<ol>)/g, '$1');
        html = html.replace(/(<\/ol>)\s*<\/p>/g, '$1');
        html = html.replace(/<p>\s*(<blockquote>)/g, '$1');
        html = html.replace(/(<\/blockquote>)\s*<\/p>/g, '$1');
        html = html.replace(/<p>\s*(<table>)/g, '$1');
        html = html.replace(/(<\/table>)\s*<\/p>/g, '$1');
        html = html.replace(/<p>\s*(<hr>)/g, '$1');
        html = html.replace(/(<hr>)\s*<\/p>/g, '$1');

        return html;
    }

    processCodeBlocks(text) {
        // Fenced code blocks with language
        const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
        return text.replace(codeBlockRegex, (_match, lang, code) => {
            const escapedCode = this.escapeHtml(code.trim());
            const langClass = lang ? ` class="language-${lang}"` : '';
            return `<pre><code${langClass}>${escapedCode}</code></pre>`;
        });
    }

    processBlockquotes(text) {
        const lines = text.split('\n');
        let inBlockquote = false;
        let result = [];
        let blockquoteContent = [];

        for (const line of lines) {
            if (line.startsWith('> ')) {
                if (!inBlockquote) {
                    inBlockquote = true;
                    blockquoteContent = [];
                }
                blockquoteContent.push(line.substring(2));
            } else {
                if (inBlockquote) {
                    result.push('<blockquote>' + blockquoteContent.join('<br>') + '</blockquote>');
                    inBlockquote = false;
                    blockquoteContent = [];
                }
                result.push(line);
            }
        }

        if (inBlockquote) {
            result.push('<blockquote>' + blockquoteContent.join('<br>') + '</blockquote>');
        }

        return result.join('\n');
    }

    processLists(text) {
        // Unordered lists
        text = text.replace(/(?:^|\n)((?:[\*\-\+] .+\n?)+)/g, (_match, list) => {
            const items = list.trim().split('\n').map(item => {
                return '<li>' + item.replace(/^[\*\-\+] /, '') + '</li>';
            }).join('');
            return '\n<ul>' + items + '</ul>\n';
        });

        // Ordered lists
        text = text.replace(/(?:^|\n)((?:\d+\. .+\n?)+)/g, (_match, list) => {
            const items = list.trim().split('\n').map(item => {
                return '<li>' + item.replace(/^\d+\. /, '') + '</li>';
            }).join('');
            return '\n<ol>' + items + '</ol>\n';
        });

        return text;
    }

    processTables(text) {
        const tableRegex = /(?:^|\n)(\|.+\|\n\|[\-\|: ]+\|\n(?:\|.+\|\n?)+)/g;

        return text.replace(tableRegex, (_match, table) => {
            const rows = table.trim().split('\n');
            let html = '<table>';

            rows.forEach((row, index) => {
                if (index === 1) return; // Skip separator row

                const cells = row.split('|').filter(cell => cell.trim());
                const tag = index === 0 ? 'th' : 'td';

                html += '<tr>';
                cells.forEach(cell => {
                    html += `<${tag}>${cell.trim()}</${tag}>`;
                });
                html += '</tr>';
            });

            html += '</table>';
            return '\n' + html + '\n';
        });
    }

    escapeHtml(text) {
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, char => escapeMap[char]);
    }
}

// Global markdown renderer instance
const markdownRenderer = new MarkdownRenderer();

// Function to render markdown content in an element
function renderMarkdown(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const markdown = element.textContent;
    element.innerHTML = markdownRenderer.render(markdown);
}

// Export for use in other files
window.markdownRenderer = markdownRenderer;
window.renderMarkdown = renderMarkdown;
window.articleStats = articleStats;
window.updateArticleStats = updateArticleStats;
window.postsLoader = postsLoader;
