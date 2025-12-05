#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码数据库管理工具
集中管理所有服务的账号密码
"""

import os
import sqlite3
import getpass
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class CredentialsManager:
    """密码数据库管理器"""

    def __init__(self, db_path: Optional[str] = None, master_password: Optional[str] = None):
        """
        初始化密码管理器

        Args:
            db_path: 数据库文件路径（默认：~/DeveloperConfig/密码数据库/credentials.db）
            master_password: 主密码（如果为None，会提示输入）
        """
        # 设置数据库路径（项目内存储，与项目捆绑）
        if db_path:
            self.db_path = Path(db_path)
        else:
            # 数据库存储在项目内的配置管理目录
            project_root = Path(__file__).parent.parent.parent.parent
            config_dir = project_root / "03-技术实现" / "05-配置管理" / "密码数据库"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = config_dir / "credentials.db"

        # 获取主密码
        if master_password:
            self.master_password = master_password
        else:
            self.master_password = getpass.getpass("请输入主密码: ")

        # 生成加密密钥
        self.encryption_key = self._generate_key(self.master_password)
        self.cipher = Fernet(self.encryption_key)

        # 初始化数据库
        self._init_database()

        # 设置文件权限
        self._set_file_permissions()

    def _generate_key(self, password: str) -> bytes:
        """从主密码生成加密密钥"""
        # 使用固定的salt（实际应用中应该随机生成并存储）
        salt = b'credentials_manager_salt_2024'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建服务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                service_type TEXT,
                description TEXT,
                base_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建凭证表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                credential_type TEXT NOT NULL,
                key_name TEXT NOT NULL,
                encrypted_value BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id),
                UNIQUE(service_id, credential_type, key_name)
            )
        ''')

        # 创建服务元数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id),
                UNIQUE(service_id, key)
            )
        ''')

        conn.commit()
        conn.close()

    def _set_file_permissions(self):
        """设置数据库文件权限（600：只有所有者可读写）"""
        os.chmod(self.db_path, 0o600)

    def _encrypt(self, value: str) -> bytes:
        """加密值"""
        return self.cipher.encrypt(value.encode())

    def _decrypt(self, encrypted_value: bytes) -> str:
        """解密值"""
        return self.cipher.decrypt(encrypted_value).decode()

    def add_service(self,
                   service_name: str,
                   service_type: str = "",
                   description: str = "",
                   base_url: str = "") -> int:
        """
        添加服务

        Args:
            service_name: 服务名称
            service_type: 服务类型
            description: 服务描述
            base_url: 服务地址

        Returns:
            服务ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO services (service_name, service_type, description, base_url, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (service_name, service_type, description, base_url, datetime.now()))

            service_id = cursor.lastrowid
            conn.commit()
            print(f"✅ 服务 '{service_name}' 添加成功，ID: {service_id}")
            return service_id

        except sqlite3.IntegrityError:
            # 服务已存在，更新
            cursor.execute('''
                UPDATE services
                SET service_type=?, description=?, base_url=?, updated_at=?
                WHERE service_name=?
            ''', (service_type, description, base_url, datetime.now(), service_name))

            cursor.execute('SELECT id FROM services WHERE service_name=?', (service_name,))
            service_id = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ 服务 '{service_name}' 已存在，已更新")
            return service_id

        finally:
            conn.close()

    def add_credential(self,
                      service_name: str,
                      credential_type: str,
                      key_name: str,
                      value: str) -> bool:
        """
        添加凭证

        Args:
            service_name: 服务名称
            credential_type: 凭证类型（username_password, api_key, token等）
            key_name: 键名（username, password, api_key等）
            value: 值（会被加密存储）

        Returns:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取服务ID
            cursor.execute('SELECT id FROM services WHERE service_name=?', (service_name,))
            result = cursor.fetchone()
            if not result:
                print(f"❌ 服务 '{service_name}' 不存在，请先添加服务")
                return False

            service_id = result[0]

            # 加密值
            encrypted_value = self._encrypt(value)

            # 插入或更新凭证
            cursor.execute('''
                INSERT OR REPLACE INTO credentials
                (service_id, credential_type, key_name, encrypted_value, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (service_id, credential_type, key_name, encrypted_value, datetime.now()))

            conn.commit()
            print(f"✅ 凭证 '{key_name}' 添加成功")
            return True

        except Exception as e:
            print(f"❌ 添加凭证失败: {e}")
            return False

        finally:
            conn.close()

    def get_service(self, service_name: str) -> Optional[Dict]:
        """
        获取服务信息（包括凭证）

        Args:
            service_name: 服务名称

        Returns:
            服务信息字典，包含所有凭证
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # 获取服务信息
            cursor.execute('''
                SELECT * FROM services WHERE service_name=?
            ''', (service_name,))
            service_row = cursor.fetchone()

            if not service_row:
                return None

            service = dict(service_row)

            # 获取凭证
            cursor.execute('''
                SELECT credential_type, key_name, encrypted_value
                FROM credentials
                WHERE service_id=?
            ''', (service['id'],))

            credentials = {}
            for row in cursor.fetchall():
                cred_type = row['credential_type']
                key_name = row['key_name']
                encrypted_value = row['encrypted_value']

                # 解密值
                decrypted_value = self._decrypt(encrypted_value)

                if cred_type not in credentials:
                    credentials[cred_type] = {}
                credentials[cred_type][key_name] = decrypted_value

            service['credentials'] = credentials

            # 获取元数据
            cursor.execute('''
                SELECT key, value FROM service_metadata WHERE service_id=?
            ''', (service['id'],))

            metadata = {}
            for row in cursor.fetchall():
                metadata[row['key']] = row['value']

            service['metadata'] = metadata

            return service

        except Exception as e:
            print(f"❌ 获取服务信息失败: {e}")
            return None

        finally:
            conn.close()

    def get_credentials(self, service_name: str) -> Optional[Dict]:
        """
        获取服务的所有凭证（扁平化格式）

        Args:
            service_name: 服务名称

        Returns:
            凭证字典，格式：{"username": "...", "password": "..."}
        """
        service = self.get_service(service_name)
        if not service:
            return None

        # 扁平化凭证
        credentials = {}
        for cred_type, creds in service.get('credentials', {}).items():
            credentials.update(creds)

        return credentials

    def list_services(self) -> List[Dict]:
        """
        列出所有服务

        Returns:
            服务列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT service_name, service_type, description, base_url, created_at
                FROM services
                ORDER BY service_name
            ''')

            services = []
            for row in cursor.fetchall():
                services.append(dict(row))

            return services

        finally:
            conn.close()

    def delete_service(self, service_name: str) -> bool:
        """
        删除服务（包括所有凭证）

        Args:
            service_name: 服务名称

        Returns:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取服务ID
            cursor.execute('SELECT id FROM services WHERE service_name=?', (service_name,))
            result = cursor.fetchone()
            if not result:
                print(f"❌ 服务 '{service_name}' 不存在")
                return False

            service_id = result[0]

            # 删除凭证
            cursor.execute('DELETE FROM credentials WHERE service_id=?', (service_id,))

            # 删除元数据
            cursor.execute('DELETE FROM service_metadata WHERE service_id=?', (service_id,))

            # 删除服务
            cursor.execute('DELETE FROM services WHERE id=?', (service_id,))

            conn.commit()
            print(f"✅ 服务 '{service_name}' 已删除")
            return True

        except Exception as e:
            print(f"❌ 删除服务失败: {e}")
            return False

        finally:
            conn.close()


