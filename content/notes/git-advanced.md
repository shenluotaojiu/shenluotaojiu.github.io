---
title: Git 进阶技巧
created: 2026-04-01
updated: 2026-04-05
category: 工具使用
tags:
  - Git
  - 版本控制
type: note
---

掌握 Git 进阶技巧，提升开发效率。

## 分支管理

### 分支策略

#### Git Flow

标准的分支模型：
- main：生产分支
- develop：开发分支
- feature/*：功能分支
- release/*：发布分支
- hotfix/*：热修复分支

#### GitHub Flow

简化的分支模型：
- main：主分支
- feature：功能分支

### 合并策略

#### Merge

```bash
git checkout main
git merge feature/new-feature
```

#### Rebase

```bash
git checkout feature/new-feature
git rebase main
```

#### Squash

```bash
git merge --squash feature/new-feature
```

## 高级命令

### Interactive Rebase

整理提交历史：

```bash
git rebase -i HEAD~5
```

可用操作：
- pick：保留提交
- reword：修改提交信息
- squash：合并到上一个提交
- drop：删除提交

### Cherry-pick

选择性合并提交：

```bash
git cherry-pick abc123
git cherry-pick abc123..def456
```

### Stash

暂存工作区：

```bash
# 暂存
git stash
git stash save "work in progress"

# 查看
git stash list

# 恢复
git stash pop
git stash apply stash@{1}
```

### Bisect

二分查找问题提交：

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0
# 测试后标记
git bisect good/bad
git bisect reset
```

## 撤销操作

### 撤销工作区

```bash
git checkout -- file.txt
git restore file.txt
```

### 撤销暂存区

```bash
git reset HEAD file.txt
git restore --staged file.txt
```

### 撤销提交

```bash
# 软重置（保留更改）
git reset --soft HEAD~1

# 硬重置（丢弃更改）
git reset --hard HEAD~1

# 创建撤销提交
git revert abc123
```

## 远程操作

### 多远程仓库

```bash
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git merge upstream/main
```

### 推送技巧

```bash
# 强制推送（慎用）
git push --force-with-lease

# 推送标签
git push --tags
```

## 子模块

### 添加子模块

```bash
git submodule add https://github.com/lib/lib.git libs/lib
```

### 更新子模块

```bash
git submodule update --init --recursive
```

## Git Hooks

### 常用钩子

- pre-commit：提交前检查
- commit-msg：检查提交信息
- pre-push：推送前检查

### 示例

```bash
#!/bin/sh
# .git/hooks/pre-commit
npm run lint
npm run test
```

## 配置优化

### 常用别名

```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.lg "log --oneline --graph"
```

### 其他配置

```bash
git config --global pull.rebase true
git config --global push.default current
```

## 总结

熟练使用 Git 进阶功能可以大大提升团队协作效率。
