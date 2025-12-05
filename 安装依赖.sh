#!/bin/bash
# 安装项目依赖脚本（解决中文路径问题）

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 安装项目依赖..."
echo ""

# 安装Web界面依赖
echo "1. 安装Web界面依赖..."
cd "$SCRIPT_DIR/03-技术实现/02-功能模块/web_interface" || {
    echo "❌ 错误: 无法进入web_interface目录"
    exit 1
}

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Web界面依赖安装完成"
else
    echo "⚠️  未找到requirements.txt"
fi

echo ""

# 安装密码数据库依赖
echo "2. 安装密码数据库依赖..."
pip3 install cryptography
echo "✅ 密码数据库依赖安装完成"

echo ""
echo "✅ 所有依赖安装完成！"
echo ""
echo "下一步：运行 ./启动Web界面.sh 启动服务"
