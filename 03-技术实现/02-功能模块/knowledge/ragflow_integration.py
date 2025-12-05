#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow知识库集成模块
用于数字人系统检索和沉淀知识
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json

# 添加RAGFlow客户端路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ragflow_path = os.path.join(project_root, '04-知识库建设/06-RAGFlow配置')
sys.path.insert(0, ragflow_path)

try:
    from ragflow_client import RAGFlowClient
except ImportError as e:
    RAGFlowClient = None
    logging.warning(f"RAGFlow客户端未找到: {e}，知识库功能将受限")

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """知识库管理器"""
    
    def __init__(self, ragflow_client: Optional[RAGFlowClient] = None):
        """
        初始化知识库管理器
        
        Args:
            ragflow_client: RAGFlow客户端实例
        """
        if RAGFlowClient is None:
            logger.warning("RAGFlow客户端不可用，知识库功能受限")
            self.client = None
            self.kb_id = None
        else:
            try:
                self.client = ragflow_client or RAGFlowClient()
                self.kb_id = self.client.knowledge_base_id
            except (ValueError, Exception) as e:
                logger.warning(f"RAGFlow客户端初始化失败: {e}，知识库功能受限")
                self.client = None
                self.kb_id = None
    
    def search(self, query: str, top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        搜索知识库
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            filters: 过滤条件
        
        Returns:
            搜索结果列表
        """
        if not self.client or not self.kb_id:
            logger.warning("知识库未配置，返回空结果")
            return []
        
        try:
            results = self.client.search(
                kb_id=self.kb_id,
                query=query,
                top_k=top_k,
                filters=filters
            )
            logger.info(f"知识库搜索: '{query}' -> {len(results)} 条结果")
            return results
        except Exception as e:
            logger.error(f"知识库搜索失败: {e}")
            return []
    
    def add_knowledge(self,
                     content: str,
                     title: str = "",
                     category: str = "general",
                     metadata: Optional[Dict] = None) -> Optional[str]:
        """
        添加知识到知识库
        
        Args:
            content: 知识内容
            title: 标题
            category: 分类
            metadata: 元数据
        
        Returns:
            文档ID（如果成功）
        """
        if not self.client or not self.kb_id:
            logger.warning("知识库未配置，无法添加知识")
            return None
        
        try:
            # 构建完整内容
            full_content = f"{title}\n\n{content}" if title else content
            
            # 构建元数据
            doc_metadata = {
                "category": category,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **(metadata or {})
            }
            
            # 生成文件名
            filename = f"{category}_{datetime.now().strftime('%Y%m%d_%H%S')}.txt"
            
            # 上传到RAGFlow
            result = self.client.upload_document(
                kb_id=self.kb_id,
                content=full_content,
                filename=filename,
                metadata=doc_metadata
            )
            
            doc_id = result.get('id') or result.get('doc_id', '')
            logger.info(f"知识已添加到知识库: {title or '未命名'} (ID: {doc_id[:8]}...)")
            return doc_id
        except Exception as e:
            logger.error(f"添加知识失败: {e}")
            return None
    
    def add_task_result(self,
                       task_id: str,
                       task_type: str,
                       result: Dict[str, Any],
                       role_name: str,
                       metadata: Optional[Dict] = None) -> Optional[str]:
        """
        将任务执行结果添加到知识库
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            result: 任务结果
            role_name: 执行角色
            metadata: 额外元数据
        
        Returns:
            文档ID
        """
        # 构建知识内容
        content = f"""
任务ID: {task_id}
任务类型: {task_type}
执行角色: {role_name}
执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

执行结果:
{json.dumps(result, ensure_ascii=False, indent=2)}
"""
        
        # 构建元数据
        doc_metadata = {
            "task_id": task_id,
            "task_type": task_type,
            "role_name": role_name,
            "type": "task_result",
            **(metadata or {})
        }
        
        title = f"任务执行结果 - {task_type} ({role_name})"
        
        return self.add_knowledge(
            content=content,
            title=title,
            category="task_results",
            metadata=doc_metadata
        )
    
    def add_experience(self,
                      experience_type: str,
                      content: str,
                      context: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> Optional[str]:
        """
        添加经验到知识库
        
        Args:
            experience_type: 经验类型（success, failure, best_practice等）
            content: 经验内容
            context: 上下文信息
            metadata: 元数据
        
        Returns:
            文档ID
        """
        full_content = f"""
经验类型: {experience_type}
{context or ''}

经验内容:
{content}
"""
        
        doc_metadata = {
            "experience_type": experience_type,
            "type": "experience",
            **(metadata or {})
        }
        
        return self.add_knowledge(
            content=full_content,
            title=f"经验总结 - {experience_type}",
            category="experiences",
            metadata=doc_metadata
        )


import json

