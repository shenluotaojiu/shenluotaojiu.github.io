---
title: Linux 常用命令速查
created: 2026-03-28
updated: 2026-04-04
category: 运维部署
tags:
  - Linux
  - Shell
type: note
---

Linux 系统管理必备命令。

## 文件操作

### 基本命令

```bash
# 列出文件
ls -la

# 切换目录
cd /path/to/dir

# 创建目录
mkdir -p dir1/dir2

# 复制
cp -r source dest

# 移动/重命名
mv old new

# 删除
rm -rf dir
```

### 文件查看

```bash
# 查看全部
cat file.txt

# 分页查看
less file.txt

# 查看开头
head -n 20 file.txt

# 查看结尾
tail -f file.txt
```

### 文件搜索

#### find

```bash
# 按名称查找
find /path -name "*.log"

# 按类型查找
find /path -type f

# 按时间查找
find /path -mtime -7

# 按大小查找
find /path -size +100M
```

#### locate

```bash
# 更新数据库
sudo updatedb

# 快速查找
locate filename
```

## 文本处理

### grep

```bash
# 基本搜索
grep "pattern" file.txt

# 递归搜索
grep -r "pattern" /path

# 忽略大小写
grep -i "pattern" file.txt

# 显示行号
grep -n "pattern" file.txt

# 正则表达式
grep -E "regex" file.txt
```

### sed

```bash
# 替换文本
sed 's/old/new/g' file.txt

# 删除行
sed '/pattern/d' file.txt

# 原地修改
sed -i 's/old/new/g' file.txt
```

### awk

```bash
# 打印列
awk '{print $1, $3}' file.txt

# 条件过滤
awk '$3 > 100 {print $0}' file.txt

# 分隔符
awk -F: '{print $1}' /etc/passwd
```

## 系统管理

### 进程管理

```bash
# 查看进程
ps aux
ps -ef | grep nginx

# 实时监控
top
htop

# 终止进程
kill PID
kill -9 PID
killall nginx
```

### 系统信息

```bash
# 系统版本
uname -a
cat /etc/os-release

# 内存使用
free -h

# 磁盘使用
df -h
du -sh /path

# CPU 信息
lscpu
cat /proc/cpuinfo
```

### 服务管理

```bash
# systemd
systemctl start nginx
systemctl stop nginx
systemctl restart nginx
systemctl status nginx
systemctl enable nginx
```

## 网络

### 网络基础命令

```bash
# IP 地址
ip addr
ifconfig

# 路由表
ip route
route -n

# DNS 查询
nslookup domain.com
dig domain.com
```

### 连接测试

```bash
# ping
ping -c 4 google.com

# 端口测试
telnet host 80
nc -zv host 80

# 路由追踪
traceroute host
```

### 网络监控

```bash
# 端口占用
netstat -tlnp
ss -tlnp

# 抓包
tcpdump -i eth0 port 80

# 流量监控
iftop
nethogs
```

## 用户权限

### 用户管理

```bash
# 添加用户
useradd -m username
passwd username

# 删除用户
userdel -r username

# 修改用户
usermod -aG group username
```

### 权限管理

```bash
# 修改权限
chmod 755 file
chmod +x script.sh

# 修改所有者
chown user:group file

# 递归修改
chmod -R 755 dir
chown -R user:group dir
```

## 压缩解压

### tar

```bash
# 压缩
tar -czvf archive.tar.gz dir/

# 解压
tar -xzvf archive.tar.gz

# 查看内容
tar -tzvf archive.tar.gz
```

### 其他格式

```bash
# zip
zip -r archive.zip dir/
unzip archive.zip

# gzip
gzip file
gunzip file.gz
```

## 总结

熟练掌握这些命令是 Linux 运维的基础。
