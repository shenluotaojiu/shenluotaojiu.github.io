---
title: 前端性能优化实战
created: 2026-04-01
updated: 2026-04-05
category: 技术分享
tags:
  - 前端
  - 性能优化
type: post
---

前端性能优化是提升用户体验的关键，本文介绍几种常用的优化技巧。

## 加载性能

### 资源压缩

- 使用 Gzip/Brotli 压缩
- 压缩 JavaScript 和 CSS
- 压缩图片资源

```nginx
# Nginx 配置 Gzip
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 懒加载

```javascript
// 图片懒加载
const img = document.querySelector('img[data-src]');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            observer.unobserve(img);
        }
    });
});
observer.observe(img);
```

### 预加载关键资源

```html
<link rel="preload" href="critical.css" as="style">
<link rel="preload" href="main.js" as="script">
<link rel="preconnect" href="https://api.example.com">
```

## 渲染性能

### 避免强制同步布局

```javascript
// Bad - 强制同步布局
for (let i = 0; i < elements.length; i++) {
    elements[i].style.width = box.offsetWidth + 'px';
}

// Good - 批量读取后批量写入
const width = box.offsetWidth;
for (let i = 0; i < elements.length; i++) {
    elements[i].style.width = width + 'px';
}
```

### 使用 CSS 动画

```css
/* Good - 使用 transform 和 opacity */
.animate {
    transition: transform 0.3s ease;
}
.animate:hover {
    transform: translateX(10px);
}

/* Bad - 触发重排的属性 */
.animate:hover {
    left: 10px;
}
```

### 虚拟列表

对于长列表，只渲染可视区域的元素：

```javascript
class VirtualList {
    constructor(container, itemHeight, totalItems) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.totalItems = totalItems;
        this.visibleCount = Math.ceil(
            container.clientHeight / itemHeight
        );
    }

    render(scrollTop) {
        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = startIndex + this.visibleCount + 1;
        // 只渲染 startIndex 到 endIndex 的元素
    }
}
```

## 缓存策略

### Service Worker

```javascript
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
```

### HTTP 缓存头

```nginx
# 静态资源长期缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 监控与分析

### Web Vitals

关注核心指标：

- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

```javascript
import { getLCP, getFID, getCLS } from 'web-vitals';

getLCP(console.log);
getFID(console.log);
getCLS(console.log);
```

---

*持续更新中...*
