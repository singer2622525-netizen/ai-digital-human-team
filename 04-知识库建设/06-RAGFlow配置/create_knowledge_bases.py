#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在RAGFlow上创建8个知识库
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from ragflow_client import RAGFlowClient
except ImportError:
    print("错误：无法导入RAGFlowClient，请确保ragflow_client.py在同一目录")
    sys.exit(1)


# 8个知识库配置
KNOWLEDGE_BASES = [
    {
        "name": "organization_knowledge",
        "description": "组织架构知识库 - 存储组织架构相关的知识（组织架构设计文档、岗位职责定义、流程设计文档、协作机制说明）"
    },
    {
        "name": "project_experience",
        "description": "项目经验知识库 - 存储项目执行过程中的经验（项目成功经验、项目失败教训、问题解决方案、最佳实践）"
    },
    {
        "name": "technical_knowledge",
        "description": "技术知识库 - 存储技术相关的知识（技术选型文档、技术方案设计、技术实现经验、技术问题解决方案）"
    },
    {
        "name": "business_knowledge",
        "description": "业务知识库 - 存储业务相关的知识（业务需求分析、业务流程设计、业务规则定义、业务场景说明）"
    },
    {
        "name": "digital_human_knowledge",
        "description": "数字人知识库 - 存储数字人相关的知识（数字人角色定义、数字人工作模式、数字人协作经验、数字人能力评估）"
    },
    {
        "name": "error_knowledge",
        "description": "错误知识库 - 存储错误和教训（错误记录、错误原因分析、错误解决方案、错误预防措施）"
    },
    {
        "name": "best_practices",
        "description": "最佳实践知识库 - 存储最佳实践和闪光点（闪光点记录、成功经验总结、最佳实践文档、可复用方案）"
    },
    {
        "name": "company_development",
        "description": "公司发展知识库 - 存储公司发展相关的知识（公司战略分析、业务发展趋势、项目关联分析、战略建议）"
    },
]


def create_all_knowledge_bases():
    """创建所有知识库"""
    print("=" * 60)
    print("RAGFlow 知识库创建工具")
    print("=" * 60)

    # 初始化RAGFlow客户端
    try:
        client = RAGFlowClient()
        print("✅ RAGFlow客户端初始化成功")
    except Exception as e:
        print(f"❌ RAGFlow客户端初始化失败：{e}")
        print("请检查环境变量配置：RAGFLOW_BASE_URL, RAGFLOW_API_KEY")
        return

    # 测试连接
    print("\n🔗 测试RAGFlow连接...")
    try:
        existing_kbs = client.list_knowledge_bases()
        print(f"✅ RAGFlow连接成功，当前已有 {len(existing_kbs)} 个知识库")
    except Exception as e:
        print(f"❌ RAGFlow连接失败：{e}")
        print("请检查：")
        print("1. RAGFlow服务是否正常运行")
        print("2. 网络连接是否正常")
        print("3. API地址是否正确")
        return

    # 检查已存在的知识库
    existing_names = {kb.get('name', '') for kb in existing_kbs}

    # 创建知识库
    print("\n📚 开始创建知识库...")
    created = []
    skipped = []
    failed = []

    for kb_config in KNOWLEDGE_BASES:
        kb_name = kb_config['name']
        kb_desc = kb_config['description']

        print(f"\n📖 处理：{kb_name}")

        # 检查是否已存在
        if kb_name in existing_names:
            print(f"  ⚠️  知识库已存在，跳过")
            skipped.append(kb_name)
            continue

        try:
            # 创建知识库
            result = client.create_knowledge_base(
                name=kb_name,
                description=kb_desc
            )

            kb_id = result.get('id') or result.get('kb_id', '')
            if kb_id:
                print(f"  ✅ 创建成功，ID: {kb_id}")
                created.append({
                    "name": kb_name,
                    "id": kb_id,
                    "description": kb_desc
                })
            else:
                print(f"  ⚠️  创建成功，但未获取到ID")
                created.append({
                    "name": kb_name,
                    "id": "未知",
                    "description": kb_desc
                })

        except Exception as e:
            print(f"  ❌ 创建失败：{e}")
            failed.append(kb_name)

    # 总结
    print("\n" + "=" * 60)
    print("创建结果总结")
    print("=" * 60)
    print(f"✅ 成功创建：{len(created)} 个")
    print(f"⚠️  已存在（跳过）：{len(skipped)} 个")
    print(f"❌ 创建失败：{len(failed)} 个")

    if created:
        print("\n📋 已创建的知识库：")
        for kb in created:
            print(f"  - {kb['name']} (ID: {kb['id']})")

    if skipped:
        print("\n⚠️  已存在的知识库（已跳过）：")
        for name in skipped:
            print(f"  - {name}")

    if failed:
        print("\n❌ 创建失败的知识库：")
        for name in failed:
            print(f"  - {name}")

    # 保存知识库ID到文件（可选）
    if created:
        print("\n💡 提示：")
        print("  请记录每个知识库的ID，用于后续配置")
        print("  可以将ID添加到环境变量配置文件中")

    print("\n" + "=" * 60)
    print("知识库创建完成！")
    print("=" * 60)


if __name__ == "__main__":
    create_all_knowledge_bases()
