#!/bin/bash

# 关闭AI数字人队伍管理系统

echo "🛑 正在关闭AI数字人队伍管理系统..."

# 关闭Web服务（端口5001）
if lsof -ti:5001 > /dev/null 2>&1; then
    echo "📌 关闭Web服务（端口5001）..."
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    echo "✅ Web服务已关闭"
else
    echo "ℹ️  Web服务未运行"
fi

# 询问是否关闭Ollama
read -p "是否关闭Ollama服务？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if pgrep -x "ollama" > /dev/null; then
        echo "📌 关闭Ollama服务..."
        pkill ollama
        echo "✅ Ollama已关闭"
    else
        echo "ℹ️  Ollama未运行"
    fi
else
    echo "ℹ️  保留Ollama运行（其他项目可能在使用）"
fi

echo ""
echo "✅ 系统关闭完成！"

