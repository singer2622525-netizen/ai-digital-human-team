# 任务分配和工作流系统

## 📋 概述

本模块实现了完整的任务分配和工作流系统，包括：
- 任务管理（创建、分配、跟踪）
- 工作流引擎（流程定义、执行、监控）
- 任务调度器（自动分配、执行）
- 工作流模板（常用流程模板）

## 🏗️ 架构设计

```
TaskManager (任务管理)
    ├── Task (任务对象)
    ├── 任务队列
    └── 状态跟踪

WorkflowEngine (工作流引擎)
    ├── Workflow (工作流)
    ├── WorkflowStep (工作流步骤)
    └── 模板管理

TaskScheduler (任务调度器)
    ├── 角色映射
    ├── 自动分配
    └── 任务执行
```

## 🚀 快速开始

### 1. 基本使用

```python
from workflow import TaskManager, TaskScheduler
from workflow.workflow_engine import WorkflowEngine

# 初始化
task_manager = TaskManager()
scheduler = TaskScheduler(task_manager)
engine = WorkflowEngine(task_manager)

# 创建任务
task = task_manager.create_task(
    task_type="create_plan",
    input_data={"requirements": "开发系统", "timeline": "2个月"}
)

# 自动分配并执行
scheduler.auto_assign_pending_tasks()
result = scheduler.execute_task(task.id)
```

### 2. 使用工作流

```python
# 注册模板
from workflow.workflow_templates import register_all_templates
register_all_templates(engine)

# 从模板创建工作流
workflow = engine.create_from_template(
    "project_development",
    name="我的项目",
    description="测试项目"
)

# 启动工作流
engine.start_workflow(workflow.id)

# 更新工作流状态
engine.update_workflow(workflow.id)
```

## 📝 任务类型

### 项目经理
- `create_plan`: 创建项目计划
- `track_progress`: 跟踪项目进度
- `generate_report`: 生成项目报告
- `identify_risks`: 识别项目风险

### 系统架构师
- `design_architecture`: 设计系统架构
- `evaluate_technology`: 评估技术方案
- `create_standards`: 制定技术规范
- `solve_problem`: 解决技术问题

### 前端工程师
- `implement_ui`: 实现UI界面
- `optimize_performance`: 优化性能
- `fix_bug`: 修复Bug

### 后端工程师
- `implement_api`: 实现API接口
- `optimize_query`: 优化数据库查询
- `fix_bug`: 修复Bug

### 运维工程师
- `monitor_system`: 监控系统
- `handle_incident`: 处理故障
- `optimize_performance`: 优化性能

## 🔄 工作流模板

### 1. 项目开发工作流
- 步骤1: 项目计划制定（项目经理）
- 步骤2: 系统架构设计（系统架构师）
- 步骤3: 前端界面开发（前端工程师）
- 步骤4: 后端API开发（后端工程师）
- 步骤5: 系统监控（运维工程师）

### 2. Bug修复工作流
- 步骤1: 问题分析（系统架构师）
- 步骤2: Bug修复（后端/前端工程师）

## 📊 API接口

### 任务管理
- `create_task()`: 创建任务
- `assign_task()`: 分配任务
- `get_task()`: 获取任务
- `get_tasks_by_status()`: 按状态查询
- `get_tasks_by_role()`: 按角色查询

### 工作流
- `create_workflow()`: 创建工作流
- `start_workflow()`: 启动工作流
- `update_workflow()`: 更新工作流状态
- `get_workflow()`: 获取工作流

### 调度器
- `auto_assign_pending_tasks()`: 自动分配待分配任务
- `execute_task()`: 执行任务
- `get_role_workload()`: 获取角色工作负载

## 🔗 集成到网页端

工作流系统已集成到网页端API，可以通过HTTP接口使用：

```bash
# 创建任务
curl -X POST http://127.0.0.1:5001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "create_plan",
    "input_data": {"requirements": "开发系统"}
  }'

# 查询任务
curl http://127.0.0.1:5001/api/tasks

# 创建工作流
curl -X POST http://127.0.0.1:5001/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "template": "project_development",
    "name": "我的项目"
  }'
```

## 📚 相关文档

- [任务管理API文档](./task_manager.py)
- [工作流引擎文档](./workflow_engine.py)
- [任务调度器文档](./task_scheduler.py)


