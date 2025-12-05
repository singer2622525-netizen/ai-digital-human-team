# 🖥️ Dell服务器存储配置指南

## 📋 概述

本指南介绍如何将公司Dell服务器或Mac上的SSD作为数据同步存储。

---

## 🎯 方案选择

### 方案1: Dell服务器存储（推荐）⭐

**优点：**
- ✅ 集中存储，统一管理
- ✅ 多设备访问
- ✅ 自动备份
- ✅ 无需携带SSD

**适用场景：**
- 公司内网环境
- 多设备使用
- 需要集中管理

### 方案2: 外部SSD存储

**优点：**
- ✅ 便携性强
- ✅ 速度快
- ✅ 离线可用
- ✅ 不依赖网络

**适用场景：**
- 需要离线访问
- 频繁切换设备
- 大文件传输

---

## 🖥️ 方案1: Dell服务器存储配置

### 步骤1: 在Dell服务器上创建存储目录

```bash
# SSH登录到Dell服务器
ssh user@dell-server-ip

# 创建存储目录
mkdir -p /data/digital-human-db
chmod 755 /data/digital-human-db

# 创建共享目录（如果需要）
# 使用Samba或NFS共享
```

### 步骤2: 配置网络挂载（Mac）

#### 方法A: Samba共享（推荐）

```bash
# 1. 在Mac上创建挂载点
mkdir -p ~/mnt/dell-server

# 2. 挂载Samba共享
mount_smbfs //username@dell-server-ip/digital-human-db ~/mnt/dell-server

# 或使用Finder：
# 1. Finder → 前往 → 连接服务器
# 2. 输入: smb://dell-server-ip/digital-human-db
# 3. 输入用户名和密码
```

#### 方法B: SSHFS挂载

```bash
# 1. 安装SSHFS
brew install sshfs

# 2. 创建挂载点
mkdir -p ~/mnt/dell-server

# 3. 挂载远程目录
sshfs user@dell-server-ip:/data/digital-human-db ~/mnt/dell-server

# 4. 卸载（需要时）
umount ~/mnt/dell-server
```

#### 方法C: NFS挂载

```bash
# 1. 在Dell服务器上配置NFS（需要root权限）
# 编辑 /etc/exports
echo "/data/digital-human-db *(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo exportfs -ra

# 2. 在Mac上挂载
mkdir -p ~/mnt/dell-server
sudo mount -t nfs dell-server-ip:/data/digital-human-db ~/mnt/dell-server
```

### 步骤3: 配置环境变量

```bash
# 编辑环境变量文件
nano ~/DeveloperConfig/环境变量/.env.work

# 添加Dell服务器路径
DELL_SERVER_PATH=~/mnt/dell-server/DigitalHumanDB
# 或使用绝对路径
DELL_SERVER_PATH=/Volumes/dell-server/DigitalHumanDB
```

### 步骤4: 设置自动挂载（可选）

创建自动挂载脚本 `mount_dell_server.sh`：

```bash
#!/bin/bash

# Dell服务器自动挂载脚本

MOUNT_POINT=~/mnt/dell-server
SERVER_PATH=//username@dell-server-ip/digital-human-db

if [ ! -d "$MOUNT_POINT" ]; then
    mkdir -p "$MOUNT_POINT"
fi

if ! mountpoint -q "$MOUNT_POINT"; then
    echo "📡 挂载Dell服务器..."
    mount_smbfs "$SERVER_PATH" "$MOUNT_POINT"
    echo "✅ 挂载成功"
else
    echo "ℹ️  已挂载"
fi
```

设置开机自动挂载：

```bash
# 添加到 ~/.zshrc 或 ~/.bash_profile
if [ -f ~/mount_dell_server.sh ]; then
    bash ~/mount_dell_server.sh
fi
```

---

## 💾 方案2: 外部SSD存储配置

### 步骤1: 格式化SSD（如果需要）

```bash
# 1. 查看连接的磁盘
diskutil list

# 2. 格式化SSD（选择合适的分区）
diskutil eraseDisk APFS "DigitalHumanDB" /dev/diskX

# 或使用GUI：磁盘工具 → 抹掉 → APFS格式
```

### 步骤2: 创建存储目录

```bash
# SSD挂载后，创建存储目录
mkdir -p /Volumes/DigitalHumanDB/DigitalHumanDB
```

### 步骤3: 配置环境变量

```bash
# 编辑环境变量文件
nano ~/DeveloperConfig/环境变量/.env.work

# 添加SSD路径
SSD_PATH=/Volumes/DigitalHumanDB/DigitalHumanDB
```

### 步骤4: 设置自动检测

