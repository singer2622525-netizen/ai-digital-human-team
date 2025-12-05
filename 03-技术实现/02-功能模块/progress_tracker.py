#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件工程事业部建设进度跟踪工具
自动记录项目进度，启动时显示当前状态和待办事项
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, data_file: str = "progress_data.json"):
        self.data_file = Path(data_file)
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """加载数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  读取数据文件失败: {e}")
                return self._init_data()
        return self._init_data()

    def _init_data(self) -> Dict:
        """初始化数据结构"""
        return {
            "project_name": "软件工程事业部建设",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "milestones": [],
            "tasks": [],
            "notes": []
        }

    def _save_data(self):
        """保存数据"""
        self.data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False

    def add_milestone(self, name: str, target_date: str, description: str = ""):
        """添加里程碑"""
        milestone = {
            "id": f"m{len(self.data['milestones']) + 1}",
            "name": name,
            "target_date": target_date,
            "description": description,
            "status": "pending",
            "completed_date": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["milestones"].append(milestone)
        self._save_data()
        return milestone

    def add_task(self, title: str, milestone_id: Optional[str] = None,
                 priority: str = "medium", description: str = ""):
        """添加任务"""
        task = {
            "id": f"t{len(self.data['tasks']) + 1}",
            "title": title,
            "milestone_id": milestone_id,
            "priority": priority,  # high, medium, low
            "description": description,
            "status": "pending",  # pending, in_progress, completed, blocked
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None
        }
        self.data["tasks"].append(task)
        self._save_data()
        return task

    def update_task_status(self, task_id: str, status: str):
        """更新任务状态"""
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task["status"] = status
                task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if status == "completed":
                    task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return True
        return False

    def complete_milestone(self, milestone_id: str):
        """完成里程碑"""
        for milestone in self.data["milestones"]:
            if milestone["id"] == milestone_id:
                milestone["status"] = "completed"
                milestone["completed_date"] = datetime.now().strftime("%Y-%m-%d")
                self._save_data()
                return True
        return False

    def add_note(self, content: str, category: str = "general"):
        """添加笔记"""
        note = {
            "id": f"n{len(self.data['notes']) + 1}",
            "content": content,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["notes"].append(note)
        self._save_data()
        return note

    def get_progress_summary(self) -> Dict:
        """获取进度摘要"""
        total_tasks = len(self.data["tasks"])
        completed_tasks = sum(1 for t in self.data["tasks"] if t["status"] == "completed")
        in_progress_tasks = sum(1 for t in self.data["tasks"] if t["status"] == "in_progress")
        pending_tasks = sum(1 for t in self.data["tasks"] if t["status"] == "pending")

        total_milestones = len(self.data["milestones"])
        completed_milestones = sum(1 for m in self.data["milestones"] if m["status"] == "completed")

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "task_completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "milestone_completion_rate": (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        }

    def get_urgent_tasks(self) -> List[Dict]:
        """获取紧急任务"""
        urgent = []
        for task in self.data["tasks"]:
            if task["status"] in ["pending", "in_progress"] and task["priority"] == "high":
                urgent.append(task)
        return sorted(urgent, key=lambda x: x["created_at"])

    def get_today_tasks(self) -> List[Dict]:
        """获取今日待办（进行中的任务）"""
        today = []
        for task in self.data["tasks"]:
            if task["status"] == "in_progress":
                today.append(task)
        return today

    def display_dashboard(self):
        """显示仪表盘"""
        summary = self.get_progress_summary()
        urgent_tasks = self.get_urgent_tasks()
        today_tasks = self.get_today_tasks()

        print("\n" + "="*60)
        print(f"📊 {self.data['project_name']} - 进度仪表盘")
        print("="*60)
        print(f"📅 项目开始日期: {self.data['start_date']}")
        print(f"🕐 最后更新: {self.data['last_update']}")
        print()

        # 里程碑进度
        print("🎯 里程碑进度:")
        if summary["total_milestones"] > 0:
            print(f"   完成: {summary['completed_milestones']}/{summary['total_milestones']} "
                  f"({summary['milestone_completion_rate']:.1f}%)")
            for milestone in self.data["milestones"]:
                status_icon = "✅" if milestone["status"] == "completed" else "⏳"
                print(f"   {status_icon} {milestone['name']} (目标: {milestone['target_date']})")
        else:
            print("   ⚠️  暂无里程碑，建议先添加里程碑")
        print()

        # 任务进度
        print("📋 任务进度:")
        print(f"   总计: {summary['total_tasks']} | "
              f"✅ 完成: {summary['completed_tasks']} | "
              f"🔄 进行中: {summary['in_progress_tasks']} | "
              f"⏸️  待办: {summary['pending_tasks']}")
        print(f"   完成率: {summary['task_completion_rate']:.1f}%")
        print()

        # 进度条
        progress_bar_length = 40
        filled = int(summary['task_completion_rate'] / 100 * progress_bar_length)
        bar = "█" * filled + "░" * (progress_bar_length - filled)
        print(f"   [{bar}] {summary['task_completion_rate']:.1f}%")
        print()

        # 紧急任务
        if urgent_tasks:
            print("🚨 紧急任务:")
            for task in urgent_tasks[:5]:  # 最多显示5个
                status_icon = "🔄" if task["status"] == "in_progress" else "⏸️"
                print(f"   {status_icon} [{task['id']}] {task['title']}")
            print()

        # 今日待办
        if today_tasks:
            print("📌 今日进行中:")
            for task in today_tasks[:5]:  # 最多显示5个
                print(f"   🔄 [{task['id']}] {task['title']}")
            print()

        # 待办任务
        pending = [t for t in self.data["tasks"] if t["status"] == "pending"]
        if pending:
            print("📝 待办任务:")
            for task in pending[:5]:  # 最多显示5个
                print(f"   ⏸️  [{task['id']}] {task['title']}")
            print()

        print("="*60)
        print("💡 提示: 使用 'python progress_tracker.py help' 查看所有命令")
        print("="*60 + "\n")


def main():
    """主函数"""
    # 确定数据文件路径（放在脚本同目录）
    script_dir = Path(__file__).parent
    data_file = script_dir / "progress_data.json"

    tracker = ProgressTracker(str(data_file))

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "help":
            print("""
