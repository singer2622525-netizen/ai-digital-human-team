#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码数据库自动收集和调用模块
在工作过程中自动检测、收集和使用账号密码
"""

import os
import re
import json
import getpass
from typing import Dict, Optional, List, Callable
from datetime import datetime
from credentials_api import CredentialsAPI
from credentials_manager import CredentialsManager


class AutoCredentialsManager:
    """自动密码管理器"""

    def __init__(self, master_password: Optional[str] = None):
        """
        初始化自动密码管理器

        Args:
            master_password: 主密码
        """
        self.api = CredentialsAPI(master_password=master_password)
        self.manager = CredentialsManager(master_password=master_password)

        # 服务检测规则
        self.service_patterns = {
            'RAGFlow': {
                'url_patterns': [
                    r'ragflow\.suuntoyun\.com',
                    r'ragflow',
                    r'知识库',
                ],
                'required_credentials': ['username', 'password'],
                'env_prefix': 'RAGFLOW_',
            },
            'frp': {
                'url_patterns': [
                    r'frp',
                    r'内网穿透',
                ],
                'required_credentials': ['username', 'password', 'server_addr'],
                'env_prefix': 'FRP_',
            },
            'DuckDNS': {
                'url_patterns': [
                    r'duckdns',
                    r'域名',
                ],
                'required_credentials': ['token', 'domain'],
                'env_prefix': 'DUCKDNS_',
            },
        }

        # 使用日志
        self.usage_log = []

    def detect_service_from_context(self, context: str) -> Optional[str]:
        """
        从上下文中检测服务名称

        Args:
            context: 上下文文本（可能是错误信息、日志、配置等）

        Returns:
            检测到的服务名称，如果未检测到返回None
        """
        context_lower = context.lower()

        for service_name, patterns in self.service_patterns.items():
            for pattern in patterns['url_patterns']:
                if re.search(pattern, context_lower, re.IGNORECASE):
                    return service_name

        return None

    def auto_get_credentials(self,
                            service_name: Optional[str] = None,
                            context: Optional[str] = None,
                            auto_set_env: bool = True) -> Optional[Dict]:
        """
        自动获取凭证

        Args:
            service_name: 服务名称（如果为None，会尝试从context检测）
            context: 上下文文本（用于检测服务）
            auto_set_env: 是否自动设置环境变量

        Returns:
            凭证字典，如果未找到返回None
        """
        # 如果未指定服务名称，尝试从上下文检测
        if not service_name and context:
            service_name = self.detect_service_from_context(context)

        if not service_name:
            return None

        # 获取凭证
        credentials = self.api.get_credentials(service_name)

        if credentials:
            # 记录使用日志
            self._log_usage(service_name, 'auto_get', success=True)

            # 自动设置环境变量
            if auto_set_env:
                patterns = self.service_patterns.get(service_name, {})
                prefix = patterns.get('env_prefix', '')
                self.api.set_env_variables(service_name, prefix)

            return credentials
        else:
            # 记录失败日志
            self._log_usage(service_name, 'auto_get', success=False)
            return None

    def auto_collect_from_error(self, error_message: str) -> Optional[str]:
        """
        从错误信息中自动收集账号密码需求

        Args:
            error_message: 错误信息

        Returns:
            建议的服务名称，如果检测到需要凭证
        """
        # 检测常见的认证错误
        auth_errors = [
            r'认证失败',
            r'未授权',
            r'unauthorized',
            r'需要登录',
            r'需要密码',
            r'credential',
            r'authentication',
            r'login',
        ]

        for pattern in auth_errors:
            if re.search(pattern, error_message, re.IGNORECASE):
                # 尝试检测服务
                service_name = self.detect_service_from_context(error_message)
                if service_name:
                    return service_name

        return None

    def prompt_add_credentials(self, service_name: str, context: str = "") -> bool:
        """
        提示用户添加凭证

        Args:
            service_name: 服务名称
            context: 上下文信息

        Returns:
            是否成功添加
        """
        print(f"\n⚠️  检测到需要 '{service_name}' 服务的凭证，但密码库中不存在")
        print(f"上下文: {context}")

        # 获取服务信息
        service_info = self.service_patterns.get(service_name, {})
        required_creds = service_info.get('required_credentials', [])

        if not required_creds:
            print(f"❌ 未知服务类型，无法提示")
            return False

        print(f"\n需要添加以下凭证：")
        for cred in required_creds:
            print(f"  - {cred}")

        confirm = input(f"\n是否现在添加 '{service_name}' 的凭证？(y/n): ")
        if confirm.lower() != 'y':
            return False

        # 检查服务是否存在
        existing_service = self.api.get_service_config(service_name)
        if not existing_service:
            # 添加服务
            url = input(f"请输入 {service_name} 的服务地址（可选）: ").strip()
            service_type = input(f"请输入服务类型（可选）: ").strip()

            self.manager.add_service(
                service_name=service_name,
                service_type=service_type,
                base_url=url
            )

        # 添加凭证
        credentials = {}
        for cred in required_creds:
            value = getpass.getpass(f"请输入 {cred}: ")
            if value:
                # 确定凭证类型
                if cred in ['username', 'password']:
                    cred_type = 'username_password'
                elif cred in ['token', 'api_key']:
                    cred_type = 'api_key'
                else:
                    cred_type = 'other'

                self.manager.add_credential(
                    service_name=service_name,
                    credential_type=cred_type,
                    key_name=cred,
                    value=value
                )
                credentials[cred] = value

        print(f"✅ '{service_name}' 的凭证已添加")
        return True

    def auto_handle_service_call(self,
                                 service_name: str,
                                 callback: Callable,
                                 *args,
                                 **kwargs) -> any:
        """
        自动处理服务调用（如果失败，自动获取凭证并重试）

        Args:
            service_name: 服务名称
            callback: 回调函数（需要凭证的服务调用）
            *args: 回调函数参数
            **kwargs: 回调函数关键字参数

        Returns:
            回调函数的返回值
        """
        # 第一次尝试
        try:
            return callback(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)

            # 检测是否是认证错误
            if self.auto_collect_from_error(error_msg) == service_name:
                # 自动获取凭证
                credentials = self.auto_get_credentials(service_name)

                if credentials:
                    # 重试
                    try:
                        return callback(*args, **kwargs)
                    except Exception as retry_error:
                        print(f"❌ 重试后仍然失败: {retry_error}")
                        raise
                else:
                    # 提示用户添加凭证
                    if self.prompt_add_credentials(service_name, error_msg):
                        # 再次重试
                        credentials = self.auto_get_credentials(service_name)
                        if credentials:
                            try:
                                return callback(*args, **kwargs)
                            except Exception as retry_error:
                                print(f"❌ 添加凭证后仍然失败: {retry_error}")
                                raise
            else:
                # 其他错误，直接抛出
                raise

    def _log_usage(self, service_name: str, action: str, success: bool, details: str = ""):
        """记录使用日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'service_name': service_name,
            'action': action,
            'success': success,
            'details': details,
        }
        self.usage_log.append(log_entry)

    def get_usage_log(self, service_name: Optional[str] = None) -> List[Dict]:
        """
        获取使用日志

        Args:
            service_name: 服务名称（如果指定，只返回该服务的日志）

        Returns:
            日志列表
        """
        if service_name:
            return [log for log in self.usage_log if log['service_name'] == service_name]
        return self.usage_log

    def register_service_pattern(self,
                                service_name: str,
                                url_patterns: List[str],
                                required_credentials: List[str],
                                env_prefix: str = ""):
        """
        注册服务检测规则

        Args:
            service_name: 服务名称
            url_patterns: URL匹配模式列表
            required_credentials: 必需的凭证列表
            env_prefix: 环境变量前缀
        """
        self.service_patterns[service_name] = {
            'url_patterns': url_patterns,
            'required_credentials': required_credentials,
            'env_prefix': env_prefix,
        }


