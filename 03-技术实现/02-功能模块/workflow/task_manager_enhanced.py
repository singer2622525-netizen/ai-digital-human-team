#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器增强功能
- 超时检测
- 批量操作
- 性能优化
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .task_manager import TaskManager, Task, TaskStatus
import logging

logger = logging.getLogger(__name__)


class EnhancedTaskManager(TaskManager):
    """增强版任务管理器"""
    
    def __init__(self):
        super().__init__()
        self.timeout_check_interval = 60  # 超时检查间隔（秒）
        self.last_timeout_check = datetime.now()
    
    def check_timeouts(self) -> List[str]:
        """
        检查所有超时任务
        
        Returns:
            超时的任务ID列表
        """
        now = datetime.now()
        if (now - self.last_timeout_check).total_seconds() < self.timeout_check_interval:
            return []
        
        self.last_timeout_check = now
        timeout_tasks = []
        
        for task in self.tasks.values():
            if task.check_timeout():
                timeout_tasks.append(task.id)
                task.fail(f"任务执行超时（{task.timeout_seconds}秒）")
                logger.warning(f"任务超时: {task.id[:8]}...")
        
        return timeout_tasks
    
    def batch_create_tasks(self, tasks_data: List[Dict[str, Any]]) -> List[Task]:
        """
        批量创建任务
        
        Args:
            tasks_data: 任务数据列表
        
        Returns:
            创建的任务列表
        """
        tasks = []
        for task_data in tasks_data:
            task = self.create_task(**task_data)
            tasks.append(task)
        
        logger.info(f"批量创建 {len(tasks)} 个任务")
        return tasks
    
    def batch_assign_tasks(self, assignments: List[tuple]) -> int:
        """
        批量分配任务
        
        Args:
            assignments: (task_id, role_name) 元组列表
        
        Returns:
            成功分配的任务数
        """
        success_count = 0
        for task_id, role_name in assignments:
            if self.assign_task(task_id, role_name):
                success_count += 1
        
        logger.info(f"批量分配 {success_count}/{len(assignments)} 个任务")
        return success_count
    
    def get_tasks_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Task]:
        """
        根据时间范围获取任务
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            任务列表
        """
        return [
            task for task in self.tasks.values()
            if start_time <= task.created_at <= end_time
        ]
    
    def cleanup_old_tasks(self, days: int = 30) -> int:
        """
        清理旧任务（已完成或失败超过指定天数）
        
        Args:
            days: 保留天数
        
        Returns:
            清理的任务数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at and task.completed_at < cutoff_date:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            self._remove_from_queue(task_id)
        
        logger.info(f"清理了 {len(to_remove)} 个旧任务")
        return len(to_remove)

