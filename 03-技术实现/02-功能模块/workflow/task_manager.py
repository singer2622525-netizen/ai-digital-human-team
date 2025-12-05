#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理系统
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import json
import heapq
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 待分配
    ASSIGNED = "assigned"    # 已分配
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class Task:
    """任务对象"""
    
    def __init__(self,
                 task_type: str,
                 input_data: Dict[str, Any],
                 assigned_to: Optional[str] = None,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 dependencies: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        创建任务
        
        Args:
            task_type: 任务类型（如：create_plan, design_architecture）
            input_data: 任务输入数据
            assigned_to: 分配给的角色名称
            priority: 任务优先级
            dependencies: 依赖的任务ID列表
            metadata: 额外元数据
        """
        self.id = str(uuid.uuid4())
        self.task_type = task_type
        self.input_data = input_data
        self.assigned_to = assigned_to
        self.priority = priority
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        
        # 状态和时间戳
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.assigned_at = None
        self.started_at = None
        self.completed_at = None
        
        # 执行结果
        self.result = None
        self.error = None
        
        # 重试相关
        self.retry_count = 0
        self.max_retries = 3
        
        # 超时相关
        self.timeout_seconds = None  # None表示不超时
        self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "task_type": self.task_type,
            "input_data": self.input_data,
            "assigned_to": self.assigned_to,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds
        }
    
    def assign(self, role_name: str):
        """分配任务"""
        self.assigned_to = role_name
        self.status = TaskStatus.ASSIGNED
        self.assigned_at = datetime.now()
    
    def start(self):
        """开始执行任务"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.last_activity = datetime.now()
    
    def complete(self, result: Dict[str, Any]):
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
    
    def fail(self, error: str):
        """任务失败"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        self.last_activity = datetime.now()
    
    def check_timeout(self) -> bool:
        """检查任务是否超时"""
        if self.timeout_seconds is None or self.status != TaskStatus.IN_PROGRESS:
            return False
        
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        return elapsed > self.timeout_seconds
    
    def cancel(self):
        """取消任务"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        """初始化任务管理器"""
        self.tasks: Dict[str, Task] = {}
        # 使用优先级队列：(-priority, created_at, task_id)
        # 负数优先级是因为heapq是最小堆，我们需要最大优先级在前
        self.task_queue: List[tuple] = []  # 待分配任务优先级队列
        self._task_queue_set: set = set()  # 用于快速查找任务是否在队列中
    
    def create_task(self,
                   task_type: str,
                   input_data: Dict[str, Any],
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   dependencies: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> Task:
        """
        创建任务
        
        Args:
            task_type: 任务类型
            input_data: 任务输入
            priority: 优先级
            dependencies: 依赖任务ID列表
            metadata: 元数据
        
        Returns:
            创建的任务对象
        """
        task = Task(
            task_type=task_type,
            input_data=input_data,
            priority=priority,
            dependencies=dependencies,
            metadata=metadata
        )
        
        self.tasks[task.id] = task
        
        # 如果没有依赖，加入优先级队列
        if not dependencies or all(dep_id in self.tasks and 
                                   self.tasks[dep_id].status == TaskStatus.COMPLETED 
                                   for dep_id in dependencies):
            self._add_to_queue(task)
        
        logger.info(f"创建任务: {task.id[:8]}... 类型: {task.task_type} 优先级: {task.priority.value}")
        return task
    
    def _add_to_queue(self, task: Task):
        """将任务添加到优先级队列"""
        if task.id not in self._task_queue_set:
            # 使用负数优先级，因为heapq是最小堆
            heapq.heappush(self.task_queue, (-task.priority.value, task.created_at.timestamp(), task.id))
            self._task_queue_set.add(task.id)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """根据状态获取任务列表"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_role(self, role_name: str) -> List[Task]:
        """获取分配给指定角色的任务"""
        return [task for task in self.tasks.values() 
                if task.assigned_to == role_name]
    
    def assign_task(self, task_id: str, role_name: str) -> bool:
        """
        分配任务给角色
        
        Args:
            task_id: 任务ID
            role_name: 角色名称
        
        Returns:
            是否分配成功
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        # 检查依赖是否完成
        if task.dependencies:
            for dep_id in task.dependencies:
                dep_task = self.get_task(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    return False
        
        task.assign(role_name)
        self._remove_from_queue(task_id)
        
        logger.info(f"任务分配: {task_id[:8]}... -> {role_name}")
        return True
    
    def _remove_from_queue(self, task_id: str):
        """从队列中移除任务"""
        if task_id in self._task_queue_set:
            # 重建队列（移除指定任务）
            new_queue = [(p, t, tid) for p, t, tid in self.task_queue if tid != task_id]
            heapq.heapify(new_queue)
            self.task_queue = new_queue
            self._task_queue_set.discard(task_id)
    
    def get_next_task(self, role_name: Optional[str] = None) -> Optional[Task]:
        """
        获取下一个待分配的任务（使用优先级队列）
        
        Args:
            role_name: 如果指定，只返回适合该角色的任务
        
        Returns:
            下一个任务
        """
        # 从优先级队列中获取任务
        while self.task_queue:
            # 弹出优先级最高的任务
            _, _, task_id = heapq.heappop(self.task_queue)
            self._task_queue_set.discard(task_id)
            
            task = self.tasks.get(task_id)
            if not task:
                continue
            
            # 检查任务状态
            if task.status != TaskStatus.PENDING:
                continue
            
            # 如果指定了角色，检查是否匹配
            if role_name:
                # TODO: 根据任务类型和角色能力匹配
                pass
            
            return task
        
        return None
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          result: Optional[Dict] = None, error: Optional[str] = None):
        """更新任务状态"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if status == TaskStatus.IN_PROGRESS:
            task.start()
        elif status == TaskStatus.COMPLETED:
            task.complete(result or {})
            # 检查是否有依赖此任务的其他任务
            self._check_dependent_tasks(task_id)
        elif status == TaskStatus.FAILED:
            task.fail(error or "未知错误")
            # 检查是否可以重试
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.error = None
                self._add_to_queue(task)
                logger.warning(f"任务失败，准备重试 ({task.retry_count}/{task.max_retries}): {task_id[:8]}...")
            else:
                logger.error(f"任务失败，已达最大重试次数: {task_id[:8]}... 错误: {error}")
        
        return True
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """检查依赖已完成任务的其他任务"""
        for task in self.tasks.values():
            if completed_task_id in task.dependencies:
                # 检查所有依赖是否都完成
                all_deps_completed = all(
                    dep_id in self.tasks and 
                    self.tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                
                if all_deps_completed and task.status == TaskStatus.PENDING:
                    self._add_to_queue(task)
                    logger.info(f"依赖完成，任务加入队列: {task.id[:8]}...")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total": len(self.tasks),
            "by_status": {},
            "by_priority": {},
            "pending_count": len(self.task_queue),
            "retry_count": sum(1 for t in self.tasks.values() if t.retry_count > 0)
        }
        
        for status in TaskStatus:
            stats["by_status"][status.value] = len(
                self.get_tasks_by_status(status)
            )
        
        for priority in TaskPriority:
            stats["by_priority"][priority.value] = len([
                t for t in self.tasks.values() 
                if t.priority == priority
            ])
        
        return stats


if __name__ == "__main__":
    # 测试代码
    manager = TaskManager()
    
    # 创建任务
    task1 = manager.create_task(
        task_type="create_plan",
        input_data={"requirements": "开发系统", "timeline": "2个月"},
        priority=TaskPriority.HIGH
    )
    
    print(f"创建任务: {task1.id}")
    print(f"状态: {task1.status.value}")
    
    # 分配任务
    manager.assign_task(task1.id, "项目经理")
    print(f"分配后状态: {task1.status.value}")
    
    # 获取统计
    stats = manager.get_statistics()
    print(f"\n统计信息: {json.dumps(stats, ensure_ascii=False, indent=2)}")


