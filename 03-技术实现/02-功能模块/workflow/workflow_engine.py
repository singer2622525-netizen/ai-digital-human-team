#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流引擎
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import uuid
import json
import logging

from .task_manager import TaskManager, Task, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """工作流状态"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"  # 新增：暂停状态
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep:
    """工作流步骤"""
    
    def __init__(self,
                 step_id: str,
                 step_type: str,
                 role_name: str,
                 input_data: Dict[str, Any],
                 condition: Optional[Callable] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        创建工作流步骤
        
        Args:
            step_id: 步骤ID
            step_type: 步骤类型（任务类型）
            role_name: 负责的角色
            input_data: 输入数据
            condition: 执行条件（函数）
            metadata: 元数据
        """
        self.step_id = step_id
        self.step_type = step_type
        self.role_name = role_name
        self.input_data = input_data
        self.condition = condition
        self.metadata = metadata or {}
        
        # 执行状态
        self.status = TaskStatus.PENDING
        self.task_id = None
        self.result = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "role_name": self.role_name,
            "input_data": self.input_data,
            "status": self.status.value,
            "task_id": self.task_id,
            "result": self.result,
            "error": self.error
        }
    
    def can_execute(self, workflow_context: Dict[str, Any]) -> bool:
        """检查是否可以执行"""
        if self.condition:
            return self.condition(workflow_context)
        return True


