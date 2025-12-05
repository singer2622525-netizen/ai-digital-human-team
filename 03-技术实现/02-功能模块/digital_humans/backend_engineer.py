#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端工程师数字人
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any
import json


class BackendEngineer(BaseDigitalHuman):
    """后端工程师数字人"""
    
    def __init__(self, name: str = "后端工程师-001", **kwargs):
        super().__init__(
            name=name,
            role="后端工程师",
            department="研发中心",
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一位专业的后端工程师，擅长：
1. 实现业务逻辑和API
2. 数据库设计和操作
3. 系统性能优化
4. 安全防护

你的工作原则：
- 代码规范、可测试
- API设计RESTful
- 性能和安全并重
- 文档完整清晰"""
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)
        
        try:
            if task_type == 'implement_api':
                return self.implement_api(task)
            elif task_type == 'optimize_query':
                return self.optimize_query(task)
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
    
    def implement_api(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """实现API接口"""
        api_spec = task.get('input', {}).get('api_spec', '')
        requirements = task.get('input', {}).get('requirements', '')
        
        prompt = f"""请实现以下API接口：

API规范：
{api_spec}

业务需求：
{requirements}

请输出：
1. Python代码（使用Flask框架）
2. 数据库模型（如果需要）
3. 请求/响应示例
4. 错误处理逻辑
5. 单元测试建议"""
        
        code = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "code": code,
                "format": "python"
            }
        }
    
    def optimize_query(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """优化数据库查询"""
        query = task.get('input', {}).get('query', '')
        performance_data = task.get('input', {}).get('performance_data', {})
        
        prompt = f"""请优化以下数据库查询：

SQL查询：
{query}

性能数据：
{json.dumps(performance_data, ensure_ascii=False)}

请输出：
1. 性能问题分析
2. 优化方案
3. 优化后的SQL
4. 索引建议
5. 预期性能提升"""
        
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
        error_log = task.get('input', {}).get('error_log', '')
        
        prompt = f"""请修复以下后端Bug：

Bug描述：
{bug_description}

相关代码：
{code}

错误日志：
{error_log}

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


