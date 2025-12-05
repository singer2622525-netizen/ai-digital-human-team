#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识管理员数字人
负责知识库技术维护、知识内容整理、分类和质量评估
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_humans.base import BaseDigitalHuman
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class KnowledgeAdministrator(BaseDigitalHuman):
    """知识管理员数字人"""

    def __init__(self, name: str = "知识管理员-001", **kwargs):
        super().__init__(
            name=name,
            role="知识管理员",
            department="PMO",
            **kwargs
        )

    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是知识管理员，负责知识库的技术维护、知识内容整理、分类和质量评估。

你的核心职责：
1. 知识库技术维护：维护RAGFlow知识库的技术配置和API访问
2. 知识内容整理：整理和分类知识内容，建立知识分类体系
3. 知识质量评估：评估知识质量，去重和更新知识内容
4. 文档管理：管理文档库，建立文档索引

你的工作原则：
- 确保知识库的可用性和性能
- 保证知识内容的准确性和完整性
- 建立科学的分类体系
- 持续优化知识检索效果"""

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('type', 'unknown')
        self.update_status('working', task)

        try:
            if task_type == 'maintain_knowledge_base':
                return self.maintain_knowledge_base(task)
            elif task_type == 'organize_knowledge':
                return self.organize_knowledge(task)
            elif task_type == 'assess_quality':
                return self.assess_quality(task)
            elif task_type == 'manage_documents':
                return self.manage_documents(task)
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

    def maintain_knowledge_base(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """维护知识库"""
        input_data = task.get('input', {})
        action = input_data.get('action', 'check')  # check, create, update, delete

        prompt = f"""作为知识管理员，请执行以下知识库维护操作：

操作类型：{action}

请提供：
1. 操作结果
2. 知识库状态
3. 发现的问题
4. 改进建议"""

        result = self.think(prompt)

        return {
            "success": True,
            "output": {
                "action": action,
                "result": result,
                "status": {},
                "issues": [],
                "suggestions": []
            }
        }

    def organize_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """整理知识"""
        input_data = task.get('input', {})
        knowledge_content = input_data.get('knowledge_content', '')

        prompt = f"""作为知识管理员，请整理以下知识内容：

知识内容：{knowledge_content}

请提供：
1. 知识分类建议
2. 标签建议
3. 关联知识识别
4. 整理后的知识结构"""

        organization = self.think(prompt)

        return {
            "success": True,
            "output": {
                "category": "",
                "tags": [],
                "related_knowledge": [],
                "organized_content": organization
            }
        }

    def assess_quality(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """评估知识质量"""
        input_data = task.get('input', {})
        knowledge_content = input_data.get('knowledge_content', '')

        prompt = f"""作为知识管理员，请评估以下知识内容的质量：

知识内容：{knowledge_content}

请评估：
1. 知识准确性
2. 知识完整性
3. 知识可复用性
4. 知识价值
5. 改进建议"""

        assessment = self.think(prompt)

        return {
            "success": True,
            "output": {
                "quality_score": 0,
                "assessment": assessment,
                "accuracy": 0,
                "completeness": 0,
                "reusability": 0,
                "value": 0,
                "suggestions": []
            }
        }

    def manage_documents(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """管理文档"""
        input_data = task.get('input', {})
        document = input_data.get('document', '')
        action = input_data.get('action', 'index')  # index, update, delete

        prompt = f"""作为知识管理员，请执行以下文档管理操作：

操作类型：{action}
文档内容：{document[:200]}...

请提供：
1. 文档索引信息
2. 文档分类
3. 文档标签
4. 文档关联"""

        result = self.think(prompt)

        return {
            "success": True,
            "output": {
                "action": action,
                "index_info": result,
                "category": "",
                "tags": [],
                "related_docs": []
            }
        }

    def update_status(self, status: str, task: Optional[Dict] = None):
        """更新状态"""
        self.status = status
        if task:
            self.current_task = task
