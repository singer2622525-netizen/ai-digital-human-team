#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow API客户端封装
用于访问公司Dell服务器上的RAGFlow服务
"""

import requests
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json

# 添加项目根目录到路径，以便导入密码管理模块
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from credentials_auto import auto_get_credentials, get_auto_manager
    AUTO_CREDENTIALS_AVAILABLE = True
except ImportError:
    AUTO_CREDENTIALS_AVAILABLE = False


class RAGFlowClient:
    """RAGFlow API客户端"""

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 knowledge_base_id: Optional[str] = None):
        """
        初始化RAGFlow客户端

        Args:
            base_url: RAGFlow服务地址，例如 http://your-server-ip:port
            api_key: API密钥（如果需要）
            username: 登录用户名（如果需要登录认证）
            password: 登录密码（如果需要登录认证）
            knowledge_base_id: 知识库ID（软件工程事业部数字人队伍知识库）
        """
        # 从环境变量读取配置
        self.base_url = base_url or os.getenv('RAGFLOW_BASE_URL', '')
        self.api_key = api_key or os.getenv('RAGFLOW_API_KEY', '')
        self.username = username or os.getenv('RAGFLOW_USERNAME', '')
        self.password = password or os.getenv('RAGFLOW_PASSWORD', '')
        self.knowledge_base_id = knowledge_base_id or os.getenv('RAGFLOW_KB_ID', '')

        # 如果未提供凭证，尝试从密码库自动获取
        if AUTO_CREDENTIALS_AVAILABLE and (not self.username or not self.password):
            try:
                auto_manager = get_auto_manager()
                credentials = auto_manager.auto_get_credentials(
                    service_name="RAGFlow",
                    context=f"初始化RAGFlow客户端，base_url={self.base_url}",
                    auto_set_env=True
                )

                if credentials:
                    if not self.username:
                        self.username = credentials.get('username', '')
                    if not self.password:
                        self.password = credentials.get('password', '')
                    if not self.base_url:
                        service_config = auto_manager.api.get_service_config("RAGFlow")
                        if service_config and service_config.get('base_url'):
                            self.base_url = service_config['base_url']

                    print("✅ 已从密码库自动获取RAGFlow凭证")
            except Exception as e:
                print(f"⚠️  从密码库获取凭证失败: {e}")

        if not self.base_url:
            raise ValueError("请设置RAGFLOW_BASE_URL环境变量或传入base_url参数")

        # 确保URL不以/结尾（API端点会自己添加/）
        if self.base_url.endswith('/'):
            self.base_url = self.base_url.rstrip('/')

        # 设置请求头
        self.headers = {
            'Content-Type': 'application/json'
        }

        # 优先使用API密钥
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

        # Session用于保持登录状态
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 如果提供了用户名和密码，尝试登录
        if self.username and self.password:
            self._login()

    def _login(self) -> bool:
        """
        登录RAGFlow获取Session Token

        Returns:
            是否登录成功
        """
        if not self.username or not self.password:
            return False

        try:
            # RAGFlow登录端点（根据实际API调整）
            login_url = f"{self.base_url}/api/v1/user/login"
            login_data = {
                "username": self.username,
                "password": self.password
            }

            response = requests.post(login_url, json=login_data)
            response.raise_for_status()
            result = response.json()

            # 获取Token（根据RAGFlow实际返回格式调整）
            self.session_token = result.get('token') or result.get('access_token') or result.get('data', {}).get('token')

            if self.session_token:
                # 更新请求头，使用Session Token
                self.headers['Authorization'] = f'Bearer {self.session_token}'
                print(f"✅ RAGFlow登录成功")
                return True
            else:
                print(f"⚠️  登录成功但未获取到Token，可能需要使用Cookie")
                # 尝试使用Cookie
                if 'set-cookie' in response.headers:
                    cookie = response.headers['set-cookie']
                    self.headers['Cookie'] = cookie
                    return True
                return False

        except Exception as e:
            print(f"⚠️  RAGFlow登录失败：{e}")
            print(f"   提示：如果RAGFlow使用Cookie认证，可能需要手动登录后获取Cookie")
            return False

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        发送HTTP请求

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            **kwargs: 其他请求参数

        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)

            # 如果返回401未授权，尝试重新登录
            if response.status_code == 401 and self.username and self.password:
                print("⚠️  认证失败，尝试重新登录...")
                if self._login():
                    # 重新发送请求
                    response = requests.request(method, url, headers=self.headers, **kwargs)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ RAGFlow API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"错误详情: {e.response.text}")
            raise

    def create_knowledge_base(self, name: str, description: str = "") -> Dict:
        """
        创建知识库

        Args:
            name: 知识库名称
            description: 知识库描述

        Returns:
            知识库信息
        """
        data = {
            "name": name,
            "description": description
        }
        return self._request('POST', 'api/v1/kb', json=data)

    def list_knowledge_bases(self) -> List[Dict]:
        """
        列出所有知识库

        Returns:
            知识库列表
        """
        result = self._request('GET', 'api/v1/kb')
        return result.get('data', [])

    def get_knowledge_base(self, kb_id: str) -> Dict:
        """
        获取知识库信息

        Args:
            kb_id: 知识库ID

        Returns:
            知识库信息
        """
        return self._request('GET', f'api/v1/kb/{kb_id}')

    def upload_document(self,
                       kb_id: str,
                       file_path: Optional[str] = None,
                       content: Optional[str] = None,
                       filename: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> Dict:
        """
        上传文档到知识库

        Args:
            kb_id: 知识库ID
            file_path: 文件路径（如果上传文件）
            content: 文档内容（如果直接上传文本）
            filename: 文件名
            metadata: 元数据

        Returns:
            上传结果
        """
        if file_path:
            # 上传文件
            with open(file_path, 'rb') as f:
                files = {'file': (filename or os.path.basename(file_path), f)}
                data = {'kb_id': kb_id}
                if metadata:
                    data['metadata'] = json.dumps(metadata)

                url = f"{self.base_url}/api/v1/document/upload"
                response = self.session.post(url, files=files, data=data)
                response.raise_for_status()
                return response.json()
        elif content:
            # 上传文本内容
            data = {
                "kb_id": kb_id,
                "content": content,
                "filename": filename or f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            }
            if metadata:
                data['metadata'] = metadata

            return self._request('POST', 'api/v1/document/text', json=data)
        else:
            raise ValueError("必须提供file_path或content参数")

    def search(self,
              kb_id: str,
              query: str,
              top_k: int = 5,
              filters: Optional[Dict] = None) -> List[Dict]:
        """
        在知识库中搜索

        Args:
            kb_id: 知识库ID
            query: 搜索查询
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            搜索结果列表
        """
        data = {
            "kb_id": kb_id,
            "question": query,
            "top_k": top_k
        }
        if filters:
            data['filters'] = filters

        result = self._request('POST', 'api/v1/retrieval', json=data)
        return result.get('data', [])

    def list_documents(self, kb_id: str) -> List[Dict]:
        """
        列出知识库中的所有文档

        Args:
            kb_id: 知识库ID

        Returns:
            文档列表
        """
        result = self._request('GET', f'api/v1/document/list', params={'kb_id': kb_id})
        return result.get('data', [])


class DiscussionRecorderRAGFlow:
    """使用RAGFlow的讨论记录管理器"""

    def __init__(self,
                 ragflow_client: Optional[RAGFlowClient] = None,
                 knowledge_base_id: Optional[str] = None):
        """
        初始化讨论记录器

        Args:
            ragflow_client: RAGFlow客户端实例
            knowledge_base_id: 知识库ID（如果为None，会尝试从环境变量读取）
        """
        self.client = ragflow_client or RAGFlowClient()
        self.kb_id = knowledge_base_id or self.client.knowledge_base_id

        if not self.kb_id:
            raise ValueError("请设置知识库ID（通过参数或RAGFLOW_KB_ID环境变量）")

    def add_discussion(self,
                      topic: str,
                      content: str,
                      category: str = "general",
                      decision: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> str:
        """
        添加讨论记录

        Args:
            topic: 讨论主题
            content: 讨论内容
            category: 分类（如：组织架构、岗位配置、流程设计等）
            decision: 决策结果（如果有）
            tags: 标签列表

        Returns:
            文档ID
        """
        # 构建完整文档内容
        full_content = f"主题：{topic}\n\n内容：{content}"
        if decision:
            full_content += f"\n\n决策：{decision}"

        # 构建元数据
        metadata = {
            "topic": topic,
            "category": category,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "has_decision": "true" if decision else "false"
        }
        if tags:
            metadata["tags"] = ",".join(tags)

        # 生成文件名
        filename = f"discussion_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # 上传到RAGFlow
        result = self.client.upload_document(
            kb_id=self.kb_id,
            content=full_content,
            filename=filename,
            metadata=metadata
        )

        doc_id = result.get('id') or result.get('doc_id', '')
        print(f"✅ 讨论记录已添加到RAGFlow：{topic}")
        return doc_id

    def search_discussions(self,
                          query: str,
                          category: Optional[str] = None,
                          n_results: int = 5) -> List[Dict]:
        """
        搜索讨论记录

        Args:
            query: 搜索查询
            category: 分类筛选（可选）
            n_results: 返回结果数量

        Returns:
            讨论记录列表
        """
        # 构建过滤条件
        filters = {}
        if category:
            filters['category'] = category

        # 搜索
        results = self.client.search(
            kb_id=self.kb_id,
            query=query,
            top_k=n_results,
            filters=filters if filters else None
        )

        # 格式化结果
        discussions = []
        for result in results:
            discussions.append({
                "id": result.get('id', ''),
                "content": result.get('content', ''),
                "metadata": result.get('metadata', {}),
                "score": result.get('score', 0.0)
            })

        return discussions

    def get_all_discussions(self, category: Optional[str] = None) -> List[Dict]:
        """
        获取所有讨论记录

        Args:
            category: 分类筛选（可选）

        Returns:
            讨论记录列表
        """
        documents = self.client.list_documents(self.kb_id)

        discussions = []
        for doc in documents:
            metadata = doc.get('metadata', {})

            # 如果指定了分类，进行筛选
            if category and metadata.get('category') != category:
                continue

            discussions.append({
                "id": doc.get('id', ''),
                "content": doc.get('content', ''),
                "metadata": metadata
            })

        # 按时间倒序排列
        discussions.sort(
            key=lambda x: x['metadata'].get('timestamp', ''),
            reverse=True
        )

        return discussions

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        documents = self.client.list_documents(self.kb_id)

        total = len(documents)
        categories = {}
        decisions = 0

        for doc in documents:
            metadata = doc.get('metadata', {})

            # 统计分类
            cat = metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1

            # 统计决策数量
            if metadata.get('has_decision') == 'true':
                decisions += 1

        return {
            "total_discussions": total,
            "total_decisions": decisions,
            "categories": categories
        }

    def display_discussion(self, discussion: Dict):
        """
        格式化显示讨论记录

        Args:
            discussion: 讨论记录字典
        """
        metadata = discussion.get('metadata', {})
        content = discussion.get('content', '')

        print("\n" + "="*60)
        print(f"📋 主题：{metadata.get('topic', '未知')}")
        print(f"📁 分类：{metadata.get('category', '未知')}")
        print(f"🕐 时间：{metadata.get('timestamp', '未知')}")
        if metadata.get('has_decision') == 'true':
            print("✅ 已决策")
        if metadata.get('tags'):
            print(f"🏷️  标签：{metadata.get('tags')}")
        if discussion.get('score'):
            print(f"📊 相似度：{discussion['score']:.2%}")
        print("-"*60)
        print(content)
        print("="*60)


if __name__ == "__main__":
    # 测试代码
    print("RAGFlow客户端封装")
    print("请设置环境变量：")
    print("  RAGFLOW_BASE_URL - RAGFlow服务地址")
    print("  RAGFLOW_API_KEY - API密钥（如果需要）")
    print("  RAGFLOW_KB_ID - 知识库ID")
