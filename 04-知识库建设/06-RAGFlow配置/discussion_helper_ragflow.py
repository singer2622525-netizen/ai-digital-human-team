#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讨论助手 - 使用RAGFlow的交互式添加和查询讨论记录
"""

from ragflow_client import DiscussionRecorderRAGFlow
from datetime import datetime
import os


def interactive_add():
    """交互式添加讨论记录"""
    try:
        recorder = DiscussionRecorderRAGFlow()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n请检查环境变量配置:")
        print("  RAGFLOW_BASE_URL - RAGFlow服务地址")
        print("  RAGFLOW_API_KEY - API密钥（如果需要）")
        print("  RAGFLOW_KB_ID - 知识库ID")
        return

    print("\n" + "="*60)
    print("📝 添加讨论记录（RAGFlow）")
    print("="*60)

    topic = input("讨论主题: ").strip()
    if not topic:
        print("❌ 主题不能为空")
        return

    print("\n讨论内容（输入多行，输入空行结束）:")
    content_lines = []
    while True:
        line = input()
        if line.strip() == "" and content_lines:
            break
        content_lines.append(line)

    content = "\n".join(content_lines)
    if not content.strip():
        print("❌ 内容不能为空")
        return

    print("\n分类选项:")
    print("1. 组织架构")
    print("2. 岗位配置")
    print("3. 流程设计")
    print("4. 数字人实现")
    print("5. 人工治理")
    print("6. 项目经验")
    print("7. 技术知识")
    print("8. 其他")

    cat_choice = input("选择分类 (1-8，直接回车使用'其他'): ").strip()
    category_map = {
        "1": "组织架构",
        "2": "岗位配置",
        "3": "流程设计",
        "4": "数字人实现",
        "5": "人工治理",
        "6": "项目经验",
        "7": "技术知识",
        "8": "其他"
    }
    category = category_map.get(cat_choice, "其他")

    has_decision = input("是否有决策结果？(y/N): ").strip().lower()
    decision = None
    if has_decision == 'y':
        print("\n决策结果（输入多行，输入空行结束）:")
        decision_lines = []
        while True:
            line = input()
            if line.strip() == "" and decision_lines:
                break
            decision_lines.append(line)
        decision = "\n".join(decision_lines)

    tags_input = input("标签（用逗号分隔，可选）: ").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else None

    try:
        doc_id = recorder.add_discussion(topic, content, category, decision, tags)
        print(f"\n✅ 讨论记录已添加到RAGFlow，ID: {doc_id}")
    except Exception as e:
        print(f"\n❌ 添加失败: {e}")
        import traceback
        traceback.print_exc()


def interactive_search():
    """交互式搜索讨论记录"""
    try:
        recorder = DiscussionRecorderRAGFlow()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    print("\n" + "="*60)
    print("🔍 搜索讨论记录（RAGFlow）")
    print("="*60)

    query = input("搜索关键词: ").strip()
    if not query:
        print("❌ 搜索关键词不能为空")
        return

    print("\n分类筛选（可选，直接回车跳过）:")
    print("1. 组织架构")
    print("2. 岗位配置")
    print("3. 流程设计")
    print("4. 数字人实现")
    print("5. 人工治理")
    print("6. 项目经验")
    print("7. 技术知识")
    print("8. 其他")
    print("0. 不筛选")

    cat_choice = input("选择分类 (0-8，默认0): ").strip() or "0"
    category_map = {
        "1": "组织架构",
        "2": "岗位配置",
        "3": "流程设计",
        "4": "数字人实现",
        "5": "人工治理",
        "6": "项目经验",
        "7": "技术知识",
        "8": "其他",
        "0": None
    }
    category = category_map.get(cat_choice)

    n_results = input("返回结果数量 (默认5): ").strip()
    n_results = int(n_results) if n_results.isdigit() else 5

    try:
        results = recorder.search_discussions(query, category, n_results)

        if results:
            print(f"\n找到 {len(results)} 条相关讨论：\n")
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                print(f"{i}. [{metadata.get('category', '未知')}] {metadata.get('topic', '未知')}")
                print(f"   ID: {result.get('id', '未知')}")
                print(f"   时间：{metadata.get('timestamp', '未知')}")
                if result.get('score'):
                    print(f"   相似度：{result['score']:.2%}")

                # 显示内容预览
                content = result.get('content', '')
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"   预览：{preview}")
                print()

            # 询问是否查看详情
            show_detail = input("输入序号查看详情（直接回车跳过）: ").strip()
            if show_detail.isdigit():
                idx = int(show_detail) - 1
                if 0 <= idx < len(results):
                    recorder.display_discussion(results[idx])
        else:
            print("\n未找到相关讨论")
    except Exception as e:
        print(f"\n❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()


def interactive_list():
    """交互式列出所有讨论"""
    try:
        recorder = DiscussionRecorderRAGFlow()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    print("\n" + "="*60)
    print("📋 所有讨论记录（RAGFlow）")
    print("="*60)

    print("\n分类筛选（可选）:")
    print("1. 组织架构")
    print("2. 岗位配置")
    print("3. 流程设计")
    print("4. 数字人实现")
    print("5. 人工治理")
    print("6. 项目经验")
    print("7. 技术知识")
    print("8. 其他")
    print("0. 显示全部")

    cat_choice = input("选择分类 (0-8，默认0): ").strip() or "0"
    category_map = {
        "1": "组织架构",
        "2": "岗位配置",
        "3": "流程设计",
        "4": "数字人实现",
        "5": "人工治理",
        "6": "项目经验",
        "7": "技术知识",
        "8": "其他",
        "0": None
    }
    category = category_map.get(cat_choice)

    try:
        discussions = recorder.get_all_discussions(category)

        if discussions:
            print(f"\n共有 {len(discussions)} 条讨论记录：\n")
            for i, disc in enumerate(discussions, 1):
                metadata = disc.get('metadata', {})
                print(f"{i}. [{metadata.get('category', '未知')}] {metadata.get('topic', '未知')}")
                print(f"   ID: {disc.get('id', '未知')}")
                print(f"   时间：{metadata.get('timestamp', '未知')}")
                if metadata.get('has_decision') == 'true':
                    print("   ✅ 已决策")
                print()

            # 询问是否查看详情
            show_detail = input("输入序号查看详情（直接回车跳过）: ").strip()
            if show_detail.isdigit():
                idx = int(show_detail) - 1
                if 0 <= idx < len(discussions):
                    recorder.display_discussion(discussions[idx])
        else:
            print("\n暂无讨论记录")
    except Exception as e:
        print(f"\n❌ 获取列表失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主菜单"""
    while True:
        print("\n" + "="*60)
        print("🗣️  组织架构讨论记录系统（RAGFlow）")
        print("="*60)
        print("1. 添加讨论记录")
        print("2. 搜索讨论记录")
        print("3. 列出所有讨论")
        print("4. 查看统计信息")
        print("5. 测试连接")
        print("0. 退出")
        print("="*60)

        choice = input("\n请选择 (0-5): ").strip()

        if choice == "1":
            interactive_add()
        elif choice == "2":
            interactive_search()
        elif choice == "3":
            interactive_list()
        elif choice == "4":
            try:
                recorder = DiscussionRecorderRAGFlow()
                stats = recorder.get_statistics()
                print("\n" + "="*60)
                print("📊 讨论记录统计（RAGFlow）")
                print("="*60)
                print(f"总讨论数：{stats['total_discussions']}")
                print(f"已决策数：{stats['total_decisions']}")
                print("\n分类统计：")
                for cat, count in stats['categories'].items():
                    print(f"  {cat}: {count}")
                print("="*60)
            except Exception as e:
                print(f"\n❌ 获取统计失败: {e}")
        elif choice == "5":
            print("\n正在测试RAGFlow连接...")
            from test_ragflow_connection import test_connection
            test_connection()
        elif choice == "0":
            print("\n再见！")
            break
        else:
            print("\n❌ 无效选择，请重试")


if __name__ == "__main__":
    main()