系统会自动检测SSD挂载，无需额外配置。

---

## 🔧 Web界面配置

### 在Web界面中使用

1. **打开数据同步页面**
   - 访问 `http://localhost:5001`
   - 点击 "🔄 数据同步" 标签

2. **查看可用存储选项**
   - 系统会自动检测：
     - iCloud
     - Dropbox
     - 外部SSD（如果已挂载）
     - Dell服务器（如果已配置）

3. **一键同步**
   - 选择存储类型
   - 点击 "同步" 按钮
   - 系统自动处理上传/下载

---

## 📝 配置示例

### Dell服务器配置示例

```bash
# ~/DeveloperConfig/环境变量/.env.work

# Dell服务器配置
DELL_SERVER_IP=192.168.1.100
DELL_SERVER_USER=your-username
DELL_SERVER_PATH=~/mnt/dell-server/DigitalHumanDB

# 或使用Finder挂载后的路径
DELL_SERVER_PATH=/Volumes/dell-server/DigitalHumanDB
```

### SSD配置示例

```bash
# ~/DeveloperConfig/环境变量/.env.work

# SSD配置（自动检测，无需配置）
# 系统会自动检测 /Volumes 下的外部存储
```

---

## 🔄 同步流程

### 自动同步流程

```
1. 检测存储选项
   ↓
2. 比较本地和远程数据库时间戳
   ↓
3. 使用最新版本
   ↓
4. 同步到目标存储
```

### 手动同步流程

```
1. 打开Web界面 → 数据同步标签
   ↓
2. 选择存储类型（Dell服务器/SSD）
   ↓
3. 点击"同步"按钮
   ↓
4. 系统自动处理
```

---

## ⚠️ 注意事项

### Dell服务器存储

1. **网络连接**
   - 确保Mac和服务器在同一网络
   - 检查防火墙设置
   - 测试网络连通性：`ping dell-server-ip`

2. **权限设置**
   - 确保有读写权限
   - 检查Samba/NFS权限配置

3. **自动挂载**
   - 网络断开时需要重新挂载
   - 建议使用自动挂载脚本

### SSD存储

1. **挂载检测**
   - 确保SSD已正确挂载
   - 检查挂载点：`ls /Volumes`

2. **文件系统**
   - 推荐使用APFS或exFAT格式
   - 确保Mac可以读写

3. **便携性**
   - 记得携带SSD
   - 安全弹出后再拔出

---

## 🚀 快速开始

### Dell服务器（3步）

```bash
# 1. 挂载服务器
mount_smbfs //user@server-ip/share ~/mnt/dell-server

# 2. 配置环境变量
export DELL_SERVER_PATH=~/mnt/dell-server/DigitalHumanDB

# 3. 在Web界面中同步
# 打开 http://localhost:5001 → 数据同步 → 选择Dell Server → 同步
```

### SSD（2步）

```bash
# 1. 插入SSD（自动挂载）

# 2. 在Web界面中同步
# 打开 http://localhost:5001 → 数据同步 → 选择外部SSD → 同步
```

---

## 📊 方案对比

| 特性 | Dell服务器 | 外部SSD | iCloud | Dropbox |
|------|-----------|---------|--------|---------|
| 速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 便携性 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 离线可用 | ❌ | ✅ | ❌ | ❌ |
| 集中管理 | ✅ | ❌ | ✅ | ✅ |
| 配置复杂度 | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ |

---

## 🔍 故障排查

### Dell服务器连接失败

```bash
# 1. 检查网络连接
ping dell-server-ip

# 2. 检查Samba服务
smbclient -L dell-server-ip -U username

# 3. 检查挂载点
ls -la ~/mnt/dell-server

# 4. 重新挂载
umount ~/mnt/dell-server
mount_smbfs //user@server-ip/share ~/mnt/dell-server
```

### SSD未检测到

```bash
# 1. 检查磁盘列表
diskutil list

# 2. 检查挂载点
ls /Volumes

# 3. 手动挂载（如果需要）
diskutil mount /dev/diskX
```

---

## ✅ 检查清单

### Dell服务器配置

- [ ] ✅ 服务器存储目录已创建
- [ ] ✅ Samba/NFS服务已配置
- [ ] ✅ Mac可以访问服务器
- [ ] ✅ 环境变量已配置
- [ ] ✅ 自动挂载脚本已设置（可选）

### SSD配置

- [ ] ✅ SSD已格式化
- [ ] ✅ 存储目录已创建
- [ ] ✅ Mac可以读写SSD
- [ ] ✅ SSD已正确挂载

---

**✅ 完成！现在你可以使用Dell服务器或SSD作为数据存储了！**

