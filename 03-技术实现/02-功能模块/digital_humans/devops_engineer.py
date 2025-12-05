#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运维工程师数字人
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any
import json


class DevOpsEngineer(BaseDigitalHuman):
    """运维工程师数字人"""
    
    def __init__(self, name: str = "运维工程师-001", **kwargs):
        super().__init__(
            name=name,
            role="运维工程师",
            department="交付运营中心",
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一位专业的运维工程师，擅长：
1. 系统监控和故障处理
2. 性能优化
3. 安全维护
4. 自动化运维

你的工作原则：
- 快速响应故障
- 预防为主
- 自动化优先
- 文档完整"""
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)
        
        try:
            if task_type == 'monitor_system':
                return self.monitor_system(task)
            elif task_type == 'handle_incident':
                return self.handle_incident(task)
            elif task_type == 'optimize_performance':
                return self.optimize_performance(task)
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
    
    def monitor_system(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """监控系统"""
        metrics = task.get('input', {}).get('metrics', {})
        
        prompt = f"""请分析以下系统监控数据：

监控指标：
{json.dumps(metrics, ensure_ascii=False, indent=2)}

请输出：
1. 系统健康状态评估
2. 异常指标识别
3. 潜在风险预警
4. 建议的处理措施"""
        
        analysis = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "analysis": analysis,
                "format": "markdown"
            }
        }
    
    def handle_incident(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理故障"""
        incident = task.get('input', {}).get('incident', '')
        logs = task.get('input', {}).get('logs', '')
        
        prompt = f"""请处理以下系统故障：

故障描述：
{incident}

相关日志：
{logs}

请输出：
1. 故障原因分析
2. 紧急处理步骤
3. 根本解决方案
4. 预防措施"""
        
        solution = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "solution": solution,
                "format": "markdown"
            }
        }
    
    def optimize_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """优化系统性能"""
        performance_data = task.get('input', {}).get('performance_data', {})
        
        prompt = f"""请优化系统性能：

性能数据：
{json.dumps(performance_data, ensure_ascii=False, indent=2)}

请输出：
1. 性能瓶颈分析
2. 优化方案（至少3个）
3. 实施步骤
4. 预期效果"""
        
        optimization = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "optimization": optimization,
                "format": "markdown"
            }
        }


