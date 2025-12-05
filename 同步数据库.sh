#!/bin/bash

# 数据库同步脚本
# 用于在家里Mac和公司Mac之间同步数据库文件

DB_FILE="03-技术实现/02-功能模块/storage/digital_humans.db"
BACKUP_DIR="03-技术实现/02-功能模块/storage/backups"

# 云存储路径（根据你的选择修改）
# iCloud路径
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/DigitalHumanDB"
# Dropbox路径
DROPBOX_DIR="$HOME/Dropbox/DigitalHumanDB"

# 选择云存储（默认使用iCloud，如果没有则使用Dropbox）
if [ -d "$ICLOUD_DIR" ]; then
    SYNC_DIR="$ICLOUD_DIR"
    echo "📁 使用iCloud同步"
elif [ -d "$DROPBOX_DIR" ]; then
    SYNC_DIR="$DROPBOX_DIR"
    echo "📁 使用Dropbox同步"
else
    echo "❌ 错误: 未找到云存储目录"
    echo "请创建以下目录之一："
    echo "  - $ICLOUD_DIR"
    echo "  - $DROPBOX_DIR"
    exit 1
fi

# 创建备份目录
mkdir -p "$BACKUP_DIR"
mkdir -p "$SYNC_DIR"

echo "🔄 开始同步数据库文件..."
echo ""

# 备份当前数据库
if [ -f "$DB_FILE" ]; then
    BACKUP_FILE="$BACKUP_DIR/digital_humans.db.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 备份当前数据库: $BACKUP_FILE"
    cp "$DB_FILE" "$BACKUP_FILE"
    
    # 只保留最近5个备份
    ls -t "$BACKUP_DIR"/digital_humans.db.backup.* 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
fi

# 检查云存储中的数据库文件
CLOUD_DB="$SYNC_DIR/digital_humans.db"

if [ -f "$CLOUD_DB" ]; then
    # 比较时间戳，使用最新的
    if [ "$DB_FILE" -nt "$CLOUD_DB" ]; then
        echo "📤 本地数据库较新，上传到云存储..."
        cp "$DB_FILE" "$CLOUD_DB"
    elif [ "$CLOUD_DB" -nt "$DB_FILE" ]; then
        echo "📥 云存储数据库较新，下载到本地..."
        cp "$CLOUD_DB" "$DB_FILE"
    else
        echo "ℹ️  数据库文件已是最新，无需同步"
    fi
else
    # 云存储中没有数据库，上传本地数据库
    if [ -f "$DB_FILE" ]; then
        echo "📤 首次上传数据库到云存储..."
        cp "$DB_FILE" "$CLOUD_DB"
    else
        echo "⚠️  本地没有数据库文件，创建新数据库..."
        # 数据库会在首次运行时自动创建
    fi
fi

echo ""
echo "✅ 数据库同步完成！"
echo "📁 数据库位置: $DB_FILE"
echo "☁️  云存储位置: $CLOUD_DB"

