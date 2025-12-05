# 🏢 公司Mac使用指南

## 📋 目录
1. [首次设置](#首次设置)
2. [日常启动](#日常启动)
3. [环境配置](#环境配置)
4. [常见问题](#常见问题)

---

## 🚀 首次设置（新电脑）

### 步骤1: 克隆项目

```bash
# 进入工作目录
cd ~/Documents/Projects/cursor

# 克隆项目（如果已发布到GitHub）
git clone https://github.com/your-username/ai-digital-human-team.git "00-00软件工程事业部（AI 数字人队伍）"

# 或者如果项目在本地，直接复制项目文件夹
```

### 步骤2: 安装Python依赖

```bash
# 进入web_interface目录
cd "00-00软件工程事业部（AI 数字人队伍）/03-技术实现/02-功能模块/web_interface"

# 安装依赖
pip3 install -r requirements.txt
```

### 步骤3: 安装并配置Ollama

```bash
# 安装Ollama (Mac)
brew install ollama

# 启动Ollama服务（后台运行）
ollama serve &

# 下载代码生成模型（首次需要网络）
ollama pull deepseek-coder:6.7b

# 验证安装
ollama list
```

### 步骤4: 配置环境变量（可选）

如果需要使用RAGFlow知识库，配置环境变量：

```bash
# 编辑环境变量文件
nano ~/DeveloperConfig/环境变量/.env.work

# 添加以下内容：
RAGFLOW_BASE_URL=http://your-server-ip:port
RAGFLOW_API_KEY=your-api-key
RAGFLOW_KB_ID=your-knowledge-base-id

# 保存并加载
source ~/DeveloperConfig/环境变量/.env.work
```

### 步骤5: 验证系统

```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 检查Python依赖
python3 -c "import flask; print('Flask OK')"
python3 -c "import markdown; print('Markdown OK')"
```

---

## 🔄 日常启动

### 方法1: 使用启动脚本（推荐）

```bash
# 进入项目目录
cd ~/Documents/Projects/cursor/"00-00软件工程事业部（AI 数字人队伍）"

# 启动系统
cd "03-技术实现/02-功能模块/web_interface"
./start.sh
```

### 方法2: 手动启动

```bash
# 1. 确保Ollama运行
ollama serve &

# 2. 启动Web服务
cd "03-技术实现/02-功能模块/web_interface"
python3 app.py
```

### 方法3: 使用Cursor任务（如果配置了）

1. 在Cursor中按 `Cmd+Shift+P`
2. 输入 "Run Task"
3. 选择 "启动AI数字人系统"

---

## 🌐 访问系统

启动成功后，在浏览器中访问：

```
http://localhost:5001
```

### 功能页面

- **首页**: `http://localhost:5001/`
- **任务管理**: `http://localhost:5001/tasks`
- **可视化**: `http://localhost:5001/visualization`
- **用户操作手册**: `http://localhost:5001/docs/user-manual`
- **Cursor使用指南**: `http://localhost:5001/docs/cursor-guide`
- **技术说明**: `http://localhost:5001/docs/technical-spec`

---

## ⚙️ 环境配置

### 检查清单

在首次使用前，确认以下配置：

- [ ] ✅ Python 3.9+ 已安装
- [ ] ✅ Ollama 已安装并运行
- [ ] ✅ deepseek-coder:6.7b 模型已下载
- [ ] ✅ Python依赖已安装
- [ ] ✅ 环境变量已配置（如需要RAGFlow）
- [ ] ✅ 端口5001未被占用

### 端口检查

```bash
# 检查端口是否被占用
lsof -ti:5001

# 如果被占用，可以：
# 1. 关闭占用进程
lsof -ti:5001 | xargs kill -9

# 2. 或修改app.py中的端口号
```

### 修改端口（如果需要）

编辑 `03-技术实现/02-功能模块/web_interface/app.py`：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)  # 修改这里的端口号
```

---

## 🛑 关闭系统

### 方法1: 使用Ctrl+C（前台运行）

如果系统在前台运行，按 `Ctrl+C` 停止。

### 方法2: 查找并关闭进程（后台运行）

```bash
# 查找Python进程
ps aux | grep "app.py"

# 或直接关闭端口5001的进程
lsof -ti:5001 | xargs kill -9

# 关闭Ollama（如果需要）
pkill ollama
```

### 方法3: 使用启动脚本的停止功能

如果启动脚本支持停止功能：

```bash
./start.sh stop
```

---

## 🔧 常见问题

### Q1: Ollama连接失败

**问题**: `❌ Ollama API调用失败`

**解决方案**:
```bash
# 1. 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 2. 如果没有运行，启动Ollama
ollama serve

# 3. 检查模型是否已下载
ollama list
```

### Q2: 端口被占用

**问题**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -ti:5001

# 关闭进程
lsof -ti:5001 | xargs kill -9

# 或使用其他端口
# 修改app.py中的port参数
```

### Q3: 模块导入错误

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 重新安装依赖
cd "03-技术实现/02-功能模块/web_interface"
pip3 install -r requirements.txt
```

### Q4: 模型未找到

**问题**: `model 'deepseek-coder:6.7b' not found`

**解决方案**:
```bash
# 下载模型（需要网络）
ollama pull deepseek-coder:6.7b

# 验证
ollama list
```

### Q5: RAGFlow连接失败

**问题**: 知识库功能不可用

**解决方案**:
```bash
# 1. 检查环境变量
echo $RAGFLOW_BASE_URL

# 2. 如果没有设置，配置环境变量
# 参考"步骤4: 配置环境变量"

# 3. 系统会在RAGFlow不可用时优雅降级，不影响其他功能
```

### Q6: 数据库文件不存在

**问题**: `database file not found`

**解决方案**:
```bash
# 数据库会在首次运行时自动创建
# 如果仍有问题，检查storage目录权限
ls -la "03-技术实现/02-功能模块/storage/"
```

---

## 📝 快速参考

### 启动命令（一键）

```bash
# 创建快捷脚本
cat > ~/start_digital_human.sh << 'EOF'
#!/bin/bash
cd ~/Documents/Projects/cursor/"00-00软件工程事业部（AI 数字人队伍）"/"03-技术实现/02-功能模块/web_interface"
ollama serve > /dev/null 2>&1 &
sleep 2
python3 app.py
EOF

chmod +x ~/start_digital_human.sh

# 使用
~/start_digital_human.sh
```

### 停止命令（一键）

```bash
# 创建停止脚本
cat > ~/stop_digital_human.sh << 'EOF'
#!/bin/bash
lsof -ti:5001 | xargs kill -9 2>/dev/null
pkill ollama 2>/dev/null
echo "✅ 系统已停止"
EOF

chmod +x ~/stop_digital_human.sh

# 使用
~/stop_digital_human.sh
```

---

## 🔄 数据同步

### 如果使用GitHub

```bash
# 拉取最新代码
cd ~/Documents/Projects/cursor/"00-00软件工程事业部（AI 数字人队伍）"
git pull origin main
```

### 如果使用本地文件

确保项目文件夹已同步到公司Mac。

---

## 📚 相关文档

- [用户操作手册](03-技术实现/02-功能模块/web_interface/用户操作手册.md)
- [Cursor配合使用指南](03-技术实现/02-功能模块/web_interface/Cursor配合使用指南.md)
- [系统技术说明](03-技术实现/02-功能模块/web_interface/系统技术说明.md)

---

## ✅ 检查清单

首次在公司Mac上使用时，按以下顺序检查：

1. [ ] 项目文件已复制/克隆到公司Mac
2. [ ] Python 3.9+ 已安装
3. [ ] 依赖已安装 (`pip3 install -r requirements.txt`)
4. [ ] Ollama已安装 (`brew install ollama`)
5. [ ] Ollama服务已启动 (`ollama serve`)
6. [ ] 模型已下载 (`ollama pull deepseek-coder:6.7b`)
7. [ ] 环境变量已配置（如需要）
8. [ ] Web服务可以启动 (`python3 app.py`)
9. [ ] 浏览器可以访问 (`http://localhost:5001`)

---

**🎉 完成！现在你可以在公司Mac上使用AI数字人队伍管理系统了！**