def main():
    """命令行工具主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='密码数据库管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 添加服务
    parser_add = subparsers.add_parser('add-service', help='添加服务')
    parser_add.add_argument('service_name', help='服务名称')
    parser_add.add_argument('--type', dest='service_type', default='', help='服务类型')
    parser_add.add_argument('--url', dest='base_url', default='', help='服务地址')
    parser_add.add_argument('--description', default='', help='服务描述')

    # 添加凭证
    parser_cred = subparsers.add_parser('add-credential', help='添加凭证')
    parser_cred.add_argument('service_name', help='服务名称')
    parser_cred.add_argument('--type', dest='credential_type', required=True, help='凭证类型')
    parser_cred.add_argument('--key', dest='key_name', required=True, help='键名')
    parser_cred.add_argument('--value', required=True, help='值')

    # 获取凭证
    parser_get = subparsers.add_parser('get-credentials', help='获取凭证')
    parser_get.add_argument('service_name', help='服务名称')

    # 获取服务
    parser_service = subparsers.add_parser('get-service', help='获取服务信息')
    parser_service.add_argument('service_name', help='服务名称')

    # 列出服务
    parser_list = subparsers.add_parser('list-services', help='列出所有服务')

    # 删除服务
    parser_del = subparsers.add_parser('delete-service', help='删除服务')
    parser_del.add_argument('service_name', help='服务名称')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 初始化管理器
    manager = CredentialsManager()

    # 执行命令
    if args.command == 'add-service':
        manager.add_service(
            service_name=args.service_name,
            service_type=args.service_type,
            description=args.description,
            base_url=args.base_url
        )

    elif args.command == 'add-credential':
        manager.add_credential(
            service_name=args.service_name,
            credential_type=args.credential_type,
            key_name=args.key_name,
            value=args.value
        )

    elif args.command == 'get-credentials':
        credentials = manager.get_credentials(args.service_name)
        if credentials:
            print("\n凭证信息：")
            for key, value in credentials.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ 服务 '{args.service_name}' 不存在或没有凭证")

    elif args.command == 'get-service':
        service = manager.get_service(args.service_name)
        if service:
            print(f"\n服务信息：")
            print(f"  名称: {service['service_name']}")
            print(f"  类型: {service['service_type']}")
            print(f"  地址: {service['base_url']}")
            print(f"  描述: {service['description']}")
            if service.get('credentials'):
                print(f"\n凭证：")
                for cred_type, creds in service['credentials'].items():
                    print(f"  {cred_type}:")
                    for key, value in creds.items():
                        print(f"    {key}: {value}")
        else:
            print(f"❌ 服务 '{args.service_name}' 不存在")

    elif args.command == 'list-services':
        services = manager.list_services()
        if services:
            print("\n所有服务：")
            for service in services:
                print(f"  - {service['service_name']} ({service['service_type']})")
                if service['base_url']:
                    print(f"    地址: {service['base_url']}")
        else:
            print("没有服务")

    elif args.command == 'delete-service':
        confirm = input(f"确定要删除服务 '{args.service_name}' 吗？(y/n): ")
        if confirm.lower() == 'y':
            manager.delete_service(args.service_name)
        else:
            print("已取消")


if __name__ == "__main__":
    main()
