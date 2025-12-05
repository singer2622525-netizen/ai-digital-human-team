#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务执行历史查询模块
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .task_manager import TaskManager, Task, TaskStatus
import logging

logger = logging.getLogger(__name__)


class TaskHistoryManager:
    """任务历史管理器"""
    
    def __init__(self, task_manager: TaskManager):
        """
        初始化任务历史管理器
        
        Args:
            task_manager: 任务管理器实例
        """
        self.task_manager = task_manager
    
    def get_task_history(self,
                        task_id: Optional[str] = None,
                        role_name: Optional[str] = None,
                        task_type: Optional[str] = None,
                        status: Optional[TaskStatus] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        limit: int = 100) -> List[Dict]:
        """
        获取任务历史
        
        Args:
            task_id: 任务ID（可选）
            role_name: 角色名称（可选）
            task_type: 任务类型（可选）
            status: 任务状态（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            limit: 返回数量限制
        
        Returns:
            任务历史列表
        """
        tasks = []
        
        # 如果指定了task_id，直接返回该任务
        if task_id:
            task = self.task_manager.get_task(task_id)
            if task:
                tasks.append(task)
        else:
            # 获取所有任务
            all_tasks = list(self.task_manager.tasks.values())
            
            # 过滤
            for task in all_tasks:
                # 角色过滤
                if role_name and task.assigned_to != role_name:
                    continue
                
                # 任务类型过滤
                if task_type and task.task_type != task_type:
                    continue
                
                # 状态过滤
                if status and task.status != status:
                    continue
                
                # 日期过滤
                if start_date and task.created_at < start_date:
                    continue
                if end_date and task.created_at > end_date:
                    continue
                
                tasks.append(task)
        
        # 按创建时间倒序排序
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # 限制数量
        tasks = tasks[:limit]
        
        # 转换为字典
        history = []
        for task in tasks:
            history.append({
                "task_id": task.id,
                "task_type": task.task_type,
                "role_name": task.assigned_to,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "assigned_at": task.assigned_at.isoformat() if task.assigned_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "duration_seconds": self._calculate_duration(task),
                "result_summary": self._get_result_summary(task),
                "error": task.error,
                "retry_count": task.retry_count
            })
        
        logger.info(f"查询任务历史: {len(history)} 条记录")
        return history
    
    def _calculate_duration(self, task: Task) -> Optional[float]:
        """计算任务执行时长（秒）"""
        if task.started_at and task.completed_at:
            return (task.completed_at - task.started_at).total_seconds()
        elif task.started_at:
            # 进行中的任务，计算到现在的时长
            return (datetime.now() - task.started_at).total_seconds()
        return None
    
    def _get_result_summary(self, task: Task) -> Optional[str]:
        """获取结果摘要"""
        if task.result:
            if isinstance(task.result, dict):
                # 提取关键信息
                output = task.result.get('output', {})
                if isinstance(output, dict):
                    plan = output.get('plan', '')
                    if plan:
                        return plan[:200] + "..." if len(plan) > 200 else plan
                return str(task.result)[:200]
            return str(task.result)[:200]
        return None
    
    def get_statistics_by_role(self,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict[str, Dict]:
        """
        按角色统计任务历史
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            角色统计字典
        """
        all_tasks = list(self.task_manager.tasks.values())
        
        # 日期过滤
        if start_date or end_date:
            filtered_tasks = []
            for task in all_tasks:
                if start_date and task.created_at < start_date:
                    continue
                if end_date and task.created_at > end_date:
                    continue
                filtered_tasks.append(task)
            all_tasks = filtered_tasks
        
        # 按角色统计
        role_stats = {}
        
        for task in all_tasks:
            role = task.assigned_to or "未分配"
            
            if role not in role_stats:
                role_stats[role] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0,
                    "in_progress": 0,
                    "total_duration": 0.0,
                    "avg_duration": 0.0,
                    "retry_count": 0
                }
            
            stats = role_stats[role]
            stats["total"] += 1
            
            if task.status == TaskStatus.COMPLETED:
                stats["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                stats["failed"] += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                stats["in_progress"] += 1
            
            duration = self._calculate_duration(task)
            if duration:
                stats["total_duration"] += duration
            
            stats["retry_count"] += task.retry_count
        
        # 计算平均时长
        for role, stats in role_stats.items():
            if stats["completed"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["completed"]
        
        return role_stats
    
    def get_statistics_by_task_type(self,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Dict]:
        """
        按任务类型统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            任务类型统计字典
        """
        all_tasks = list(self.task_manager.tasks.values())
        
        # 日期过滤
        if start_date or end_date:
            filtered_tasks = []
            for task in all_tasks:
                if start_date and task.created_at < start_date:
                    continue
                if end_date and task.created_at > end_date:
                    continue
                filtered_tasks.append(task)
            all_tasks = filtered_tasks
        
        # 按任务类型统计
        type_stats = {}
        
        for task in all_tasks:
            task_type = task.task_type
            
            if task_type not in type_stats:
                type_stats[task_type] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0,
                    "avg_duration": 0.0,
                    "total_duration": 0.0
                }
            
            stats = type_stats[task_type]
            stats["total"] += 1
            
            if task.status == TaskStatus.COMPLETED:
                stats["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                stats["failed"] += 1
            
            duration = self._calculate_duration(task)
            if duration:
                stats["total_duration"] += duration
        
        # 计算平均时长
        for task_type, stats in type_stats.items():
            if stats["completed"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["completed"]
        
        return type_stats
    
    def get_recent_tasks(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """
        获取最近的任务
        
        Args:
            hours: 最近多少小时
            limit: 返回数量限制
        
        Returns:
            任务列表
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        return self.get_task_history(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def get_failed_tasks(self, limit: int = 50) -> List[Dict]:
        """
        获取失败的任务
        
        Args:
            limit: 返回数量限制
        
        Returns:
            失败任务列表
        """
        return self.get_task_history(
            status=TaskStatus.FAILED,
            limit=limit
        )
    
    def get_performance_report(self,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict:
        """
        生成性能报告
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            性能报告字典
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        # 获取统计数据
        role_stats = self.get_statistics_by_role(start_date, end_date)
        type_stats = self.get_statistics_by_task_type(start_date, end_date)
        
        # 总体统计
        all_tasks = self.get_task_history(start_date=start_date, end_date=end_date, limit=10000)
        
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t['status'] == 'completed'])
        failed_tasks = len([t for t in all_tasks if t['status'] == 'failed'])
        
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 计算平均执行时长
        durations = [t['duration_seconds'] for t in all_tasks if t['duration_seconds']]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": round(success_rate, 2),
                "avg_duration_seconds": round(avg_duration, 2)
            },
            "by_role": role_stats,
            "by_task_type": type_stats
        }

