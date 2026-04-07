---
title: Docker 容器化入门
created: 2026-04-03
updated: 2026-04-06
category: 运维部署
tags:
  - Docker
  - 容器
type: note
---

Docker 是现代应用部署的标准工具。

## 基础概念

### 镜像 (Image)

镜像是只读的模板，包含运行应用所需的一切。

#### 镜像层

Docker 镜像由多层组成：

- 基础层（如 Ubuntu、Alpine）
- 应用层
- 配置层

#### 镜像仓库

常用的镜像仓库：

- Docker Hub
- 阿里云容器镜像服务
- 私有 Registry

### 容器 (Container)

容器是镜像的运行实例。

```bash
# 运行容器
docker run -d --name myapp nginx

# 查看容器
docker ps

# 停止容器
docker stop myapp
```

### 数据卷 (Volume)

数据持久化的解决方案。

#### 绑定挂载

```bash
docker run -v /host/path:/container/path nginx
```

#### 命名卷

```bash
docker volume create mydata
docker run -v mydata:/data nginx
```

## Dockerfile

### 基本指令

```dockerfile
# 基础镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制文件
COPY package*.json ./

# 运行命令
RUN npm install

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["npm", "start"]
```

### 多阶段构建

```dockerfile
# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

## Docker Compose

### 基本配置

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

### 常用命令

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 网络

### 网络类型

- bridge：默认网络
- host：使用主机网络
- none：无网络

### 自定义网络

```bash
docker network create mynet
docker run --network mynet nginx
```

## 最佳实践

### 镜像优化

1. 使用小基础镜像（如 Alpine）
2. 合并 RUN 指令减少层数
3. 使用 .dockerignore

### 安全建议

1. 不使用 root 用户
2. 定期更新基础镜像
3. 扫描镜像漏洞

## 总结

Docker 简化了应用的打包、分发和部署流程。