可用命令:
  python progress_tracker.py                    # 显示仪表盘
  python progress_tracker.py add-milestone       # 添加里程碑
  python progress_tracker.py add-task            # 添加任务
  python progress_tracker.py update-task         # 更新任务状态
  python progress_tracker.py complete-milestone  # 完成里程碑
  python progress_tracker.py add-note            # 添加笔记
  python progress_tracker.py list-tasks          # 列出所有任务
  python progress_tracker.py list-milestones     # 列出所有里程碑
  python progress_tracker.py help               # 显示帮助
            """)

        elif command == "add-milestone":
            print("添加里程碑:")
            name = input("里程碑名称: ").strip()
            target_date = input("目标日期 (YYYY-MM-DD): ").strip()
            description = input("描述 (可选): ").strip()
            milestone = tracker.add_milestone(name, target_date, description)
            print(f"✅ 已添加里程碑: {milestone['id']} - {milestone['name']}")

        elif command == "add-task":
            print("添加任务:")
            title = input("任务标题: ").strip()
            milestone_id = input("关联里程碑ID (可选，直接回车跳过): ").strip() or None
            priority = input("优先级 (high/medium/low，默认medium): ").strip() or "medium"
            description = input("描述 (可选): ").strip()
            task = tracker.add_task(title, milestone_id, priority, description)
            print(f"✅ 已添加任务: {task['id']} - {task['title']}")

        elif command == "update-task":
            print("更新任务状态:")
            task_id = input("任务ID: ").strip()
            print("状态选项: pending, in_progress, completed, blocked")
            status = input("新状态: ").strip()
            if tracker.update_task_status(task_id, status):
                print(f"✅ 任务 {task_id} 状态已更新为: {status}")
            else:
                print(f"❌ 未找到任务: {task_id}")

        elif command == "complete-milestone":
            print("完成里程碑:")
            milestone_id = input("里程碑ID: ").strip()
            if tracker.complete_milestone(milestone_id):
                print(f"✅ 里程碑 {milestone_id} 已完成")
            else:
                print(f"❌ 未找到里程碑: {milestone_id}")

        elif command == "add-note":
            print("添加笔记:")
            content = input("笔记内容: ").strip()
            category = input("分类 (可选，默认general): ").strip() or "general"
            note = tracker.add_note(content, category)
            print(f"✅ 已添加笔记: {note['id']}")

        elif command == "list-tasks":
            print("\n所有任务:")
            print("-" * 60)
            for task in tracker.data["tasks"]:
                status_icon = {
                    "pending": "⏸️",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "blocked": "🚫"
                }.get(task["status"], "❓")
                priority_icon = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(task["priority"], "⚪")
                print(f"{status_icon} {priority_icon} [{task['id']}] {task['title']}")
                print(f"   状态: {task['status']} | 创建: {task['created_at']}")
                if task['milestone_id']:
                    print(f"   里程碑: {task['milestone_id']}")
                print()

        elif command == "list-milestones":
            print("\n所有里程碑:")
            print("-" * 60)
            for milestone in tracker.data["milestones"]:
                status_icon = "✅" if milestone["status"] == "completed" else "⏳"
                print(f"{status_icon} [{milestone['id']}] {milestone['name']}")
                print(f"   目标日期: {milestone['target_date']}")
                if milestone['status'] == "completed" and milestone['completed_date']:
                    print(f"   完成日期: {milestone['completed_date']}")
                print()

        else:
            print(f"❌ 未知命令: {command}")
            print("使用 'python progress_tracker.py help' 查看帮助")
    else:
        # 默认显示仪表盘
        tracker.display_dashboard()


if __name__ == "__main__":
    main()