# 全局实例（单例模式）
_global_manager: Optional[AutoCredentialsManager] = None


def get_auto_manager(master_password: Optional[str] = None) -> AutoCredentialsManager:
    """获取全局自动密码管理器实例"""
    global _global_manager
    if _global_manager is None:
        _global_manager = AutoCredentialsManager(master_password=master_password)
    return _global_manager


# 便捷函数
def auto_get_credentials(service_name: Optional[str] = None,
                        context: Optional[str] = None) -> Optional[Dict]:
    """自动获取凭证"""
    manager = get_auto_manager()
    return manager.auto_get_credentials(service_name, context)


def auto_handle_service(service_name: str, callback: Callable, *args, **kwargs) -> any:
    """自动处理服务调用"""
    manager = get_auto_manager()
    return manager.auto_handle_service_call(service_name, callback, *args, **kwargs)


if __name__ == "__main__":
    # 测试代码
    manager = AutoCredentialsManager()

    # 测试服务检测
    context = "连接RAGFlow知识库失败，需要认证"
    service = manager.detect_service_from_context(context)
    print(f"检测到的服务: {service}")

    # 测试自动获取凭证
    credentials = manager.auto_get_credentials(service_name="RAGFlow")
    if credentials:
        print(f"获取到的凭证: {list(credentials.keys())}")
    else:
        print("未找到凭证")
