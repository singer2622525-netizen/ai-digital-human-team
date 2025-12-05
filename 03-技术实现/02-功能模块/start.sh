#!/bin/bash
# 启动进度跟踪工具

cd "$(dirname "$0")"

echo "🚀 启动软件工程事业部建设进度跟踪系统..."
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查数据文件是否存在
if [ ! -f "progress_data.json" ]; then
    echo "⚠️  未找到数据文件，是否初始化？(y/N)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        python3 init_progress.py
    else
        echo "已取消"
        exit 0
    fi
fi

# 运行进度跟踪工具
python3 progress_tracker.py


