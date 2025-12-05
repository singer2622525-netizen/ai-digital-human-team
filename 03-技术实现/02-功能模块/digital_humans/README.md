# 数字人核心框架

## 📋 概述

数字人核心框架提供了所有数字人角色的基础能力，包括：
- AI模型集成（Ollama）
- 任务执行框架
- 状态管理
- 知识库集成（RAGFlow）

## 🏗️ 架构设计

```
BaseDigitalHuman (基类)
├── OllamaClient (AI引擎)
├── 状态管理
├── 任务执行
└── 知识检索

具体角色实现
├── ProjectManager (项目经理)
├── SystemArchitect (系统架构师)
├── FrontendEngineer (前端工程师)
├── BackendEngineer (后端工程师)
└── DevOpsEngineer (运维工程师)
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 确保Ollama运行

```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 如果没有运行，启动Ollama
ollama serve
```

### 3. 使用示例

```python
from digital_humans import ProjectManager

# 创建项目经理实例
pm = ProjectManager(name="项目经理-001")

# 执行任务
task = {
    "type": "create_plan",
    "input": {
        "requirements": "开发一个项目管理系统的网页端",
        "timeline": "3个月"
    }
}

result = pm.execute_task(task)
print(result["output"]["plan"])
```

## 📝 任务类型

### 项目经理 (ProjectManager)
- `create_plan`: 创建项目计划
- `track_progress`: 跟踪项目进度
- `generate_report`: 生成项目报告
- `identify_risks`: 识别项目风险

### 系统架构师 (SystemArchitect)
- `design_architecture`: 设计系统架构
- `evaluate_technology`: 评估技术方案
- `create_standards`: 制定技术规范
- `solve_problem`: 解决技术问题

## 🔧 扩展新角色

1. 继承 `BaseDigitalHuman`
2. 实现 `get_system_prompt()` 方法
3. 实现 `execute_task()` 方法
4. 定义任务类型和处理逻辑

示例：

```python
from .base import BaseDigitalHuman

class MyRole(BaseDigitalHuman):
    def get_system_prompt(self) -> str:
        return "你的角色定义..."
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get('type')
        if task_type == 'my_task':
            return self.handle_my_task(task)
        # ...
```

## 📊 状态管理

每个数字人都有状态：
- `idle`: 空闲
- `working`: 工作中
- `error`: 错误

```python
# 获取状态
status = pm.get_status()
print(status)
```

## 🔗 集成RAGFlow

TODO: 集成RAGFlow知识库检索功能

## 📚 相关文档

- [角色定义](../../02-数字人设计/)
- [Ollama配置](../../06-参考资源/02-ollama%20配置/)
- [RAGFlow配置](../../04-知识库建设/06-RAGFlow配置/)


