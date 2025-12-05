#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目经理数字人
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any, List
import json
from datetime import datetime


class ProjectManager(BaseDigitalHuman):
    """项目经理数字人"""
    
    def __init__(self, name: str = "项目经理-001", **kwargs):
        super().__init__(
            name=name,
            role="项目经理",
            department="PMO",
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一位经验丰富的项目经理，擅长：
1. 制定详细的项目计划和里程碑
2. 跟踪项目进度，识别风险和偏差
3. 协调跨部门资源分配
4. 生成清晰的项目状态报告

你的工作原则：
- 数据驱动决策
- 提前识别风险
- 保持沟通透明
- 持续优化流程"""
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)
        
        try:
            if task_type == 'create_plan':
                return self.create_project_plan(task)
            elif task_type == 'track_progress':
                return self.track_progress(task)
            elif task_type == 'generate_report':
                return self.generate_report(task)
            elif task_type == 'identify_risks':
                return self.identify_risks(task)
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
    
    def create_project_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目计划"""
        requirements = task.get('input', {}).get('requirements', '')
        timeline = task.get('input', {}).get('timeline', '')
        
        # 先搜索相关历史经验
        knowledge_context = ""
        try:
            knowledge_results = self.search_knowledge(f"项目计划 {requirements}", top_k=3)
            if knowledge_results:
                knowledge_context = "\n\n参考历史项目经验:\n"
                for i, result in enumerate(knowledge_results, 1):
                    content = result.get('content', '')[:300]
                    knowledge_context += f"{i}. {content}...\n"
        except:
            pass
        
        prompt = f"""请根据以下需求创建详细的项目计划：

需求描述：
{requirements}

时间要求：
{timeline}
{knowledge_context}

请输出：
1. 项目目标
2. 主要里程碑（至少3个）
3. 任务分解（WBS）
4. 资源需求
5. 风险预估

格式要求：使用Markdown格式，结构清晰。"""
        
        plan = self.think_with_knowledge(prompt, use_knowledge=True)
        
        return {
            "success": True,
            "output": {
                "plan": plan,
                "format": "markdown"
            }
        }
    
    def track_progress(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """跟踪项目进度"""
        project_data = task.get('input', {}).get('project_data', {})
        
        prompt = f"""请分析以下项目进度数据，识别问题和风险：

项目数据：
{json.dumps(project_data, ensure_ascii=False, indent=2)}

请输出：
1. 当前进度百分比
2. 是否按计划进行
3. 识别的风险点
4. 建议的应对措施"""
        
        analysis = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def generate_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成项目报告"""
        report_type = task.get('input', {}).get('type', 'weekly')  # daily, weekly, monthly
        project_data = task.get('input', {}).get('project_data', {})
        
        prompt = f"""请生成一份{report_type}项目报告：

项目数据：
{json.dumps(project_data, ensure_ascii=False, indent=2)}

报告应包含：
1. 项目概况
2. 本周/本月完成情况
3. 下周/下月计划
4. 风险与问题
5. 需要支持的事项"""
        
        report = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "report": report,
                "type": report_type,
                "format": "markdown"
            }
        }
    
    def identify_risks(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """识别项目风险"""
        project_info = task.get('input', {}).get('project_info', {})
        
        prompt = f"""请分析以下项目信息，识别潜在风险：

项目信息：
{json.dumps(project_info, ensure_ascii=False, indent=2)}

请输出：
1. 识别的风险列表（至少3个）
2. 每个风险的影响程度（高/中/低）
3. 发生概率（高/中/低）
4. 应对建议"""
        
        risks = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "risks": risks,
                "format": "markdown"
            }
        }


if __name__ == "__main__":
    import json
    from datetime import datetime
    
    # 测试项目经理
    pm = ProjectManager()
    
    # 测试创建项目计划
    task = {
        "type": "create_plan",
        "input": {
            "requirements": "开发一个内部项目管理系统的网页端，包含项目看板、任务管理、进度跟踪功能",
            "timeline": "3个月"
        }
    }
    
    print("=" * 60)
    print("测试：创建项目计划")
    print("=" * 60)
    result = pm.execute_task(task)
    print(json.dumps(result, ensure_ascii=False, indent=2))

