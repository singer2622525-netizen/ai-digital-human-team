#!/bin/bash

# 数字人管理网页端启动脚本

echo "🚀 启动数字人管理网页端..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 未找到requirements.txt"
    exit 1
fi

# 安装依赖（如果需要）
echo "📦 检查依赖..."
pip3 install -q -r requirements.txt

# 启动应用
echo "✅ 启动Flask应用..."
echo "📍 访问地址: http://localhost:5001"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py


