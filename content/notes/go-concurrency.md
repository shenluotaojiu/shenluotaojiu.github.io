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

Goroutine 是 Go 的轻量级线程，由 Go 运行时管理。

```go
// 启动一个 goroutine
go func() {
    fmt.Println("Hello from goroutine")
}()
```

### 特点

- 轻量级：初始栈只有 2KB
- 由 Go 运行时调度，而非操作系统
- 可以轻松创建成千上万个 goroutine

## Channel

Channel 是 goroutine 之间通信的管道。

```go
// 创建 channel
ch := make(chan int)      // 无缓冲
ch := make(chan int, 10)  // 有缓冲

// 发送和接收
ch <- 42    // 发送
val := <-ch // 接收
```

### Channel 类型

| 类型   | 语法       | 说明         |
| ------ | ---------- | ------------ |
| 双向   | `chan T`   | 可发送可接收 |
| 只发送 | `chan<- T` | 只能发送     |
| 只接收 | `<-chan T` | 只能接收     |

## Select 语句

`select` 用于同时等待多个 channel 操作。

```go
select {
case msg1 := <-ch1:
    fmt.Println("Received from ch1:", msg1)
case msg2 := <-ch2:
    fmt.Println("Received from ch2:", msg2)
case ch3 <- 42:
    fmt.Println("Sent to ch3")
default:
    fmt.Println("No communication")
}
```

## 常用并发模式

### Worker Pool

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("Worker %d processing job %d\n", id, j)
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动 3 个 worker
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    // 发送 5 个任务
    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)

    // 收集结果
    for a := 1; a <= 5; a++ {
        <-results
    }
}
```

### Context 控制

```go
func doWork(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            fmt.Println("Work cancelled")
            return
        default:
            // 执行工作
        }
    }
}

func main() {
    ctx, cancel := context.WithTimeout(
        context.Background(), 
        5*time.Second,
    )
    defer cancel()
    
    go doWork(ctx)
    
    // 等待或提前取消
    time.Sleep(2 * time.Second)
    cancel()
}
```

## 注意事项

> 不要通过共享内存来通信，而要通过通信来共享内存。

- 避免 goroutine 泄露
- 使用 `sync.WaitGroup` 等待 goroutine 完成
- 使用 `sync.Mutex` 保护共享数据
- 使用 `-race` 检测数据竞争

---

*持续更新中...*
