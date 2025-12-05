# GitHub推送指南

## 📋 准备工作

### 1. 检查Git状态

```bash
# 检查是否已初始化git仓库
git status

# 如果未初始化，执行：
git init
```

### 2. 配置Git用户信息（如果未配置）

```bash
# 设置用户名
git config user.name "你的GitHub用户名"

# 设置邮箱
git config user.email "你的GitHub邮箱"
```

---

## 🚀 推送步骤

### 步骤1：添加文件到暂存区

```bash
# 添加所有文件（.gitignore会自动排除不需要的文件）
git add .

# 或者选择性添加
git add README.md
git add 01-项目构想/
git add 02-数字人设计/
git add 03-技术实现/
git add 04-知识库建设/
```

### 步骤2：提交更改

```bash
# 首次提交
git commit -m "初始提交：软件工程事业部AI数字人队伍项目"

# 或者更详细的提交信息
git commit -m "初始提交：软件工程事业部AI数字人队伍项目

- 完成组织架构设计
- 实现9个数字人角色
- 完成智能产品规划师核心功能
- 完成Web界面基础功能
- 完成系统布局和逻辑关系设计"
```

### 步骤3：在GitHub创建仓库

1. 登录GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `ai-digital-human-team` 或 `software-engineering-division`
   - **Description**: `软件工程事业部 - AI数字人队伍管理平台`
   - **Visibility**: Public 或 Private（根据你的需要）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有文件）
4. 点击 "Create repository"

### 步骤4：连接远程仓库并推送

```bash
# 添加远程仓库（替换YOUR_USERNAME和REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 或者使用SSH（如果已配置SSH密钥）
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# 查看远程仓库配置
git remote -v

# 推送代码（首次推送）
git push -u origin main

# 如果默认分支是master，使用：
git push -u origin master
```

---

## 🔧 常见问题解决

### 问题1：分支名称不匹配

如果GitHub仓库默认分支是 `main`，但本地是 `master`：

```bash
# 重命名本地分支
git branch -M main

# 然后推送
git push -u origin main
```

### 问题2：需要强制推送（谨慎使用）

```bash
# 强制推送（会覆盖远程仓库）
git push -u origin main --force
```

### 问题3：认证问题

#### 使用HTTPS（需要Personal Access Token）

1. GitHub设置 → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新token，勾选 `repo` 权限
3. 推送时使用token作为密码

#### 使用SSH（推荐）

```bash
# 检查是否已有SSH密钥
ls -al ~/.ssh

# 如果没有，生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 添加到GitHub: Settings → SSH and GPG keys → New SSH key
```

---

## 📝 后续更新

推送成功后，后续更新代码：

```bash
# 1. 查看更改
git status

# 2. 添加更改
git add .

# 3. 提交
git commit -m "更新说明"

# 4. 推送
git push
```

---

## ✅ 推送前检查清单

- [ ] 已创建 `.gitignore` 文件
- [ ] 已排除敏感信息（密码、密钥等）
- [ ] 已排除临时文件和缓存
- [ ] README.md 已更新
- [ ] 代码已测试通过
- [ ] 提交信息清晰明确

---

## 🎯 推荐的仓库结构

推送后，GitHub仓库应该包含：

```
ai-digital-human-team/
├── README.md                    # 项目说明
├── .gitignore                   # Git忽略文件
├── 01-项目构想/                 # 项目设计文档
├── 02-数字人设计/               # 数字人角色定义
├── 03-技术实现/                 # 代码实现
├── 04-知识库建设/               # 知识库配置
├── 启动Web界面.sh              # 启动脚本
├── 安装依赖.sh                 # 依赖安装脚本
└── ...                          # 其他文件
```

---

## 📞 需要帮助？

如果遇到问题：
1. 检查GitHub仓库是否已创建
2. 检查远程仓库URL是否正确
3. 检查认证信息是否正确
4. 查看错误信息，根据提示解决
