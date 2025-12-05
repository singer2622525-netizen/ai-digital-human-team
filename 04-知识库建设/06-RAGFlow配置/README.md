# RAGFlow知识库集成

## 📋 概述

本项目已迁移到使用公司Dell服务器上的RAGFlow服务作为统一知识库平台，替代本地ChromaDB存储。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests python-dotenv
```

### 2. 配置环境变量

在 `~/DeveloperConfig/环境变量/.env.work` 中添加：

```bash
RAGFLOW_BASE_URL=http://your-server-ip:port
RAGFLOW_API_KEY=your-api-key-if-needed
RAGFLOW_KB_ID=your-knowledge-base-id
```

### 3. 测试连接

```bash
python3 test_ragflow_connection.py
```

### 4. 使用交互式界面

```bash
python3 discussion_helper_ragflow.py
```

## 📁 文件说明

- `ragflow_client.py` - RAGFlow API客户端封装
- `discussion_helper_ragflow.py` - 交互式讨论记录工具
- `test_ragflow_connection.py` - 连接测试脚本
- `RAGFlow配置指南.md` - 详细配置文档

## 🔧 API使用示例

```python
from ragflow_client import DiscussionRecorderRAGFlow

# 初始化（使用环境变量）
recorder = DiscussionRecorderRAGFlow()

# 添加讨论
recorder.add_discussion(
    topic="测试主题",
    content="测试内容",
    category="其他"
)

# 搜索
results = recorder.search_discussions("测试", n_results=5)
```

## 📚 相关文档

- [RAGFlow配置指南](./RAGFlow配置指南.md)
- [环境变量管理指南](../../03-技术实现/05-配置管理/环境变量管理指南.md)

