#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度器 - 负责将任务分配给合适的数字人
"""

from typing import Dict, List, Optional, Any
from .task_manager import TaskManager, Task, TaskStatus
import sys
import os
import logging

# 添加数字人模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

from digital_humans import (
    ProjectManager, SystemArchitect, FrontendEngineer,
    BackendEngineer, DevOpsEngineer
)
import json


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, task_manager: TaskManager):
        """
        初始化任务调度器
        
        Args:
            task_manager: 任务管理器实例
        """
        self.task_manager = task_manager
        
        # 角色映射（任务类型 -> 角色名称）
        self.role_mapping = {
            # 项目经理任务
            "create_plan": "项目经理",
            "track_progress": "项目经理",
            "generate_report": "项目经理",
            "identify_risks": "项目经理",
            
            # 系统架构师任务
            "design_architecture": "系统架构师",
            "evaluate_technology": "系统架构师",
            "create_standards": "系统架构师",
            "solve_problem": "系统架构师",
            
            # 前端工程师任务
            "implement_ui": "前端工程师",
            "optimize_performance": "前端工程师",
            "fix_bug": "前端工程师",
            
            # 后端工程师任务
            "implement_api": "后端工程师",
            "optimize_query": "后端工程师",
            
            # 运维工程师任务
            "monitor_system": "运维工程师",
            "handle_incident": "运维工程师",
        }
        
        # 数字人实例池（按需创建）
        self.digital_humans: Dict[str, Any] = {}
    
    def _get_digital_human(self, role_name: str):
        """获取数字人实例（懒加载）"""
        if role_name not in self.digital_humans:
            role_classes = {
                "项目经理": ProjectManager,
                "系统架构师": SystemArchitect,
                "前端工程师": FrontendEngineer,
                "后端工程师": BackendEngineer,
                "运维工程师": DevOpsEngineer
            }
            
            role_class = role_classes.get(role_name)
            if role_class:
                self.digital_humans[role_name] = role_class()
        
        return self.digital_humans.get(role_name)
    
    def assign_task(self, task: Task) -> bool:
        """
        分配任务给合适的数字人
        
        Args:
            task: 任务对象
        
        Returns:
            是否分配成功
        """
        # 根据任务类型确定角色
        role_name = self.role_mapping.get(task.task_type)
        if not role_name:
            return False
        
        # 分配任务
        return self.task_manager.assign_task(task.id, role_name)
    
    def auto_assign_pending_tasks(self) -> int:
        """
        自动分配所有待分配的任务
        
        Returns:
            分配的任务数量
        """
        assigned_count = 0
        
        # 获取所有待分配的任务
        pending_tasks = self.task_manager.get_tasks_by_status(TaskStatus.PENDING)
        
        for task in pending_tasks:
            # 检查依赖是否完成
            if task.dependencies:
                all_deps_completed = all(
                    dep_task.status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if (dep_task := self.task_manager.get_task(dep_id))
                )
                if not all_deps_completed:
                    continue
            
            # 分配任务
            if self.assign_task(task):
                assigned_count += 1
        
        return assigned_count
    
    def execute_task(self, task_id: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        执行任务（支持超时）
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒），None表示使用任务默认超时
        
        Returns:
            执行结果
        """
        import time
        import signal
        
        task = self.task_manager.get_task(task_id)
        if not task:
            return {
                "success": False,
                "error": f"任务不存在: {task_id}"
            }
        
        if not task.assigned_to:
            return {
                "success": False,
                "error": "任务未分配"
            }
        
        # 检查任务是否超时
        if task.check_timeout():
            return {
                "success": False,
                "error": f"任务已超时（{task.timeout_seconds}秒）"
            }
        
        # 获取数字人实例
        digital_human = self._get_digital_human(task.assigned_to)
        if not digital_human:
            return {
                "success": False,
                "error": f"找不到数字人: {task.assigned_to}"
            }
        
        # 设置超时
        if timeout:
            task.timeout_seconds = timeout
        
        # 更新任务状态为进行中
        self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        
        start_time = time.time()
        
        try:
            # 执行任务
            task_dict = {
                "type": task.task_type,
                "input": task.input_data
            }
            
            result = digital_human.execute_task(task_dict)
            
            elapsed_time = time.time() - start_time
            
            # 更新任务状态
            if result.get("success"):
                self.task_manager.update_task_status(
                    task_id, 
                    TaskStatus.COMPLETED,
                    result=result
                )
                logger.info(f"任务执行成功: {task_id[:8]}... 耗时: {elapsed_time:.2f}秒")
                
                # 将成功结果沉淀到知识库
                self._save_to_knowledge_base(task, result)
            else:
                self.task_manager.update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error=result.get("error", "未知错误")
                )
                logger.warning(f"任务执行失败: {task_id[:8]}... 错误: {result.get('error')}")
                
                # 将失败经验也沉淀到知识库
                self._save_failure_experience(task, result.get("error", "未知错误"))
            
            return result
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.task_manager.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=str(e)
            )
            logger.error(f"任务执行异常: {task_id[:8]}... 耗时: {elapsed_time:.2f}秒 错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_to_knowledge_base(self, task: Task, result: Dict[str, Any]):
        """将任务结果保存到知识库"""
        try:
            from knowledge.ragflow_integration import KnowledgeBase
            kb = KnowledgeBase()
            
            kb.add_task_result(
                task_id=task.id,
                task_type=task.task_type,
                result=result,
                role_name=task.assigned_to or "未知",
                metadata={
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat()
                }
            )
            logger.info(f"任务结果已保存到知识库: {task.id[:8]}...")
        except Exception as e:
            logger.warning(f"保存任务结果到知识库失败: {e}")
    
    def _save_failure_experience(self, task: Task, error: str):
        """将失败经验保存到知识库"""
        try:
            from knowledge.ragflow_integration import KnowledgeBase
            kb = KnowledgeBase()
            
            experience_content = f"""
任务类型: {task.task_type}
错误信息: {error}
任务输入数据: {json.dumps(task.input_data, ensure_ascii=False)}
"""
            
            kb.add_experience(
                experience_type="failure",
                content=experience_content,
                context=f"任务执行失败，角色: {task.assigned_to}",
                metadata={
                    "task_id": task.id,
                    "task_type": task.task_type,
                    "role_name": task.assigned_to
                }
            )
            logger.info(f"失败经验已保存到知识库: {task.id[:8]}...")
        except Exception as e:
            logger.warning(f"保存失败经验到知识库失败: {e}")
    
    def get_role_workload(self) -> Dict[str, int]:
        """获取各角色的工作负载"""
        workload = {}
        
        for role_name in self.role_mapping.values():
            tasks = self.task_manager.get_tasks_by_role(role_name)
            # 统计进行中的任务数
            workload[role_name] = len([
                t for t in tasks 
                if t.status == TaskStatus.IN_PROGRESS
            ])
        
        return workload


if __name__ == "__main__":
    from task_manager import TaskManager
    
    # 测试
    task_manager = TaskManager()
    scheduler = TaskScheduler(task_manager)
    
    # 创建任务
    task = task_manager.create_task(
        task_type="create_plan",
        input_data={"requirements": "测试", "timeline": "1周"}
    )
    
    print(f"创建任务: {task.id}")
    
    # 自动分配
    scheduler.auto_assign_pending_tasks()
    
    print(f"分配后: {task.assigned_to}")
    print(f"状态: {task.status.value}")


