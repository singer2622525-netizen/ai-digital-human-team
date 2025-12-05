#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流暂停/恢复功能
"""

from typing import Dict, Optional, List
from .workflow_engine import WorkflowEngine, Workflow, WorkflowStatus
from .task_manager import TaskManager, TaskStatus
import logging

logger = logging.getLogger(__name__)


class WorkflowPauseManager:
    """工作流暂停管理器"""
    
    def __init__(self, workflow_engine: WorkflowEngine):
        """
        初始化暂停管理器
        
        Args:
            workflow_engine: 工作流引擎实例
        """
        self.workflow_engine = workflow_engine
        self.paused_workflows: Dict[str, Dict] = {}  # workflow_id -> 暂停信息
    
    def pause_workflow(self, workflow_id: str, reason: str = "") -> bool:
        """
        暂停工作流
        
        Args:
            workflow_id: 工作流ID
            reason: 暂停原因
        
        Returns:
            是否成功暂停
        """
        workflow = self.workflow_engine.get_workflow(workflow_id)
        if not workflow:
            return False
        
        if workflow.status != WorkflowStatus.RUNNING:
            logger.warning(f"工作流 {workflow_id[:8]}... 不在运行状态，无法暂停")
            return False
        
        # 保存暂停信息
        self.paused_workflows[workflow_id] = {
            "reason": reason,
            "paused_at": datetime.now().isoformat(),
            "running_steps": [
                step.step_id for step in workflow.steps 
                if step.status == TaskStatus.IN_PROGRESS
            ]
        }
        
        # 更新工作流状态
        workflow.status = WorkflowStatus.PAUSED
        
        logger.info(f"工作流已暂停: {workflow_id[:8]}... 原因: {reason}")
        return True
    
    def resume_workflow(self, workflow_id: str) -> bool:
        """
        恢复工作流
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            是否成功恢复
        """
        workflow = self.workflow_engine.get_workflow(workflow_id)
        if not workflow:
            return False
        
        if workflow.status != WorkflowStatus.PAUSED:
            logger.warning(f"工作流 {workflow_id[:8]}... 不在暂停状态，无法恢复")
            return False
        
        # 移除暂停信息
        if workflow_id in self.paused_workflows:
            del self.paused_workflows[workflow_id]
        
        # 恢复工作流状态
        workflow.status = WorkflowStatus.RUNNING
        
        # 更新工作流（检查是否有新步骤可以执行）
        self.workflow_engine.update_workflow(workflow_id)
        
        logger.info(f"工作流已恢复: {workflow_id[:8]}...")
        return True
    
    def get_paused_workflows(self) -> List[Dict]:
        """获取所有暂停的工作流"""
        paused = []
        for workflow_id, pause_info in self.paused_workflows.items():
            workflow = self.workflow_engine.get_workflow(workflow_id)
            if workflow:
                paused.append({
                    "workflow_id": workflow_id,
                    "workflow_name": workflow.name,
                    "pause_info": pause_info
                })
        return paused


from datetime import datetime

