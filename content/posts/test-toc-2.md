---
title: Web 开发完全指南
created: 2026-04-06
updated: 2026-04-07
category: 前端开发
tags:
  - Web
  - 前端
  - 后端
type: post
---

全面介绍 Web 开发的各个方面。

## 前端基础

前端是用户直接看到和交互的部分。

### HTML

HTML 是网页的骨架。

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello World</title>
</head>
<body>
    <h1>欢迎</h1>
</body>
</html>
```

### CSS

CSS 负责样式和布局。

#### 选择器

```css
.class-name { }
#id-name { }
element { }
```

#### Flexbox

现代布局利器：

```css
.container {
    display: flex;
    justify-content: center;
    align-items: center;
}
```

#### Grid

更强大的网格系统：

```css
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}
```

### JavaScript

为网页添加交互性。

#### 变量和类型

```javascript
const name = "Alice";
let age = 25;
const isStudent = true;
```

#### 函数

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}

const arrow = (x) => x * 2;
```

#### 异步编程

```javascript
async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
}
```

## 后端开发

后端处理业务逻辑和数据存储。

### 服务器框架

#### Node.js + Express

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('Hello World!');
});

app.listen(3000);
```

#### Go + Gin

```go
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello"})
    })
    r.Run()
}
```

### 数据库

#### SQL 数据库

- PostgreSQL
- MySQL
- SQLite

#### NoSQL 数据库

- MongoDB
- Redis
- Cassandra

## 部署和运维

### Docker

容器化你的应用：

```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
```

### CI/CD

自动化部署流程。

## 安全性

### 常见攻击

- XSS
- CSRF
- SQL 注入

### 防护措施

- 输入验证
- HTTPS
- 安全 Headers

## 结语

Web 开发是一个不断演进的领域，持续学习很重要。
