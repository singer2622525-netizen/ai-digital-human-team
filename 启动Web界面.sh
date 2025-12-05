#!/bin/bash
# 启动Web界面脚本（解决中文路径问题）

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到web_interface目录
cd "$SCRIPT_DIR/03-技术实现/02-功能模块/web_interface" || {
    echo "❌ 错误: 无法进入web_interface目录"
    echo "当前目录: $(pwd)"
    exit 1
}

echo "✅ 当前目录: $(pwd)"
echo ""

# 检查requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 未找到requirements.txt文件"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip3 install -r requirements.txt

# 安装密码数据库依赖
echo "📦 安装密码数据库依赖..."
pip3 install cryptography

# 启动应用
echo ""
echo "🚀 启动Flask应用..."
echo "📍 访问地址: http://localhost:5001"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py
