---
title: SQL 基础语法笔记
created: 2026-03-25
updated: 2026-04-02
category: 数据库
tags:
  - SQL
  - 数据库
type: note
---

SQL 是操作关系型数据库的标准语言。

## 数据定义 (DDL)

### 创建表

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    age INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 修改表

```sql
-- 添加列
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- 修改列
ALTER TABLE users MODIFY COLUMN phone VARCHAR(30);

-- 删除列
ALTER TABLE users DROP COLUMN phone;

-- 重命名表
RENAME TABLE users TO members;
```

### 删除表

```sql
DROP TABLE IF EXISTS users;
```

### 索引

```sql
-- 创建索引
CREATE INDEX idx_username ON users(username);
CREATE UNIQUE INDEX idx_email ON users(email);

-- 删除索引
DROP INDEX idx_username ON users;
```

## 数据操作 (DML)

### 插入数据

```sql
-- 单行插入
INSERT INTO users (username, email, age)
VALUES ('alice', 'alice@example.com', 25);

-- 多行插入
INSERT INTO users (username, email, age)
VALUES 
    ('bob', 'bob@example.com', 30),
    ('charlie', 'charlie@example.com', 28);
```

### 更新数据

```sql
UPDATE users 
SET age = 26, email = 'newemail@example.com'
WHERE username = 'alice';
```

### 删除数据

```sql
DELETE FROM users WHERE age < 18;

-- 清空表
TRUNCATE TABLE users;
```

## 数据查询 (DQL)

### 基本查询

```sql
-- 查询所有
SELECT * FROM users;

-- 指定列
SELECT username, email FROM users;

-- 去重
SELECT DISTINCT age FROM users;

-- 别名
SELECT username AS name, email AS mail FROM users;
```

### 条件过滤

```sql
-- WHERE 子句
SELECT * FROM users WHERE age > 20;

-- 多条件
SELECT * FROM users WHERE age > 20 AND email LIKE '%@gmail.com';

-- IN 操作符
SELECT * FROM users WHERE age IN (20, 25, 30);

-- BETWEEN
SELECT * FROM users WHERE age BETWEEN 20 AND 30;

-- NULL 判断
SELECT * FROM users WHERE phone IS NULL;
```

### 排序分页

```sql
-- 排序
SELECT * FROM users ORDER BY age DESC, username ASC;

-- 分页
SELECT * FROM users LIMIT 10 OFFSET 20;
-- 或
SELECT * FROM users LIMIT 20, 10;
```

### 聚合函数

```sql
-- 计数
SELECT COUNT(*) FROM users;

-- 求和
SELECT SUM(age) FROM users;

-- 平均值
SELECT AVG(age) FROM users;

-- 最大最小
SELECT MAX(age), MIN(age) FROM users;
```

### 分组查询

```sql
-- GROUP BY
SELECT age, COUNT(*) as count 
FROM users 
GROUP BY age;

-- HAVING
SELECT age, COUNT(*) as count 
FROM users 
GROUP BY age 
HAVING count > 5;
```

## 表连接

### 内连接

```sql
SELECT u.username, o.order_id
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

### 左连接

```sql
SELECT u.username, o.order_id
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

### 右连接

```sql
SELECT u.username, o.order_id
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

### 自连接

```sql
SELECT a.username, b.username AS friend
FROM users a
JOIN friendships f ON a.id = f.user_id
JOIN users b ON f.friend_id = b.id;
```

## 子查询

### WHERE 子查询

```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);
```

### FROM 子查询

```sql
SELECT avg_age
FROM (SELECT AVG(age) as avg_age FROM users) AS subquery;
```

### EXISTS

```sql
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

## 事务

```sql
-- 开始事务
START TRANSACTION;

-- 执行操作
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 提交
COMMIT;

-- 或回滚
ROLLBACK;
```

## 总结

掌握 SQL 基础是后端开发的必备技能。
