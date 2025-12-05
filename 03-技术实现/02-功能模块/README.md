# 进度跟踪工具使用指南

## 功能说明

这是一个本地化的进度跟踪工具，用于记录和管理"软件工程事业部建设"项目的进度。工具会自动记录里程碑、任务、笔记等信息，并在每次启动时显示当前进度和待办事项。

## 快速开始

### 1. 初始化项目（首次使用）

```bash
cd 03-技术实现/02-功能模块
python3 init_progress.py
```

这会自动创建初始的里程碑和任务。

### 2. 查看进度仪表盘

**方式A: 在 Cursor 中快速查看（推荐）**
- 按 `Cmd+Shift+P` (Mac) 或 `Ctrl+Shift+P` (Windows)
- 输入 "Run Task" 或 "task"
- 选择 "📊 查看项目进度"

**方式B: 在 Cursor 终端中运行**
```bash
# 在项目根目录运行
./show_progress.sh

# 或者
python3 03-技术实现/02-功能模块/progress_tracker.py
```

**方式C: 进入目录运行**
```bash
cd 03-技术实现/02-功能模块
python3 progress_tracker.py
```

每次运行都会显示：
- 📊 项目总体进度
- 🎯 里程碑完成情况
- 📋 任务统计和完成率
- 🚨 紧急任务提醒
- 📌 今日进行中的任务
- 📝 待办任务列表

### 3. 常用命令

```bash
# 显示帮助
python progress_tracker.py help

# 添加里程碑
python progress_tracker.py add-milestone

# 添加任务
python progress_tracker.py add-task

# 更新任务状态
python progress_tracker.py update-task

# 完成里程碑
python progress_tracker.py complete-milestone

# 添加笔记
python progress_tracker.py add-note

# 列出所有任务
python progress_tracker.py list-tasks

# 列出所有里程碑
python progress_tracker.py list-milestones
```

## 数据结构

所有数据保存在 `progress_data.json` 文件中，包含：

- **项目信息**: 项目名称、开始日期、最后更新时间
- **里程碑**: 目标日期、状态、完成日期
- **任务**: 标题、优先级、状态、关联里程碑
- **笔记**: 记录重要决策和思考

## 任务状态

- `pending`: 待办
- `in_progress`: 进行中
- `completed`: 已完成
- `blocked`: 受阻

## 任务优先级

- `high`: 高优先级（紧急任务）
- `medium`: 中优先级
- `low`: 低优先级

## 使用建议

1. **每天开始工作前**: 运行 `python progress_tracker.py` 查看当前进度和待办事项
2. **完成任务后**: 使用 `update-task` 更新任务状态为 `completed`
3. **开始新任务**: 使用 `update-task` 将任务状态改为 `in_progress`
4. **重要决策**: 使用 `add-note` 记录关键决策和思考
5. **定期回顾**: 使用 `list-tasks` 和 `list-milestones` 查看完整列表

## 数据备份

建议定期备份 `progress_data.json` 文件，可以手动复制或使用版本控制工具（如 Git）。

## 扩展功能

如果需要更多功能，可以：
- 修改 `progress_tracker.py` 添加新功能
- 集成到其他工具（如看板、日历等）
- 导出数据到其他格式（Excel、Markdown等）
