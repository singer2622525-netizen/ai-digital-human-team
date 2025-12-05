#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量操作模块
"""

from typing import List, Dict, Any, Optional
from .export import Exporter
import logging

logger = logging.getLogger(__name__)


class BatchOperations:
    """批量操作管理器"""
    
    def __init__(self, task_manager, scheduler=None):
        """
        初始化批量操作管理器
        
        Args:
            task_manager: 任务管理器实例
            scheduler: 任务调度器实例（可选）
        """
        self.task_manager = task_manager
        self.scheduler = scheduler
    
    def batch_create_tasks(self, tasks_data: List[Dict[str, Any]]) -> List[str]:
        """
        批量创建任务
        
        Args:
            tasks_data: 任务数据列表，每个元素包含 task_type, input_data, priority 等
        
        Returns:
            创建的任务ID列表
        """
        task_ids = []
        
        for task_data in tasks_data:
            try:
                task = self.task_manager.create_task(**task_data)
                task_ids.append(task.id)
                logger.info(f"批量创建任务: {task.id[:8]}...")
            except Exception as e:
                logger.error(f"批量创建任务失败: {e}")
        
        # 自动分配
        if self.scheduler:
            self.scheduler.auto_assign_pending_tasks()
        
        logger.info(f"批量创建完成: {len(task_ids)}/{len(tasks_data)} 个任务")
        return task_ids
    
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
            try:
                if self.task_manager.assign_task(task_id, role_name):
                    success_count += 1
            except Exception as e:
                logger.error(f"批量分配任务失败 {task_id[:8]}...: {e}")
        
        logger.info(f"批量分配完成: {success_count}/{len(assignments)} 个任务")
        return success_count
    
    def batch_execute_tasks(self, task_ids: List[str], max_concurrent: int = 3) -> Dict[str, Any]:
        """
        批量执行任务
        
        Args:
            task_ids: 任务ID列表
            max_concurrent: 最大并发数
        
        Returns:
            执行结果统计
        """
        if not self.scheduler:
            return {"error": "调度器未设置"}
        
        results = {
            "total": len(task_ids),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        # 简单实现：顺序执行（可以改进为并发）
        for task_id in task_ids:
            try:
                result = self.scheduler.execute_task(task_id)
                if result.get("success"):
                    results["success"] += 1
                else:
                    results["failed"] += 1
                results["results"].append({
                    "task_id": task_id,
                    "success": result.get("success", False),
                    "error": result.get("error")
                })
            except Exception as e:
                results["failed"] += 1
                results["results"].append({
                    "task_id": task_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"批量执行完成: 成功 {results['success']}/{results['total']}")
        return results
    
    def batch_update_status(self, updates: List[tuple]) -> int:
        """
        批量更新任务状态
        
        Args:
            updates: (task_id, status, result, error) 元组列表
        
        Returns:
            成功更新的任务数
        """
        success_count = 0
        
        for update in updates:
            task_id = update[0]
            status = update[1]
            result = update[2] if len(update) > 2 else None
            error = update[3] if len(update) > 3 else None
            
            try:
                if self.task_manager.update_task_status(task_id, status, result, error):
                    success_count += 1
            except Exception as e:
                logger.error(f"批量更新状态失败 {task_id[:8]}...: {e}")
        
        logger.info(f"批量更新完成: {success_count}/{len(updates)} 个任务")
        return success_count
    
    def export_tasks(self, file_path: str, format: str = "json", 
                    filters: Optional[Dict] = None) -> bool:
        """
        导出任务
        
        Args:
            file_path: 文件路径
            format: 格式 (json, csv)
            filters: 过滤条件
        
        Returns:
            是否成功
        """
        # 获取任务
        if filters:
            # 应用过滤条件
            tasks = []
            all_tasks = list(self.task_manager.tasks.values())
            for task in all_tasks:
                if filters.get('status') and task.status.value != filters['status']:
                    continue
                if filters.get('role') and task.assigned_to != filters['role']:
                    continue
                tasks.append(task.to_dict())
        else:
            tasks = [task.to_dict() for task in self.task_manager.tasks.values()]
        
        # 导出
        if format.lower() == "json":
            return Exporter.export_tasks_to_json(tasks, file_path)
        elif format.lower() == "csv":
            return Exporter.export_tasks_to_csv(tasks, file_path)
        else:
            logger.error(f"不支持的格式: {format}")
            return False

