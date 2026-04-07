---
title: 数据结构学习笔记
created: 2026-04-05
updated: 2026-04-07
category: 编程语言
tags:
  - 数据结构
  - 算法
type: note
---

数据结构是计算机科学的基础。

## 线性结构

按顺序存储的数据结构。

### 数组

固定大小的连续内存。

#### 特点

- 随机访问 O(1)
- 插入删除 O(n)
- 内存连续

#### 实现

```go
arr := [5]int{1, 2, 3, 4, 5}
slice := []int{1, 2, 3}
```

### 链表

节点通过指针连接。

#### 单链表

```go
type Node struct {
    Value int
    Next  *Node
}
```

#### 双链表

```go
type DNode struct {
    Value int
    Prev  *DNode
    Next  *DNode
}
```

### 栈

后进先出（LIFO）。

```go
type Stack struct {
    items []int
}

func (s *Stack) Push(item int) {
    s.items = append(s.items, item)
}

func (s *Stack) Pop() int {
    n := len(s.items)
    item := s.items[n-1]
    s.items = s.items[:n-1]
    return item
}
```

### 队列

先进先出（FIFO）。

#### 普通队列

```go
type Queue struct {
    items []int
}
```

#### 优先队列

按优先级出队。

## 树形结构

层次化的数据结构。

### 二叉树

每个节点最多两个子节点。

```go
type TreeNode struct {
    Value int
    Left  *TreeNode
    Right *TreeNode
}
```

#### 遍历方式

- 前序遍历：根-左-右
- 中序遍历：左-根-右
- 后序遍历：左-右-根
- 层序遍历：按层从上到下

### 二叉搜索树

左子树 < 根 < 右子树。

### 平衡二叉树

#### AVL 树

严格平衡，高度差不超过 1。

#### 红黑树

宽松平衡，查询性能稍差但插入删除更快。

### B 树

用于数据库索引。

## 图结构

节点和边组成的网络。

### 表示方法

#### 邻接矩阵

```go
graph := [][]int{
    {0, 1, 0},
    {1, 0, 1},
    {0, 1, 0},
}
```

#### 邻接表

```go
graph := map[int][]int{
    0: {1},
    1: {0, 2},
    2: {1},
}
```

### 遍历算法

#### DFS 深度优先

```go
func dfs(node int, visited map[int]bool, graph map[int][]int) {
    if visited[node] {
        return
    }
    visited[node] = true
    for _, neighbor := range graph[node] {
        dfs(neighbor, visited, graph)
    }
}
```

#### BFS 广度优先

```go
func bfs(start int, graph map[int][]int) {
    queue := []int{start}
    visited := map[int]bool{start: true}
    
    for len(queue) > 0 {
        node := queue[0]
        queue = queue[1:]
        for _, neighbor := range graph[node] {
            if !visited[neighbor] {
                visited[neighbor] = true
                queue = append(queue, neighbor)
            }
        }
    }
}
```

## 哈希表

键值对存储，O(1) 查找。

### 实现原理

- 哈希函数
- 冲突解决（链地址法、开放寻址法）

### 使用场景

- 缓存
- 去重
- 计数

## 总结

掌握数据结构是编程的基础，不同场景选择合适的数据结构。
