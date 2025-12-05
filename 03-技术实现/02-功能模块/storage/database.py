#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据持久化模块 - SQLite数据库
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = "digital_humans.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # 任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                input_data TEXT NOT NULL,
                assigned_to TEXT,
                priority INTEGER NOT NULL,
                dependencies TEXT,
                metadata TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                assigned_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                result TEXT,
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                timeout_seconds INTEGER
            )
        """)
        
        # 工作流表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                template_name TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT
            )
        """)
        
        # 工作流步骤表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                step_type TEXT NOT NULL,
                step_order INTEGER NOT NULL,
                dependencies TEXT,
                status TEXT NOT NULL,
                task_id TEXT,
                result TEXT,
                error TEXT,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)
        
        # 知识库记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_records (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                title TEXT,
                category TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                source_type TEXT,
                source_id TEXT
            )
        """)
        
        self.conn.commit()
        logger.info(f"数据库初始化完成: {self.db_path}")
    
    def save_task(self, task: Any) -> bool:
        """
        保存任务到数据库
        
        Args:
            task: 任务对象
        
        Returns:
            是否成功
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO tasks (
                    id, task_type, input_data, assigned_to, priority,
                    dependencies, metadata, status, created_at,
                    assigned_at, started_at, completed_at, result,
                    error, retry_count, max_retries, timeout_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.task_type,
                json.dumps(task.input_data, ensure_ascii=False),
                task.assigned_to,
                task.priority.value,
                json.dumps(task.dependencies, ensure_ascii=False),
                json.dumps(task.metadata, ensure_ascii=False),
                task.status.value,
                task.created_at.isoformat(),
                task.assigned_at.isoformat() if task.assigned_at else None,
                task.started_at.isoformat() if task.started_at else None,
                task.completed_at.isoformat() if task.completed_at else None,
                json.dumps(task.result, ensure_ascii=False) if task.result else None,
                task.error,
                task.retry_count,
                task.max_retries,
                task.timeout_seconds
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"保存任务失败: {e}")
            return False
    
    def load_tasks(self) -> List[Dict]:
        """
        从数据库加载所有任务
        
        Returns:
            任务列表
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            tasks = []
            for row in rows:
                task = dict(row)
                # 解析JSON字段
                task['input_data'] = json.loads(task['input_data'])
                task['dependencies'] = json.loads(task['dependencies']) if task['dependencies'] else []
                task['metadata'] = json.loads(task['metadata']) if task['metadata'] else {}
                if task['result']:
                    task['result'] = json.loads(task['result'])
                tasks.append(task)
            
            return tasks
        except Exception as e:
            logger.error(f"加载任务失败: {e}")
            return []
    
    def save_workflow(self, workflow: Any) -> bool:
        """
        保存工作流到数据库
        
        Args:
            workflow: 工作流对象
        
        Returns:
            是否成功
        """
        try:
            cursor = self.conn.cursor()
            
            # 保存工作流
            cursor.execute("""
                INSERT OR REPLACE INTO workflows (
                    id, name, description, status, template_name,
                    metadata, created_at, started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow.id,
                workflow.name,
                workflow.description,
                workflow.status.value,
                workflow.template_name,
                json.dumps(workflow.metadata, ensure_ascii=False),
                workflow.created_at.isoformat(),
                workflow.started_at.isoformat() if workflow.started_at else None,
                workflow.completed_at.isoformat() if workflow.completed_at else None
            ))
            
            # 保存工作流步骤
            cursor.execute("DELETE FROM workflow_steps WHERE workflow_id = ?", (workflow.id,))
            
            for i, step in enumerate(workflow.steps):
                cursor.execute("""
                    INSERT INTO workflow_steps (
                        id, workflow_id, step_type, step_order,
                        dependencies, status, task_id, result, error
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    step.step_id,
                    workflow.id,
                    step.step_type,
                    i,
                    json.dumps(step.dependencies, ensure_ascii=False),
                    step.status.value,
                    step.task_id,
                    json.dumps(step.result, ensure_ascii=False) if step.result else None,
                    step.error
                ))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"保存工作流失败: {e}")
            return False
    
    def load_workflows(self) -> List[Dict]:
        """
        从数据库加载所有工作流
        
        Returns:
            工作流列表
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM workflows ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            workflows = []
            for row in rows:
                workflow = dict(row)
                workflow['metadata'] = json.loads(workflow['metadata']) if workflow['metadata'] else {}
                
                # 加载步骤
                cursor.execute("SELECT * FROM workflow_steps WHERE workflow_id = ? ORDER BY step_order", (workflow['id'],))
                steps = cursor.fetchall()
                workflow['steps'] = [dict(step) for step in steps]
                
                workflows.append(workflow)
            
            return workflows
        except Exception as e:
            logger.error(f"加载工作流失败: {e}")
            return []
    
    def save_knowledge(self, knowledge_id: str, content: str, title: str = "",
                      category: str = "general", metadata: Optional[Dict] = None,
                      source_type: Optional[str] = None, source_id: Optional[str] = None) -> bool:
        """
        保存知识到数据库
        
        Args:
            knowledge_id: 知识ID
            content: 内容
            title: 标题
            category: 分类
            metadata: 元数据
            source_type: 来源类型
            source_id: 来源ID
        
        Returns:
            是否成功
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO knowledge_records (
                    id, content, title, category, metadata,
                    created_at, source_type, source_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                knowledge_id,
                content,
                title,
                category,
                json.dumps(metadata or {}, ensure_ascii=False),
                datetime.now().isoformat(),
                source_type,
                source_id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"保存知识失败: {e}")
            return False
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索知识（简单文本匹配）
        
        Args:
            query: 搜索查询
            limit: 返回数量限制
        
        Returns:
            知识列表
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM knowledge_records
                WHERE content LIKE ? OR title LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"搜索知识失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

