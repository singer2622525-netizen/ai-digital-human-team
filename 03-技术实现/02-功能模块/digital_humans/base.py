#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字人基础框架
所有数字人角色的基类
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import sys

# 添加知识库模块路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'knowledge'))


class OllamaClient:
    """Ollama API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder:6.7b"):
        """
        初始化Ollama客户端
        
        Args:
            base_url: Ollama服务地址
            model: 使用的模型名称（默认: deepseek-coder:6.7b）
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示（角色定义）
            **kwargs: 其他参数（temperature, max_tokens等）
        
        Returns:
            生成的文本
        """
        url = f"{self.base_url}/api/generate"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        # Ollama的generate API不支持system参数，需要将system_prompt合并到prompt中
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        data["prompt"] = full_prompt
        
        try:
            response = requests.post(url, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            print(f"❌ Ollama API调用失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   响应内容: {e.response.text[:200]}")
            return f"[错误] 无法调用AI模型: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        对话模式
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            **kwargs: 其他参数
        
        Returns:
            回复内容
        """
        url = f"{self.base_url}/api/chat"
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('message', {}).get('content', '')
        except Exception as e:
            print(f"❌ Ollama API调用失败: {e}")
            return f"[错误] 无法调用AI模型: {str(e)}"


class BaseDigitalHuman(ABC):
    """数字人基类"""
    
    def __init__(self, 
                 name: str,
                 role: str,
                 department: str,
                 ollama_client: Optional[OllamaClient] = None,
                 knowledge_base_id: Optional[str] = None):
        """
        初始化数字人
        
        Args:
            name: 数字人名称
            role: 角色名称
            department: 所属部门
            ollama_client: Ollama客户端实例
            knowledge_base_id: 知识库ID（用于RAGFlow）
        """
        self.name = name
        self.role = role
        self.department = department
        self.ollama = ollama_client or OllamaClient()
        self.knowledge_base_id = knowledge_base_id
        
        # 工作状态
        self.status = "idle"  # idle, working, error
        self.current_task = None
        self.work_history = []
        
        # 加载角色定义
        self.role_definition = self._load_role_definition()
    
    def _load_role_definition(self) -> Dict:
        """加载角色定义"""
        role_file = f"02-数字人设计/{self.role}.md"
        if os.path.exists(role_file):
            # 简单读取，实际可以解析Markdown
            with open(role_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content}
        return {"content": f"{self.role}角色定义"}
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示（角色定义）"""
        pass
    
    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task: 任务描述，包含type, input等信息
        
        Returns:
            任务执行结果
        """
        pass
    
    def think(self, prompt: str, context: Optional[str] = None) -> str:
        """
        思考（调用AI）
        
        Args:
            prompt: 提示
            context: 上下文信息
        
        Returns:
            AI回复
        """
        system_prompt = self.get_system_prompt()
        if context:
            full_prompt = f"{context}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        return self.ollama.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
    
    def update_status(self, status: str, task: Optional[Dict] = None):
        """更新工作状态"""
        self.status = status
        self.current_task = task
        if task:
            self.work_history.append({
                "task": task,
                "status": status,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "status": self.status,
            "current_task": self.current_task,
            "work_count": len(self.work_history)
        }
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        搜索知识库（集成RAGFlow）
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
        
        Returns:
            搜索结果
        """
        try:
            from knowledge.ragflow_integration import KnowledgeBase
            kb = KnowledgeBase()
            return kb.search(query, top_k=top_k)
        except Exception as e:
            print(f"⚠️  知识库搜索失败: {e}")
            return []
    
    def think_with_knowledge(self, prompt: str, use_knowledge: bool = True) -> str:
        """
        结合知识库进行思考
        
        Args:
            prompt: 提示
            use_knowledge: 是否使用知识库
        
        Returns:
            AI回复
        """
        context = ""
        
        if use_knowledge:
            # 从知识库检索相关经验
            knowledge_results = self.search_knowledge(prompt, top_k=3)
            if knowledge_results:
                context = "相关历史经验:\n"
                for i, result in enumerate(knowledge_results, 1):
                    content = result.get('content', '')[:200]  # 限制长度
                    context += f"{i}. {content}...\n\n"
        
        return self.think(prompt, context=context if context else None)

