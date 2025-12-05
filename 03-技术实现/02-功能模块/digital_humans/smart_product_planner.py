#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能产品规划师数字人
项目的核心角色，具备多模态沟通、需求引导、任务拆解等能力
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class SmartProductPlanner(BaseDigitalHuman):
    """智能产品规划师数字人 - 项目的核心角色"""
    
    def __init__(self, name: str = "智能产品规划师-001", **kwargs):
        super().__init__(
            name=name,
            role="智能产品规划师",
            department="解决方案中心",
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是智能产品规划师，是整个数字人团队的核心角色，直接服务于事业部总监。

你的核心能力包括：

1. **多模态沟通能力**
   - 文字对话：自然语言对话，理解用户想法
   - 图片理解：分析流程图、界面截图、手绘草图
   - 文档解析：阅读PDF、Word、Excel、Markdown等文档
   - 音频/语音处理：处理录音音频文件和语音文件
   - 软件使用说明分析：深度分析参考软件的使用说明

2. **需求引导能力**
   - 需求挖掘：通过提问，挖掘未说出的需求
   - 需求澄清：将模糊想法转化为清晰描述
   - 需求验证：验证需求的合理性和可行性
   - 需求优先级：帮助确定需求的优先级

3. **业务分析能力**
   - 需求分析：深入分析业务需求
   - 业务规划：制定业务规划和发展路径
   - 业务方案设计：设计完整的业务方案
   - 详细需求文档：生成详细的需求文档

4. **技术对接能力**
   - 了解最新技术：跟踪技术趋势
   - 技术方案建议：提供技术建议和方案
   - 技术可行性评估：评估技术可行性

5. **任务拆解能力**
   - 需求拆解：将需求拆解成具体任务
   - 任务分配：自动分配给数字人团队
   - 任务跟踪：跟踪任务执行情况

6. **知识理解能力**
   - 深度理解知识内容
   - 理解任务关联性
   - 逐步理解公司发展

7. **数字人监控能力**
   - 监控所有数字人的工作
   - 识别和记录错误
   - 识别和记录闪光点
   - 自动沉淀知识

你的工作原则：
- 以用户为中心，理解用户真实需求
- 将想法转化为可执行的方案
- 全程陪伴，从想法到落地
- 持续学习和优化"""
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)
        
        try:
            if task_type == 'understand_requirement':
                return self.understand_requirement(task)
            elif task_type == 'guide_requirement':
                return self.guide_requirement(task)
            elif task_type == 'analyze_business':
                return self.analyze_business(task)
            elif task_type == 'suggest_technology':
                return self.suggest_technology(task)
            elif task_type == 'breakdown_tasks':
                return self.breakdown_tasks(task)
            elif task_type == 'analyze_reference':
                return self.analyze_reference(task)
            elif task_type == 'process_audio':
                return self.process_audio(task)
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
    
    def understand_requirement(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """理解需求"""
        input_data = task.get('input', {})
        requirement = input_data.get('requirement', '')
        context = input_data.get('context', '')
        
        prompt = f"""作为智能产品规划师，请分析以下需求：

需求描述：{requirement}
上下文：{context}

请提供：
1. 需求的核心要点
2. 需求的业务价值
3. 可能的功能点
4. 需要澄清的问题"""
        
        analysis = self.think(prompt, context)
        
        return {
            "success": True,
            "output": {
                "analysis": analysis,
                "key_points": [],
                "questions": []
            }
        }
    
    def guide_requirement(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """引导需求"""
        input_data = task.get('input', {})
        requirement = input_data.get('requirement', '')
        
        prompt = f"""作为智能产品规划师，请引导和优化以下需求：

原始需求：{requirement}

请提供：
1. 需求优化建议
2. 需要补充的信息
3. 优化后的需求描述"""
        
        guidance = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "optimized_requirement": guidance,
                "suggestions": [],
                "missing_info": []
            }
        }
    
    def analyze_business(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """业务分析"""
        input_data = task.get('input', {})
        requirement = input_data.get('requirement', '')
        
        prompt = f"""作为智能产品规划师，请进行深入的业务分析：

需求：{requirement}

请提供：
1. 业务需求分析
2. 功能点识别
3. 业务规则定义
4. 业务流程设计
5. 详细需求文档"""
        
        analysis = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "business_analysis": analysis,
                "functional_points": [],
                "business_rules": [],
                "business_processes": []
            }
        }
    
    def suggest_technology(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """技术方案建议"""
        input_data = task.get('input', {})
        requirement = input_data.get('requirement', '')
        
        prompt = f"""作为智能产品规划师，请提供技术方案建议：

需求：{requirement}

请提供：
1. 技术选型建议
2. 技术架构建议
3. 技术实现路径
4. 技术风险评估"""
        
        suggestion = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "technology_suggestion": suggestion,
                "tech_stack": [],
                "architecture": ""
            }
        }
    
    def breakdown_tasks(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """任务拆解"""
        input_data = task.get('input', {})
        requirement = input_data.get('requirement', '')
        
        prompt = f"""作为智能产品规划师，请将以下需求拆解成具体任务：

需求：{requirement}

请提供：
1. 任务列表
2. 任务优先级
3. 任务依赖关系
4. 任务分配建议"""
        
        breakdown = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "tasks": [],
                "priorities": {},
                "dependencies": {},
                "assignments": {}
            }
        }
    
    def analyze_reference(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """分析参考软件"""
        input_data = task.get('input', {})
        reference_doc = input_data.get('reference_doc', '')
        
        prompt = f"""作为智能产品规划师，请分析以下参考软件的使用说明：

参考文档：{reference_doc}

请提供：
1. 软件功能分析
2. 设计思路理解
3. 可借鉴的功能点
4. 实现建议"""
        
        analysis = self.think(prompt)
        
        return {
            "success": True,
            "output": {
                "function_analysis": analysis,
                "design_ideas": [],
                "reference_features": []
            }
        }
    
    def process_audio(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理音频/语音"""
        input_data = task.get('input', {})
        audio_file = input_data.get('audio_file', '')
        
        # 这里应该集成语音识别功能（如Whisper）
        # 目前返回占位符
        
        return {
            "success": True,
            "output": {
                "transcription": "音频转文字功能待实现",
                "understanding": "语音理解功能待实现"
            },
            "note": "需要集成Whisper或其他语音识别服务"
        }
    
    def update_status(self, status: str, task: Optional[Dict] = None):
        """更新状态"""
        self.status = status
        if task:
            self.current_task = task
            if status == 'working':
                self.work_history.append({
                    "task": task,
                    "started_at": datetime.now().isoformat(),
                    "status": status
                })
        if status == 'idle':
            self.current_task = None
        elif status == 'error':
            if self.current_task:
                self.work_history[-1]["status"] = "error"
                self.work_history[-1]["error"] = str(task.get('error', 'Unknown error'))

