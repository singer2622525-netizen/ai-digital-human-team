#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统架构师数字人
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any
import json
from datetime import datetime


class SystemArchitect(BaseDigitalHuman):
    """系统架构师数字人"""
    
    def __init__(self, name: str = "架构师-001", **kwargs):
        super().__init__(
            name=name,
            role="系统架构师",
            department="解决方案中心",
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一位资深系统架构师，擅长：
1. 设计系统整体技术架构
2. 评估和选择技术方案
3. 制定技术开发规范
4. 解决关键技术难题

你的工作原则：
- 架构清晰、可扩展
- 技术选型务实
- 考虑性能和成本
- 文档完整规范"""
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)
        
        try:
            if task_type == 'design_architecture':
                return self.design_architecture(task)
            elif task_type == 'evaluate_technology':
                return self.evaluate_technology(task)
            elif task_type == 'create_standards':
                return self.create_standards(task)
            elif task_type == 'solve_problem':
                return self.solve_problem(task)
            else:
                return {
                    "success": False,
                    "error": f"未知任务类型: {task_type}"
                }
        except Exception as e:
            self.update_status('error', task)
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.update_status('idle')
    
    def design_architecture(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """设计系统架构"""
        requirements = task.get('input', {}).get('requirements', '')
        constraints = task.get('input', {}).get('constraints', '')
        
        prompt = f"""请设计系统技术架构：

业务需求：
{requirements}

技术约束：
{constraints}

请输出：
1. 整体架构图（用Mermaid格式描述）
2. 技术栈选型（前端、后端、数据库等）
3. 模块划分
4. 接口设计原则
5. 部署架构"""
        
        architecture = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "architecture": architecture,
                "format": "markdown"
            }
        }
    
    def evaluate_technology(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """评估技术方案"""
        options = task.get('input', {}).get('options', [])
        context = task.get('input', {}).get('context', '')
        
        prompt = f"""请评估以下技术方案：

技术选项：
{json.dumps(options, ensure_ascii=False, indent=2)}

应用场景：
{context}

请输出：
1. 各方案优缺点对比
2. 推荐方案及理由
3. 风险评估
4. 实施建议"""
        
        evaluation = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "evaluation": evaluation,
                "format": "markdown"
            }
        }
    
    def create_standards(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """制定技术规范"""
        standard_type = task.get('input', {}).get('type', 'code')  # code, api, database
        context = task.get('input', {}).get('context', '')
        
        prompt = f"""请制定{standard_type}技术规范：

规范类型：{standard_type}
应用场景：{context}

请输出：
1. 规范目的和适用范围
2. 具体规范条目（至少10条）
3. 示例代码/文档
4. 检查清单"""
        
        standards = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "standards": standards,
                "type": standard_type,
                "format": "markdown"
            }
        }
    
    def solve_problem(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """解决技术问题"""
        problem = task.get('input', {}).get('problem', '')
        context = task.get('input', {}).get('context', '')
        
        prompt = f"""请解决以下技术问题：

问题描述：
{problem}

技术背景：
{context}

请输出：
1. 问题分析
2. 解决方案（至少2个）
3. 推荐方案及实施步骤
4. 注意事项"""
        
        solution = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "solution": solution,
                "format": "markdown"
            }
        }


if __name__ == "__main__":
    # 测试架构师
    architect = SystemArchitect()
    
    # 测试设计架构
    task = {
        "type": "design_architecture",
        "input": {
            "requirements": "开发一个数字人管理平台，需要支持多角色协作、任务分配、进度跟踪",
            "constraints": "使用Python后端、Flask框架、本地部署"
        }
    }
    
    print("=" * 60)
    print("测试：设计系统架构")
    print("=" * 60)
    result = architect.execute_task(task)
    print(json.dumps(result, ensure_ascii=False, indent=2))

