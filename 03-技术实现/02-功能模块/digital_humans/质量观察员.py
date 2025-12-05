#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量观察员数字人
负责质量监控和问题识别
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class QualityObserver(BaseDigitalHuman):
    """质量观察员数字人"""
    
    def __init__(self, name: str = "质量观察员-001", **kwargs):
        super().__init__(
            name=name,
            role="质量观察员",
            department="业务支持中心",
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是质量观察员，负责项目执行过程中的质量监控和问题识别。

你的核心职责：
1. 质量监控：监控项目执行质量
2. 问题识别：识别质量问题和技术问题
3. 质量评估：评估工作成果质量
4. 质量报告：生成质量评估报告

你的工作原则：
- 客观公正，基于事实评估
- 及时反馈，快速识别问题
- 持续改进，提出改进建议
- 预防为主，提前识别风险"""
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)
        
        try:
            if task_type == 'monitor_quality':
                return self.monitor_quality(task)
            elif task_type == 'identify_issues':
                return self.identify_issues(task)
            elif task_type == 'assess_quality':
                return self.assess_quality(task)
            elif task_type == 'generate_report':
                return self.generate_report(task)
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
    
    def monitor_quality(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """监控质量"""
        input_data = task.get('input', {})
        work_product = input_data.get('work_product', '')
        
        prompt = f"""作为质量观察员，请监控以下工作成果的质量：

工作成果：{work_product}

请评估：
1. 质量指标
2. 潜在问题
3. 改进建议"""
        
        assessment = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "quality_assessment": assessment,
                "issues": [],
                "suggestions": []
            }
        }
    
    def identify_issues(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """识别问题"""
        input_data = task.get('input', {})
        work_data = input_data.get('work_data', '')
        
        prompt = f"""作为质量观察员，请识别以下工作中的问题：

工作数据：{work_data}

请识别：
1. 质量问题
2. 技术问题
3. 流程问题
4. 风险问题"""
        
        issues = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "issues": issues,
                "severity": {},
                "solutions": []
            }
        }
    
    def assess_quality(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """评估质量"""
        input_data = task.get('input', {})
        deliverable = input_data.get('deliverable', '')
        
        prompt = f"""作为质量观察员，请评估以下交付物的质量：

交付物：{deliverable}

请评估：
1. 质量评分
2. 质量维度分析
3. 质量等级
4. 改进建议"""
        
        assessment = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "quality_score": 0,
                "assessment": assessment,
                "dimensions": {}
            }
        }
    
    def generate_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成质量报告"""
        input_data = task.get('input', {})
        period = input_data.get('period', '')
        quality_data = input_data.get('quality_data', {})
        
        prompt = f"""作为质量观察员，请生成以下时间段的质量报告：

时间段：{period}
质量数据：{json.dumps(quality_data, ensure_ascii=False)}

请生成：
1. 质量概况
2. 质量问题统计
3. 质量趋势分析
4. 改进建议"""
        
        report = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "report": report
            }
        }
    
    def update_status(self, status: str, task: Optional[Dict] = None):
        """更新状态"""
        self.status = status
        if task:
            self.current_task = task

