#!/bin/bash
# 博客发布脚本
# 用法: ./publish.sh [watch]

cd "$(dirname "$0")"

echo "📝 神洛桃玖博客发布系统"
echo "========================"

if [ "$1" = "watch" ]; then
    echo "🔄 启动监听模式..."
    python3 build.py --watch
elif [ "$1" = "serve" ]; then
    echo "🌐 启动本地服务器..."
    python3 build.py
    echo ""
    echo "📡 服务器运行在: http://localhost:8888"
    python3 -m http.server 8888
elif [ "$1" = "dev" ]; then
    echo "🔧 开发模式 (构建 + 服务器)..."
    python3 build.py
    echo ""
    echo "📡 服务器运行在: http://localhost:8888"
    echo "📂 修改 content/ 目录下的 Markdown 文件后，重新运行此脚本"
    python3 -m http.server 8888
else
    echo "🔨 构建中..."
    python3 build.py
    echo ""
    echo "用法:"
    echo "  ./publish.sh         # 一次性构建"
    echo "  ./publish.sh watch   # 监听模式，自动重新构建"
    echo "  ./publish.sh serve   # 构建并启动本地服务器"
    echo "  ./publish.sh dev     # 开发模式 (构建+服务器)"
fi
