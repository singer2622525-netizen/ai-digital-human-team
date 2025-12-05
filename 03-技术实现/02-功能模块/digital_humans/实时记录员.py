#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时记录员数字人
负责过程记录和经验提取
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class RealTimeRecorder(BaseDigitalHuman):
    """实时记录员数字人"""

    def __init__(self, name: str = "实时记录员-001", **kwargs):
        super().__init__(
            name=name,
            role="实时记录员",
            department="业务支持中心",
            **kwargs
        )

    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是实时记录员，负责项目执行过程中的实时记录和经验提取。

你的核心职责：
1. 过程记录：记录项目执行过程中的关键事件和决策
2. 经验提取：从项目过程中提取有价值的经验
3. 知识沉淀：将经验转化为可复用的知识
4. 过程文档：生成过程文档和总结报告

你的工作原则：
- 及时记录，不遗漏关键信息
- 客观准确，如实反映过程
- 提炼精华，提取有价值经验
- 便于检索，结构化存储知识"""

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)

        try:
            if task_type == 'record_process':
                return self.record_process(task)
            elif task_type == 'extract_experience':
                return self.extract_experience(task)
            elif task_type == 'generate_summary':
                return self.generate_summary(task)
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

    def record_process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """记录过程"""
        input_data = task.get('input', {})
        event = input_data.get('event', '')
        context = input_data.get('context', '')

        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "context": context,
            "recorded_by": self.name
        }

        return {
            "success": True,
            "output": {
                "record": record
            }
        }

    def extract_experience(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """提取经验"""
        input_data = task.get('input', {})
        process_data = input_data.get('process_data', '')

        prompt = f"""作为实时记录员，请从以下过程数据中提取有价值的经验：

过程数据：{process_data}

请提取：
1. 成功经验
2. 失败教训
3. 最佳实践
4. 可复用方案"""

        experience = self.think(prompt)

        return {
            "success": True,
            "output": {
                "experience": experience,
                "success_points": [],
                "lessons_learned": []
            }
        }

    def generate_summary(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成总结"""
        input_data = task.get('input', {})
        period = input_data.get('period', '')
        events = input_data.get('events', [])

        prompt = f"""作为实时记录员，请生成以下时间段的过程总结：

时间段：{period}
事件列表：{json.dumps(events, ensure_ascii=False)}

请生成：
1. 过程概述
2. 关键事件
3. 经验总结
4. 改进建议"""

        summary = self.think(prompt)

        return {
            "success": True,
            "output": {
                "summary": summary
            }
        }

    def update_status(self, status: str, task: Optional[Dict] = None):
        """更新状态"""
        self.status = status
        if task:
            self.current_task = task
