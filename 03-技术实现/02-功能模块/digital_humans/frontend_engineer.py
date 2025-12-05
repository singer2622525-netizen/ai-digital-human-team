#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端工程师数字人
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any
import json


class FrontendEngineer(BaseDigitalHuman):
    """前端工程师数字人"""
    
    def __init__(self, name: str = "前端工程师-001", **kwargs):
        super().__init__(
            name=name,
            role="前端工程师",
            department="研发中心",
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一位专业的前端工程师，擅长：
1. 实现用户界面和交互
2. 优化前端性能
3. 确保跨平台兼容性
4. 与后端API对接

你的工作原则：
- 代码规范、可维护
- 用户体验优先
- 性能优化
- 响应式设计"""
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)
        
        try:
            if task_type == 'implement_ui':
                return self.implement_ui(task)
            elif task_type == 'optimize_performance':
                return self.optimize_performance(task)
            elif task_type == 'fix_bug':
                return self.fix_bug(task)
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
    
    def implement_ui(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """实现UI界面"""
        design = task.get('input', {}).get('design', '')
        requirements = task.get('input', {}).get('requirements', '')
        
        prompt = f"""请根据设计稿实现前端界面：

设计要求：
{design}

功能需求：
{requirements}

请输出：
1. HTML结构
2. CSS样式（使用现代CSS特性）
3. JavaScript交互逻辑
4. 响应式设计说明"""
        
        code = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "code": code,
                "format": "html/css/js"
            }
        }
    
    def optimize_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """优化性能"""
        code = task.get('input', {}).get('code', '')
        metrics = task.get('input', {}).get('metrics', {})
        
        prompt = f"""请优化以下前端代码的性能：

代码：
{code}

性能指标：
{json.dumps(metrics, ensure_ascii=False)}

请输出：
1. 性能问题分析
2. 优化方案
3. 优化后的代码
4. 预期性能提升"""
        
        optimization = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "optimization": optimization,
                "format": "markdown"
            }
        }
    
    def fix_bug(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """修复Bug"""
        bug_description = task.get('input', {}).get('bug_description', '')
        code = task.get('input', {}).get('code', '')
        
        prompt = f"""请修复以下前端Bug：

Bug描述：
{bug_description}

相关代码：
{code}

请输出：
1. Bug原因分析
2. 修复方案
3. 修复后的代码
4. 测试建议"""
        
        fix = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "fix": fix,
                "format": "markdown"
            }
        }


