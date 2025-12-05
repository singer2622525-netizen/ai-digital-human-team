#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码自动收集器
在工作过程中自动检测和收集账号密码
"""

import re
import json
from typing import Dict, Optional, List
from datetime import datetime
from credentials_manager import CredentialsManager
from credentials_auto import AutoCredentialsManager


class CredentialsCollector:
    """密码自动收集器"""

    def __init__(self, master_password: Optional[str] = None):
        """
        初始化收集器

        Args:
            master_password: 主密码
        """
        self.manager = CredentialsManager(master_password=master_password)
        self.auto_manager = AutoCredentialsManager(master_password=master_password)

        # 收集规则
        self.collection_patterns = {
            'url': r'https?://[^\s]+',
            'username': r'用户名[：:]\s*(\S+)',
            'password': r'密码[：:]\s*(\S+)',
            'api_key': r'API[_\s]?[Kk]ey[：:]\s*(\S+)',
            'token': r'[Tt]oken[：:]\s*(\S+)',
        }

    def extract_from_text(self, text: str) -> Dict:
        """
        从文本中提取账号密码信息

        Args:
            text: 文本内容（可能是错误信息、日志、配置等）

        Returns:
            提取的信息字典
        """
        extracted = {
            'urls': [],
            'usernames': [],
            'passwords': [],
            'api_keys': [],
            'tokens': [],
            'service_name': None,
        }

        # 提取URL
        urls = re.findall(self.collection_patterns['url'], text)
        extracted['urls'] = urls

        # 提取用户名
        usernames = re.findall(self.collection_patterns['username'], text)
        extracted['usernames'] = usernames

        # 提取密码
        passwords = re.findall(self.collection_patterns['password'], text)
        extracted['passwords'] = passwords

        # 提取API密钥
        api_keys = re.findall(self.collection_patterns['api_key'], text)
        extracted['api_keys'] = api_keys

        # 提取Token
        tokens = re.findall(self.collection_patterns['token'], text)
        extracted['tokens'] = tokens

        # 检测服务名称
        extracted['service_name'] = self.auto_manager.detect_service_from_context(text)

        return extracted

    def collect_from_error(self, error_message: str) -> Optional[Dict]:
        """
        从错误信息中收集账号密码需求

        Args:
            error_message: 错误信息

        Returns:
            收集到的信息和建议
        """
        extracted = self.extract_from_text(error_message)

        # 检测是否需要凭证
        service_name = extracted['service_name']
        if not service_name:
            return None

        # 检查密码库中是否已有凭证
        existing_credentials = self.auto_manager.api.get_credentials(service_name)

        result = {
            'service_name': service_name,
            'needs_credentials': not existing_credentials,
            'extracted_info': extracted,
            'suggestion': None,
        }

        # 如果检测到URL，建议添加服务
        if extracted['urls']:
            result['suggestion'] = {
                'action': 'add_service',
                'service_name': service_name,
                'base_url': extracted['urls'][0],
            }

        # 如果检测到用户名和密码，建议添加凭证
        if extracted['usernames'] and extracted['passwords']:
            result['suggestion'] = {
                'action': 'add_credentials',
                'service_name': service_name,
                'username': extracted['usernames'][0],
                'password': extracted['passwords'][0],
            }

        return result

    def auto_collect_and_save(self, context: str, interactive: bool = True) -> bool:
        """
        自动收集并保存凭证

        Args:
            context: 上下文信息（错误信息、日志等）
            interactive: 是否交互式确认

        Returns:
            是否成功保存
        """
        extracted = self.extract_from_text(context)
        service_name = extracted['service_name']

        if not service_name:
            print("⚠️  无法从上下文中检测到服务名称")
            return False

        # 检查是否已有凭证
        existing = self.auto_manager.api.get_credentials(service_name)
        if existing:
            print(f"✅ 服务 '{service_name}' 的凭证已存在")
            return True

        # 提取信息
        if extracted['urls']:
            base_url = extracted['urls'][0]
        else:
            base_url = input(f"请输入 {service_name} 的服务地址: ").strip()

        # 添加服务
        self.manager.add_service(
            service_name=service_name,
            service_type="",
            base_url=base_url
        )

        # 添加凭证
        if extracted['usernames'] and extracted['passwords']:
            # 自动提取
            username = extracted['usernames'][0]
            password = extracted['passwords'][0]

            if interactive:
                print(f"\n检测到以下信息：")
                print(f"  用户名: {username}")
                print(f"  密码: {'*' * len(password)}")
                confirm = input("是否保存到密码库？(y/n): ")
                if confirm.lower() != 'y':
                    return False

            self.manager.add_credential(
                service_name=service_name,
                credential_type='username_password',
                key_name='username',
                value=username
            )

            self.manager.add_credential(
                service_name=service_name,
                credential_type='username_password',
                key_name='password',
                value=password
            )

            print(f"✅ '{service_name}' 的凭证已保存到密码库")
            return True
        else:
            # 手动输入
            return self.auto_manager.prompt_add_credentials(service_name, context)

    def monitor_and_collect(self, log_file: str, watch_patterns: List[str] = None):
        """
        监控日志文件并自动收集凭证需求

        Args:
            log_file: 日志文件路径
            watch_patterns: 监控的模式列表（如果为None，使用默认模式）
        """
        if watch_patterns is None:
            watch_patterns = [
                r'认证失败',
                r'需要登录',
                r'unauthorized',
                r'credential',
            ]

        # 这里可以实现文件监控逻辑
        # 可以使用 watchdog 库监控文件变化
        print(f"📊 开始监控日志文件: {log_file}")
        print(f"监控模式: {watch_patterns}")


def main():
    """命令行工具"""
    import argparse

    parser = argparse.ArgumentParser(description='密码自动收集器')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 从文本提取
    parser_extract = subparsers.add_parser('extract', help='从文本提取信息')
    parser_extract.add_argument('text', help='文本内容')

    # 从错误收集
    parser_error = subparsers.add_parser('collect-from-error', help='从错误信息收集')
    parser_error.add_argument('error', help='错误信息')

    # 自动收集并保存
    parser_auto = subparsers.add_parser('auto-collect', help='自动收集并保存')
    parser_auto.add_argument('context', help='上下文信息')
    parser_auto.add_argument('--no-interactive', action='store_true', help='非交互模式')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    collector = CredentialsCollector()

    if args.command == 'extract':
        extracted = collector.extract_from_text(args.text)
        print("\n提取的信息：")
        print(json.dumps(extracted, indent=2, ensure_ascii=False))

    elif args.command == 'collect-from-error':
        result = collector.collect_from_error(args.error)
        if result:
            print("\n收集结果：")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("未检测到需要凭证的服务")

    elif args.command == 'auto-collect':
        collector.auto_collect_and_save(
            args.context,
            interactive=not args.no_interactive
        )


if __name__ == "__main__":
    main()
