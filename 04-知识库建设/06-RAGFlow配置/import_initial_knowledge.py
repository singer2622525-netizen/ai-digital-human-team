#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入初始知识到RAGFlow知识库
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from ragflow_client import RAGFlowClient
except ImportError:
    print("错误：无法导入RAGFlowClient，请确保ragflow_client.py在同一目录")
    sys.exit(1)


# 知识库映射
KNOWLEDGE_BASE_MAPPING = {
    "organization_knowledge": {
        "name": "组织架构知识库",
        "files": [
            "01-项目构想/组织架构详细设计.md",
            "01-项目构想/项目章程.md",
            "01-项目构想/技术选型.md",
        ]
    },
    "digital_human_knowledge": {
        "name": "数字人知识库",
        "files": [
            "02-数字人设计/00-智能产品规划师/角色定义.md",
            "02-数字人设计/00-智能产品规划师/知识理解与关联分析.md",
            "02-数字人设计/00-智能产品规划师/数字人监控与知识沉淀.md",
            "02-数字人设计/00-智能产品规划师/参考软件分析能力.md",
            "02-数字人设计/00-智能产品规划师/音频语音处理能力.md",
            "02-数字人设计/04-实时记录员/角色定义.md",
            "02-数字人设计/05-质量观察员/角色定义.md",
            "02-数字人设计/06-知识管理员/角色定义.md",
            "02-数字人设计/项目经理.md",
            "02-数字人设计/系统架构师.md",
            "02-数字人设计/前端工程师.md",
            "02-数字人设计/后端工程师.md",
            "02-数字人设计/运维工程师.md",
        ]
    },
    "technical_knowledge": {
        "name": "技术知识库",
        "files": [
            "01-项目构想/技术选型.md",
            "01-项目构想/智能产品规划师-实现方案.md",
            "03-技术实现/02-功能模块/README.md",
        ]
    },
    "project_experience": {
        "name": "项目经验知识库",
        "files": [
            # 项目经验文档（如果有）
        ]
    },
    "business_knowledge": {
        "name": "业务知识库",
        "files": [
            # 业务文档（如果有）
        ]
    },
    "error_knowledge": {
        "name": "错误知识库",
        "files": [
            # 错误记录（如果有）
        ]
    },
    "best_practices": {
        "name": "最佳实践知识库",
        "files": [
            # 最佳实践文档（如果有）
        ]
    },
    "company_development": {
        "name": "公司发展知识库",
        "files": [
            # 公司发展文档（如果有）
        ]
    },
}


def read_file_content(file_path: str) -> Optional[str]:
    """读取文件内容"""
    full_path = project_root / file_path
    if not full_path.exists():
        print(f"⚠️  文件不存在：{file_path}")
        return None

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败：{file_path}, 错误：{e}")
        return None


def import_to_knowledge_base(client: RAGFlowClient, kb_name: str, kb_config: Dict):
    """导入知识到指定知识库"""
    print(f"\n📚 开始导入：{kb_config['name']} ({kb_name})")

    files = kb_config.get("files", [])
    if not files:
        print(f"  ⚠️  没有文件需要导入")
        return 0, 0

    success_count = 0
    fail_count = 0

    for file_path in files:
        print(f"  📄 处理文件：{file_path}")

        content = read_file_content(file_path)
        if not content:
            fail_count += 1
            continue

        # 准备元数据
        metadata = {
            "source": file_path,
            "type": "markdown",
            "category": kb_name,
        }

        try:
            # 使用RAGFlow API保存知识
            result = client.add_document(
                knowledge_base=kb_name,
                content=content,
                metadata=metadata
            )

            if result.get("success"):
                print(f"    ✅ 导入成功")
                success_count += 1
            else:
                print(f"    ❌ 导入失败：{result.get('error', '未知错误')}")
                fail_count += 1

        except Exception as e:
            print(f"    ❌ 导入异常：{e}")
            fail_count += 1

    print(f"\n  📊 导入结果：成功 {success_count} 个，失败 {fail_count} 个")
    return success_count, fail_count


def main():
    """主函数"""
    print("=" * 60)
    print("RAGFlow 初始知识导入工具")
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
    if not client.test_connection():
        print("❌ RAGFlow连接失败，请检查配置")
        return
    print("✅ RAGFlow连接成功")

    # 确认操作
    print("\n" + "=" * 60)
    print("准备导入以下知识库：")
    for kb_name, kb_config in KNOWLEDGE_BASE_MAPPING.items():
        file_count = len(kb_config.get("files", []))
        print(f"  - {kb_config['name']} ({kb_name}): {file_count} 个文件")
    print("=" * 60)

    confirm = input("\n是否继续导入？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消导入")
        return

    # 开始导入
    print("\n🚀 开始导入...")
    total_success = 0
    total_fail = 0

    for kb_name, kb_config in KNOWLEDGE_BASE_MAPPING.items():
        try:
            success, fail = import_to_knowledge_base(client, kb_name, kb_config)
            total_success += success
            total_fail += fail
        except Exception as e:
            print(f"❌ 导入知识库 {kb_name} 时出错：{e}")
            import traceback
            traceback.print_exc()

    # 总结
    print("\n" + "=" * 60)
    print("导入完成！")
    print("=" * 60)
    print(f"总计：成功 {total_success} 个，失败 {total_fail} 个")
    print("\n💡 提示：")
    print("  - 可以在RAGFlow Web界面中查看导入的知识")
    print("  - 可以使用API测试知识检索功能")


if __name__ == "__main__":
    main()
