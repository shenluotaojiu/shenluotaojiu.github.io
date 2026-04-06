---
title: Go 语言最佳实践指南
created: 2026-04-05
category: 技术分享
tags:
  - Go
  - 最佳实践
type: post
---

Go 语言以其简洁性和高效性著称，本文总结一些实用的最佳实践。

## 代码风格

### 使用 gofmt

始终使用 `gofmt` 格式化代码，保持一致的代码风格。

```bash
gofmt -w .
```

### 命名规范

- 包名：小写单词，避免下划线
- 变量：驼峰命名，首字母大写表示导出
- 接口：单方法接口通常以 `er` 结尾

```go
// Good
type Reader interface {
    Read(p []byte) (n int, err error)
}

// 包级变量
var maxRetries = 3

// 导出变量
var MaxConnections = 100
```

## 错误处理

### 总是检查错误

```go
// Bad
file, _ := os.Open("file.txt")

// Good
file, err := os.Open("file.txt")
if err != nil {
    return fmt.Errorf("failed to open file: %w", err)
}
defer file.Close()
```

### 使用 errors.Is 和 errors.As

```go
if errors.Is(err, os.ErrNotExist) {
    // 处理文件不存在
}

var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println(pathErr.Path)
}
```

## 并发安全

### 使用 sync 包

```go
var (
    mu      sync.RWMutex
    counter int
)

func increment() {
    mu.Lock()
    defer mu.Unlock()
    counter++
}

func getCount() int {
    mu.RLock()
    defer mu.RUnlock()
    return counter
}
```

### 使用 atomic 包

```go
var counter int64

func increment() {
    atomic.AddInt64(&counter, 1)
}
```

## 性能优化

### 预分配切片容量

```go
// Bad - 多次扩容
var result []int
for i := 0; i < 1000; i++ {
    result = append(result, i)
}

// Good - 一次分配
result := make([]int, 0, 1000)
for i := 0; i < 1000; i++ {
    result = append(result, i)
}
```

### 使用 strings.Builder

```go
// Bad
var s string
for i := 0; i < 1000; i++ {
    s += "a"
}

// Good
var sb strings.Builder
for i := 0; i < 1000; i++ {
    sb.WriteString("a")
}
result := sb.String()
```

## 测试

### 表驱动测试

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", 
                    tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

---

*持续更新中...*
