#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流模板定义
"""

from .workflow_engine import WorkflowEngine, Workflow


def create_project_development_workflow(engine: WorkflowEngine) -> Workflow:
    """创建项目开发工作流模板"""
    
    workflow = engine.create_workflow(
        name="项目开发工作流",
        description="从需求分析到项目交付的完整流程",
        metadata={
            "category": "项目开发",
            "estimated_duration": "2-3个月"
        }
    )
    
    # 步骤1: 需求分析
    workflow.add_step(
        step_type="create_plan",
        role_name="项目经理",
        input_data={
            "requirements": "{{requirements}}",
            "timeline": "{{timeline}}"
        },
        metadata={"step_name": "项目计划制定"}
    )
    
    # 步骤2: 架构设计（依赖步骤1）
    workflow.add_step(
        step_type="design_architecture",
        role_name="系统架构师",
        input_data={
            "requirements": "{{requirements}}",
            "constraints": "{{constraints}}"
        },
        depends_on=["step_1"],
        metadata={"step_name": "系统架构设计"}
    )
    
    # 步骤3: 前端开发（依赖步骤2）
    workflow.add_step(
        step_type="implement_ui",
        role_name="前端工程师",
        input_data={
            "design": "{{step_2.result}}",
            "requirements": "{{requirements}}"
        },
        depends_on=["step_2"],
        metadata={"step_name": "前端界面开发"}
    )
    
    # 步骤4: 后端开发（依赖步骤2）
    workflow.add_step(
        step_type="implement_api",
        role_name="后端工程师",
        input_data={
            "api_spec": "{{step_2.result}}",
            "requirements": "{{requirements}}"
        },
        depends_on=["step_2"],
        metadata={"step_name": "后端API开发"}
    )
    
    # 步骤5: 系统监控（依赖步骤3和4）
    workflow.add_step(
        step_type="monitor_system",
        role_name="运维工程师",
        input_data={
            "metrics": {}
        },
        depends_on=["step_3", "step_4"],
        metadata={"step_name": "系统监控"}
    )
    
    return workflow


def create_bug_fix_workflow(engine: WorkflowEngine) -> Workflow:
    """创建Bug修复工作流模板"""
    
    workflow = engine.create_workflow(
        name="Bug修复工作流",
        description="从问题发现到修复完成的流程",
        metadata={
            "category": "问题修复",
            "estimated_duration": "1-3天"
        }
    )
    
    # 步骤1: 问题分析
    workflow.add_step(
        step_type="solve_problem",
        role_name="系统架构师",
        input_data={
            "problem": "{{bug_description}}",
            "context": "{{context}}"
        },
        metadata={"step_name": "问题分析"}
    )
    
    # 步骤2: 修复实施（根据问题类型选择角色）
    workflow.add_step(
        step_type="fix_bug",
        role_name="后端工程师",  # 默认后端，实际应该根据问题类型动态选择
        input_data={
            "bug_description": "{{bug_description}}",
            "code": "{{code}}"
        },
        depends_on=["step_1"],
        metadata={"step_name": "Bug修复"}
    )
    
    return workflow


def register_all_templates(engine: WorkflowEngine):
    """注册所有工作流模板"""
    templates = {
        "project_development": create_project_development_workflow(engine),
        "bug_fix": create_bug_fix_workflow(engine)
    }
    
    for name, workflow in templates.items():
        engine.register_template(name, workflow)
    
    return templates


