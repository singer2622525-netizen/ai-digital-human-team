#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化工具模块
用于生成任务依赖图、工作流图等
"""

from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class TaskVisualizer:
    """任务可视化器"""
    
    @staticmethod
    def generate_dependency_graph(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成任务依赖图数据
        
        Args:
            tasks: 任务列表
        
        Returns:
            图数据（节点和边）
        """
        nodes = []
        edges = []
        
        # 创建节点
        for task in tasks:
            node = {
                "id": task.get('id', ''),
                "label": task.get('task_type', 'unknown'),
                "status": task.get('status', 'pending'),
                "role": task.get('assigned_to', '未分配'),
                "priority": task.get('priority', 2)
            }
            nodes.append(node)
        
        # 创建边（依赖关系）
        task_dict = {task.get('id'): task for task in tasks}
        
        for task in tasks:
            task_id = task.get('id')
            dependencies = task.get('dependencies', [])
            
            for dep_id in dependencies:
                if dep_id in task_dict:
                    edge = {
                        "from": dep_id,
                        "to": task_id,
                        "type": "dependency"
                    }
                    edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    @staticmethod
    def generate_mermaid_diagram(tasks: List[Dict[str, Any]]) -> str:
        """
        生成Mermaid流程图代码
        
        Args:
            tasks: 任务列表
        
        Returns:
            Mermaid代码
        """
        lines = ["graph TD"]
        
        # 如果没有任务，显示提示节点
        if not tasks:
            lines.append('    Empty["暂无任务\\n请先创建任务"]:::empty')
            lines.append("")
            lines.append("    classDef empty fill:#fff3cd,stroke:#856404,stroke-width:2px")
            lines.append("    classDef completed fill:#d4edda,stroke:#155724")
            lines.append("    classDef failed fill:#f8d7da,stroke:#721c24")
            lines.append("    classDef inprogress fill:#d1ecf1,stroke:#0c5460")
            return "\n".join(lines)
        
        task_dict = {task.get('id'): task for task in tasks}
        
        # 创建节点
        for task in tasks:
            task_id = task.get('id', '')[:8]
            task_type = task.get('task_type', 'unknown')
            status = task.get('status', 'pending')
            role = task.get('assigned_to', '未分配')
            
            # 根据状态设置样式
            style = ""
            if status == "completed":
                style = ":::completed"
            elif status == "failed":
                style = ":::failed"
            elif status == "in_progress":
                style = ":::inprogress"
            
            label = f"{task_type}\\n{role}"
            lines.append(f'    {task_id}["{label}"]{style}')
        
        # 创建边（依赖关系）
        for task in tasks:
            task_id = task.get('id', '')[:8]
            dependencies = task.get('dependencies', [])
            
            for dep_id in dependencies:
                if dep_id in task_dict:
                    dep_id_short = dep_id[:8]
                    lines.append(f"    {dep_id_short} --> {task_id}")
        
        # 添加样式定义
        lines.append("")
        lines.append("    classDef completed fill:#d4edda,stroke:#155724")
        lines.append("    classDef failed fill:#f8d7da,stroke:#721c24")
        lines.append("    classDef inprogress fill:#d1ecf1,stroke:#0c5460")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_workflow_mermaid(workflow: Dict[str, Any]) -> str:
        """
        生成工作流的Mermaid流程图
        
        Args:
            workflow: 工作流数据
        
        Returns:
            Mermaid代码
        """
        lines = [f"graph TD"]
        lines.append(f'    Start([开始]) --> Step1')
        
        steps = workflow.get('steps', [])
        
        for i, step in enumerate(steps):
            step_id = f"Step{i+1}"
            step_type = step.get('step_type', 'unknown')
            status = step.get('status', 'pending')
            role = step.get('role', '未知')
            
            label = f"{step_type}\\n{role}"
            
            # 根据状态设置样式
            style = ""
            if status == "completed":
                style = ":::completed"
            elif status == "failed":
                style = ":::failed"
            elif status == "in_progress":
                style = ":::inprogress"
            
            lines.append(f'    {step_id}["{label}"]{style}')
            
            # 连接步骤
            if i == 0:
                lines.append(f"    Start --> {step_id}")
            else:
                prev_step_id = f"Step{i}"
                # 检查依赖
                deps = step.get('dependencies', [])
                if deps:
                    for dep in deps:
                        dep_idx = next((j for j, s in enumerate(steps) if s.get('id') == dep), None)
                        if dep_idx is not None:
                            dep_step_id = f"Step{dep_idx+1}"
                            lines.append(f"    {dep_step_id} --> {step_id}")
                else:
                    lines.append(f"    {prev_step_id} --> {step_id}")
        
        # 添加结束节点
        if steps:
            last_step_id = f"Step{len(steps)}"
            lines.append(f"    {last_step_id} --> End([结束])")
        
        # 添加样式定义
        lines.append("")
        lines.append("    classDef completed fill:#d4edda,stroke:#155724")
        lines.append("    classDef failed fill:#f8d7da,stroke:#721c24")
        lines.append("    classDef inprogress fill:#d1ecf1,stroke:#0c5460")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_d3_json(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成D3.js格式的图数据
        
        Args:
            tasks: 任务列表
        
        Returns:
            D3.js格式的数据
        """
        graph = TaskVisualizer.generate_dependency_graph(tasks)
        
        # 转换为D3.js格式
        d3_data = {
            "nodes": [
                {
                    "id": node["id"],
                    "name": node["label"],
                    "group": 1,
                    "status": node["status"],
                    "role": node["role"],
                    "priority": node["priority"]
                }
                for node in graph["nodes"]
            ],
            "links": [
                {
                    "source": edge["from"],
                    "target": edge["to"],
                    "value": 1
                }
                for edge in graph["edges"]
            ]
        }
        
        return d3_data

