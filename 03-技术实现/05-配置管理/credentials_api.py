#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码数据库API接口
供数字人调用，获取服务凭证
"""

import os
from typing import Dict, Optional
from credentials_manager import CredentialsManager


class CredentialsAPI:
    """密码数据库API接口"""
    
    def __init__(self, master_password: Optional[str] = None):
        """
        初始化API
        
        Args:
            master_password: 主密码（如果为None，会从环境变量读取或提示输入）
        """
        # 尝试从环境变量获取主密码
        if not master_password:
            master_password = os.getenv('CREDENTIALS_MASTER_PASSWORD')
        
        self.manager = CredentialsManager(master_password=master_password)
    
    def get_service_config(self, service_name: str) -> Optional[Dict]:
        """
        获取服务配置（包括凭证）
        
        Args:
            service_name: 服务名称
        
        Returns:
            服务配置字典
        """
        return self.manager.get_service(service_name)
    
    def get_credentials(self, service_name: str) -> Optional[Dict]:
        """
        获取服务凭证（扁平化格式）
        
        Args:
            service_name: 服务名称
        
        Returns:
            凭证字典
        """
        return self.manager.get_credentials(service_name)
    
    def set_env_variables(self, service_name: str, prefix: str = "") -> bool:
        """
        将服务凭证设置为环境变量
        
        Args:
            service_name: 服务名称
            prefix: 环境变量前缀（如 "RAGFLOW_"）
        
        Returns:
            是否成功
        """
        service = self.manager.get_service(service_name)
        if not service:
            return False
        
        # 设置基础URL
        if service.get('base_url'):
            env_key = f"{prefix}BASE_URL" if prefix else "BASE_URL"
            os.environ[env_key] = service['base_url']
        
        # 设置凭证
        credentials = self.manager.get_credentials(service_name)
        if credentials:
            for key, value in credentials.items():
                env_key = f"{prefix}{key.upper()}" if prefix else key.upper()
                os.environ[env_key] = value
        
        return True
    
    def get_ragflow_config(self) -> Optional[Dict]:
        """
        获取RAGFlow配置（便捷方法）
        
        Returns:
            RAGFlow配置字典
        """
        return self.get_service_config("RAGFlow")
    
    def set_ragflow_env(self) -> bool:
        """
        设置RAGFlow环境变量（便捷方法）
        
        Returns:
            是否成功
        """
        return self.set_env_variables("RAGFlow", prefix="RAGFLOW_")


# 便捷函数
def get_credentials(service_name: str) -> Optional[Dict]:
    """获取服务凭证"""
    api = CredentialsAPI()
    return api.get_credentials(service_name)


def get_service_config(service_name: str) -> Optional[Dict]:
    """获取服务配置"""
    api = CredentialsAPI()
    return api.get_service_config(service_name)


def set_env_variables(service_name: str, prefix: str = "") -> bool:
    """设置环境变量"""
    api = CredentialsAPI()
    return api.set_env_variables(service_name, prefix)


if __name__ == "__main__":
    # 测试代码
    api = CredentialsAPI()
    
    # 测试获取RAGFlow配置
    ragflow_config = api.get_ragflow_config()
    if ragflow_config:
        print("RAGFlow配置：")
        print(f"  地址: {ragflow_config.get('base_url')}")
        print(f"  凭证: {ragflow_config.get('credentials', {})}")
    else:
        print("RAGFlow配置不存在")

