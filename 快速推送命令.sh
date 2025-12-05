#!/bin/bash
# 快速推送到GitHub的脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "🚀 准备推送到GitHub..."
echo ""

# 检查是否已初始化git
if [ ! -d ".git" ]; then
    echo "📦 初始化Git仓库..."
    git init
fi

# 检查Git用户配置
if [ -z "$(git config user.name)" ]; then
    echo "⚠️  未配置Git用户名，请先配置："
    echo "   git config user.name '你的GitHub用户名'"
    echo "   git config user.email '你的GitHub邮箱'"
    echo ""
    read -p "是否现在配置？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入GitHub用户名: " GIT_USERNAME
        read -p "请输入GitHub邮箱: " GIT_EMAIL
        git config user.name "$GIT_USERNAME"
        git config user.email "$GIT_EMAIL"
        echo "✅ 配置完成"
    else
        echo "❌ 请先配置Git用户信息"
        exit 1
    fi
fi

echo ""
echo "📋 当前Git状态："
git status --short | head -20

echo ""
read -p "是否继续添加所有文件并提交？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

# 添加所有文件
echo ""
echo "📦 添加文件到暂存区..."
git add .

# 提交
echo ""
echo "💾 提交更改..."
read -p "请输入提交信息（直接回车使用默认信息）: " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="初始提交：软件工程事业部AI数字人队伍项目

- 完成组织架构设计
- 实现9个数字人角色
- 完成智能产品规划师核心功能
- 完成Web界面基础功能
- 完成系统布局和逻辑关系设计"
fi

git commit -m "$COMMIT_MSG"

echo ""
echo "✅ 本地提交完成！"
echo ""
echo "📤 下一步："
echo "1. 在GitHub创建新仓库（如果还没有）"
echo "2. 添加远程仓库："
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "3. 推送代码："
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "或者运行以下命令（替换YOUR_USERNAME和REPO_NAME）："
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
