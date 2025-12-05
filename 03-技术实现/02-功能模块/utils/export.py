#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出功能模块
支持导出任务、工作流、统计报告等
"""

import json
import csv
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Exporter:
    """导出器"""
    
    @staticmethod
    def export_tasks_to_json(tasks: List[Dict], file_path: str) -> bool:
        """
        导出任务到JSON文件
        
        Args:
            tasks: 任务列表
            file_path: 文件路径
        
        Returns:
            是否成功
        """
        try:
            data = {
                "export_time": datetime.now().isoformat(),
                "total": len(tasks),
                "tasks": tasks
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"任务已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出任务失败: {e}")
            return False
    
    @staticmethod
    def export_tasks_to_csv(tasks: List[Dict], file_path: str) -> bool:
        """
        导出任务到CSV文件
        
        Args:
            tasks: 任务列表
            file_path: 文件路径
        
        Returns:
            是否成功
        """
        try:
            if not tasks:
                return False
            
            # 获取所有字段
            fieldnames = set()
            for task in tasks:
                fieldnames.update(task.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for task in tasks:
                    # 将复杂对象转换为字符串
                    row = {}
                    for key, value in task.items():
                        if isinstance(value, (dict, list)):
                            row[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            row[key] = value
                    writer.writerow(row)
            
            logger.info(f"任务已导出到CSV: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出CSV失败: {e}")
            return False
    
    @staticmethod
    def export_workflows_to_json(workflows: List[Dict], file_path: str) -> bool:
        """
        导出工作流到JSON文件
        
        Args:
            workflows: 工作流列表
            file_path: 文件路径
        
        Returns:
            是否成功
        """
        try:
            data = {
                "export_time": datetime.now().isoformat(),
                "total": len(workflows),
                "workflows": workflows
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"工作流已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出工作流失败: {e}")
            return False
    
    @staticmethod
    def export_report_to_markdown(report: Dict, file_path: str) -> bool:
        """
        导出报告到Markdown文件
        
        Args:
            report: 报告数据
            file_path: 文件路径
        
        Returns:
            是否成功
        """
        try:
            content = f"""# 性能报告

**生成时间**: {report.get('period', {}).get('start', 'N/A')} 至 {report.get('period', {}).get('end', 'N/A')}

## 摘要

- **总任务数**: {report.get('summary', {}).get('total_tasks', 0)}
- **已完成**: {report.get('summary', {}).get('completed_tasks', 0)}
- **失败**: {report.get('summary', {}).get('failed_tasks', 0)}
- **成功率**: {report.get('summary', {}).get('success_rate', 0)}%
- **平均执行时长**: {report.get('summary', {}).get('avg_duration_seconds', 0):.2f}秒

## 按角色统计

"""
            
            by_role = report.get('by_role', {})
            for role, stats in by_role.items():
                content += f"### {role}\n\n"
                content += f"- 总任务: {stats.get('total', 0)}\n"
                content += f"- 已完成: {stats.get('completed', 0)}\n"
                content += f"- 失败: {stats.get('failed', 0)}\n"
                if stats.get('avg_duration', 0) > 0:
                    content += f"- 平均时长: {stats.get('avg_duration', 0):.2f}秒\n"
                content += "\n"
            
            content += "## 按任务类型统计\n\n"
            by_type = report.get('by_task_type', {})
            for task_type, stats in by_type.items():
                content += f"### {task_type}\n\n"
                content += f"- 总任务: {stats.get('total', 0)}\n"
                content += f"- 已完成: {stats.get('completed', 0)}\n"
                content += f"- 失败: {stats.get('failed', 0)}\n"
                if stats.get('avg_duration', 0) > 0:
                    content += f"- 平均时长: {stats.get('avg_duration', 0):.2f}秒\n"
                content += "\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"报告已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出报告失败: {e}")
            return False