class Workflow:
    """工作流"""
    
    def __init__(self,
                 name: str,
                 description: str = "",
                 steps: Optional[List[WorkflowStep]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        创建工作流
        
        Args:
            name: 工作流名称
            description: 描述
            steps: 步骤列表
            metadata: 元数据
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.steps = steps or []
        self.metadata = metadata or {}
        
        # 状态
        self.status = WorkflowStatus.CREATED
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
        # 上下文（用于步骤间数据传递）
        self.context: Dict[str, Any] = {}
        
        # 步骤依赖关系（step_id -> [依赖的step_id列表]）
        self.dependencies: Dict[str, List[str]] = {}
    
    def add_step(self,
                 step_type: str,
                 role_name: str,
                 input_data: Dict[str, Any],
                 depends_on: Optional[List[str]] = None,
                 condition: Optional[Callable] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        添加步骤
        
        Args:
            step_type: 步骤类型
            role_name: 负责角色
            input_data: 输入数据
            depends_on: 依赖的步骤ID列表
            condition: 执行条件
            metadata: 元数据
        
        Returns:
            步骤ID
        """
        step_id = f"step_{len(self.steps) + 1}"
        step = WorkflowStep(
            step_id=step_id,
            step_type=step_type,
            role_name=role_name,
            input_data=input_data,
            condition=condition,
            metadata=metadata
        )
        
        self.steps.append(step)
        
        if depends_on:
            self.dependencies[step_id] = depends_on
        
        return step_id
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """获取可以执行的步骤"""
        ready_steps = []
        
        for step in self.steps:
            # 如果已完成或进行中，跳过
            if step.status in [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS]:
                continue
            
            # 检查依赖
            if step.step_id in self.dependencies:
                deps = self.dependencies[step.step_id]
                all_deps_completed = all(
                    any(s.step_id == dep_id and s.status == TaskStatus.COMPLETED 
                        for s in self.steps)
                    for dep_id in deps
                )
                if not all_deps_completed:
                    continue
            
            # 检查执行条件
            if step.can_execute(self.context):
                ready_steps.append(step)
        
        return ready_steps
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """获取步骤"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def update_step_result(self, step_id: str, result: Dict[str, Any]):
        """更新步骤结果"""
        step = self.get_step(step_id)
        if step:
            step.status = TaskStatus.COMPLETED
            step.result = result
            # 将结果添加到上下文
            self.context[step_id] = result
    
    def is_completed(self) -> bool:
        """检查是否所有步骤都完成"""
        return all(step.status == TaskStatus.COMPLETED for step in self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [step.to_dict() for step in self.steps],
            "context": self.context,
            "dependencies": self.dependencies
        }


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, task_manager: TaskManager):
        """
        初始化工作流引擎
        
        Args:
            task_manager: 任务管理器实例
        """
        self.task_manager = task_manager
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_templates: Dict[str, Workflow] = {}
    
    def create_workflow(self,
                      name: str,
                      description: str = "",
                      steps: Optional[List[WorkflowStep]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Workflow:
        """创建工作流"""
        workflow = Workflow(
            name=name,
            description=description,
            steps=steps,
            metadata=metadata
        )
        self.workflows[workflow.id] = workflow
        return workflow
    
    def register_template(self, name: str, workflow: Workflow):
        """注册工作流模板"""
        self.workflow_templates[name] = workflow
    
    def create_from_template(self, template_name: str, **kwargs) -> Optional[Workflow]:
        """从模板创建工作流"""
        template = self.workflow_templates.get(template_name)
        if not template:
            return None
        
        # 创建新工作流（复制模板）
        workflow = Workflow(
            name=kwargs.get('name', template.name),
            description=kwargs.get('description', template.description),
            steps=[],  # 需要重新创建步骤
            metadata=kwargs.get('metadata', {})
        )
        
        # 复制步骤
        for step in template.steps:
            workflow.add_step(
                step_type=step.step_type,
                role_name=step.role_name,
                input_data=step.input_data,
                depends_on=self.workflow_templates[template_name].dependencies.get(step.step_id),
                condition=step.condition,
                metadata=step.metadata
            )
        
        self.workflows[workflow.id] = workflow
        return workflow
    
    def start_workflow(self, workflow_id: str) -> bool:
        """启动工作流"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        # 创建初始任务
        self._create_tasks_for_ready_steps(workflow)
        
        return True
    
    def _create_tasks_for_ready_steps(self, workflow: Workflow):
        """为就绪的步骤创建任务"""
        ready_steps = workflow.get_ready_steps()
        
        for step in ready_steps:
            # 构建依赖任务ID列表
            dependencies = []
            if step.step_id in workflow.dependencies:
                for dep_step_id in workflow.dependencies[step.step_id]:
                    dep_step = workflow.get_step(dep_step_id)
                    if dep_step and dep_step.task_id:
                        dependencies.append(dep_step.task_id)
            
            # 创建任务
            task = self.task_manager.create_task(
                task_type=step.step_type,
                input_data=step.input_data,
                dependencies=dependencies if dependencies else None,
                metadata={
                    "workflow_id": workflow.id,
                    "step_id": step.step_id,
                    **step.metadata
                }
            )
            
            # 分配任务
            self.task_manager.assign_task(task.id, step.role_name)
            step.task_id = task.id
            step.status = TaskStatus.ASSIGNED
    
    def update_workflow(self, workflow_id: str):
        """更新工作流状态（检查任务完成情况）"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return
        
        # 检查所有步骤的任务状态
        for step in workflow.steps:
            if step.task_id:
                task = self.task_manager.get_task(step.task_id)
                if task:
                    step.status = task.status
                    if task.status == TaskStatus.COMPLETED:
                        step.result = task.result
                        workflow.update_step_result(step.step_id, task.result)
                    elif task.status == TaskStatus.FAILED:
                        step.error = task.error
        
        # 检查是否有新的步骤可以执行（仅在运行状态）
        if workflow.status == WorkflowStatus.RUNNING:
            self._create_tasks_for_ready_steps(workflow)
            
            # 检查工作流是否完成
            if workflow.is_completed():
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now()
        elif workflow.status == WorkflowStatus.PAUSED:
            # 暂停状态不创建新任务
            logger.info(f"工作流已暂停，跳过更新: {workflow_id[:8]}...")
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流"""
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[Workflow]:
        """获取所有工作流"""
        return list(self.workflows.values())


if __name__ == "__main__":
    # 测试代码
    from task_manager import TaskManager
    
    task_manager = TaskManager()
    engine = WorkflowEngine(task_manager)
    
    # 创建一个简单的工作流
    workflow = engine.create_workflow(
        name="项目开发工作流",
        description="从需求到交付的完整流程"
    )
    
    # 添加步骤
    workflow.add_step(
        step_type="create_plan",
        role_name="项目经理",
        input_data={"requirements": "开发系统", "timeline": "2个月"}
    )
    
    step2_id = workflow.add_step(
        step_type="design_architecture",
        role_name="系统架构师",
        input_data={"requirements": "设计架构"},
        depends_on=["step_1"]
    )
    
    print(f"工作流ID: {workflow.id}")
    print(f"步骤数: {len(workflow.steps)}")
    print(f"就绪步骤: {len(workflow.get_ready_steps())}")


