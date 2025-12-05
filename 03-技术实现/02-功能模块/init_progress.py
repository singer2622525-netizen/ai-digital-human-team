#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化进度跟踪系统 - 设置初始里程碑和任务
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from progress_tracker import ProgressTracker

def init_project_progress():
    """初始化项目进度"""
    script_dir = Path(__file__).parent
    data_file = script_dir / "progress_data.json"

    # 如果数据文件已存在，询问是否覆盖
    if data_file.exists():
        response = input("⚠️  数据文件已存在，是否重新初始化？(y/N): ").strip().lower()
        if response != 'y':
            print("已取消初始化")
            return

    tracker = ProgressTracker(str(data_file))

    print("🚀 正在初始化软件工程事业部建设进度跟踪系统...")
    print()

    # 添加里程碑
    print("📅 添加里程碑...")

    # M0: 组织蓝图确认（第1个月末）
    today = datetime.now()
    m0_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    tracker.add_milestone(
        "M0: 组织蓝图确认",
        m0_date,
        "完成组织架构设计、角色定义、流程框架"
    )

    # M1: 流程体系上线（第2个月末）
    m1_date = (today + timedelta(days=60)).strftime("%Y-%m-%d")
    tracker.add_milestone(
        "M1: 流程体系上线",
        m1_date,
        "完成流程标准化、工具链搭建、知识库框架"
    )

    # M2: 数字人试点启动（第3个月末）
    m2_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")
    tracker.add_milestone(
        "M2: 数字人试点启动",
        m2_date,
        "完成首个数字人场景开发并上线"
    )

    # M3: 数字人服务迭代与扩展（第4-6个月）
    m3_date = (today + timedelta(days=180)).strftime("%Y-%m-%d")
    tracker.add_milestone(
        "M3: 数字人服务迭代与扩展",
        m3_date,
        "完成多个数字人场景，建立持续迭代机制"
    )

    print("✅ 里程碑添加完成")
    print()

    # 添加第一阶段任务（M0相关）
    print("📋 添加第一阶段任务...")

    # 组织结构设计相关任务
    tracker.add_task(
        "完成组织架构设计（事业部总监、PMO、各中心）",
        milestone_id="m1",
        priority="high",
        description="定义各中心的职责和协作关系"
    )

    tracker.add_task(
        "完成岗位职责说明书",
        milestone_id="m1",
        priority="high",
        description="为每个岗位编写详细的职责说明"
    )

    tracker.add_task(
        "设计审批链和决策机制",
        milestone_id="m1",
        priority="medium",
        description="明确关键节点的审批流程"
    )

    # 流程与制度相关任务
    tracker.add_task(
        "梳理项目全流程（立项→交付→运维）",
        milestone_id="m2",
        priority="high",
        description="绘制流程图，定义各阶段交付物"
    )

    tracker.add_task(
        "建立标准文档模板库",
        milestone_id="m2",
        priority="high",
        description="需求文档、设计文档、测试报告等模板"
    )

    tracker.add_task(
        "设计质量评审机制",
        milestone_id="m2",
        priority="medium",
        description="定义评审标准和流程"
    )

    # 工具与知识库相关任务
    tracker.add_task(
        "搭建进度跟踪工具（本工具）",
        milestone_id="m1",
        priority="high",
        description="完成进度跟踪系统的开发和部署"
    )

    tracker.add_task(
        "搭建知识库框架（RAGFlow，远程API）",
        milestone_id="m2",
        priority="high",
        description="配置知识库，建立分类体系"
    )

    tracker.add_task(
        "搭建可视化看板",
        milestone_id="m2",
        priority="medium",
        description="选择并配置项目管理看板工具"
    )

    # 数字人场景孵化相关任务
    tracker.add_task(
        "收集各部门数字人需求",
        milestone_id="m3",
        priority="high",
        description="与各部门主管沟通，收集需求"
    )

    tracker.add_task(
        "设计首个数字人场景方案",
        milestone_id="m3",
        priority="high",
        description="选择优先级最高的场景，完成方案设计"
    )

    tracker.add_task(
        "开发数字人原型",
        milestone_id="m3",
        priority="high",
        description="实现首个数字人的核心功能"
    )

    print("✅ 任务添加完成")
    print()

    # 添加初始笔记
    tracker.add_note(
        "项目启动：开始建设软件工程事业部，目标是构建一个能够自主运转并孵化数字人产品的组织",
        category="project"
    )

    print("🎉 初始化完成！")
    print()
    print("💡 提示:")
    print("   1. 运行 'python progress_tracker.py' 查看进度仪表盘")
    print("   2. 运行 'python progress_tracker.py help' 查看所有命令")
    print("   3. 数据文件保存在: progress_data.json")
    print()


if __name__ == "__main__":
    init_project_progress()
