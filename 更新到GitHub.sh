#!/bin/bash
# 快速更新到GitHub的脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "🔄 准备更新到GitHub..."
echo ""

# 检查是否有未提交的更改
if [ -z "$(git status --short)" ]; then
    echo "✅ 工作区干净，没有需要提交的更改"
    exit 0
fi

# 显示当前更改
echo "📋 当前更改："
git status --short
echo ""

# 询问是否继续
read -p "是否继续提交并推送到GitHub？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

# 添加所有更改
echo ""
echo "📦 添加文件到暂存区..."
git add .

# 提交
echo ""
echo "💾 提交更改..."
if [ -z "$1" ]; then
    read -p "请输入提交信息: " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        echo "❌ 提交信息不能为空"
        exit 1
    fi
else
    COMMIT_MSG="$1"
fi

git commit -m "$COMMIT_MSG"

# 推送
echo ""
echo "📤 推送到GitHub..."
git push

echo ""
echo "✅ 更新完成！"
echo ""
echo "📊 当前状态："
git status --short

echo ""
echo "🔗 GitHub仓库: https://github.com/singer2622525-netizen/ai-digital-human-team"
