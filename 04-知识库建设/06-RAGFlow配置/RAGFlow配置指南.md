# RAGFlow知识库配置指南

## 📋 概述

本项目使用公司Dell服务器上的RAGFlow服务作为统一的知识库平台，替代本地ChromaDB存储。这样可以实现：
- ✅ 跨设备访问（公司Mac、家里Mac都可以访问）
- ✅ 统一数据管理（所有数据集中在服务器）
- ✅ 更好的协作支持（未来可以多人共享）

## 🏗️ 架构设计

```
公司Dell服务器 (RAGFlow服务)
    ↑
    ├── 公司Mac (Cursor) ──┐
    │                      │
    └── 家里Mac (Cursor) ──┘
        通过API访问RAGFlow知识库
```

## 🔧 配置步骤

### 1. 在RAGFlow中创建知识库

登录RAGFlow Web界面（通常是 `http://your-server-ip:port`），创建知识库：

**知识库名称**: `软件工程事业部-数字人队伍`

**知识库描述**: `存储软件工程事业部数字人队伍的所有讨论记录、项目经验、最佳实践等知识`

**知识库分类**: 根据您现有的分类体系选择（如果没有，可以创建新分类）

**记录知识库ID**: 创建后会生成一个知识库ID，需要记录下来用于配置

### 2. 配置环境变量

在您的环境变量配置文件中（`~/DeveloperConfig/环境变量/.env.work`）添加：

```bash
# RAGFlow配置
RAGFLOW_BASE_URL=http://your-server-ip:port
RAGFLOW_API_KEY=your-api-key-if-needed
RAGFLOW_KB_ID=your-knowledge-base-id
```

**参数说明**:
- `RAGFLOW_BASE_URL`: RAGFlow服务的完整URL，例如 `http://192.168.1.100:9380`
- `RAGFLOW_API_KEY`: API密钥（如果RAGFlow启用了API认证）
- `RAGFLOW_KB_ID`: 步骤1中创建的知识库ID

### 3. 测试连接

运行测试脚本验证配置：

```bash
cd "04-知识库建设/06-RAGFlow配置"
python3 test_ragflow_connection.py
```

### 4. 迁移现有数据（可选）

如果您之前在ChromaDB中有数据，可以运行迁移脚本：

```bash
python3 migrate_chromadb_to_ragflow.py
```

## 📚 知识库分类体系

建议在RAGFlow中创建以下分类（或使用标签/metadata）：

1. **组织架构** - 关于整体架构、中心设置等
2. **岗位配置** - 关于岗位职责、人员配置等
3. **流程设计** - 关于工作流程、协作机制等
4. **数字人实现** - 关于如何用数字人实现岗位
5. **人工治理** - 关于人工介入点、治理强度等
6. **项目经验** - 项目过程记录、成功案例、失败教训
7. **技术知识** - 技术选型、架构设计、代码实现
8. **其他** - 其他讨论

## 🔌 API使用示例

### Python代码示例

```python
from ragflow_client import RAGFlowClient, DiscussionRecorderRAGFlow

# 方式1: 使用环境变量
recorder = DiscussionRecorderRAGFlow()

# 方式2: 直接指定参数
client = RAGFlowClient(
    base_url="http://your-server-ip:port",
    api_key="your-api-key",
    knowledge_base_id="your-kb-id"
)
recorder = DiscussionRecorderRAGFlow(ragflow_client=client)

# 添加讨论记录
doc_id = recorder.add_discussion(
    topic="组织架构设计",
    content="讨论了6个中心的设置...",
    category="组织架构",
    decision="决定采用6个中心的架构",
    tags=["架构", "决策"]
)

# 搜索讨论记录
results = recorder.search_discussions(
    query="PMO职责",
    category="组织架构",
    n_results=5
)

# 获取所有讨论
all_discussions = recorder.get_all_discussions(category="组织架构")

# 获取统计信息
stats = recorder.get_statistics()
```

## 🔐 安全注意事项

1. **API密钥管理**
   - 不要将API密钥提交到Git仓库
   - 使用环境变量管理敏感信息
   - 定期轮换API密钥

2. **网络访问**
   - 确保RAGFlow服务只在内网可访问（或使用VPN）
   - 如果需要在公网访问，使用HTTPS和强认证

3. **数据备份**
   - 定期备份RAGFlow知识库数据
   - 重要数据建议额外备份

## 🚀 使用场景

### 场景1: 在公司Mac上添加讨论记录

```bash
cd "04-知识库建设/06-RAGFlow配置"
python3 discussion_helper_ragflow.py
# 选择"添加讨论记录"
```

### 场景2: 在家里Mac上搜索历史讨论

```bash
# 确保已配置环境变量（VPN连接公司网络）
python3 discussion_helper_ragflow.py
# 选择"搜索讨论记录"
```

### 场景3: 在Cursor中使用

在Cursor的AI对话中，可以引用知识库内容：

```
@知识库 查询关于PMO职责的讨论
```

## 📝 与ChromaDB的对比

| 特性 | ChromaDB (旧方案) | RAGFlow (新方案) |
|------|------------------|------------------|
| 部署位置 | 本地Mac | 公司Dell服务器 |
| 跨设备访问 | ❌ | ✅ |
| Web界面 | ❌ | ✅ |
| 文档解析 | ❌ | ✅ (支持多种格式) |
| 协作支持 | ❌ | ✅ |
| 数据集中管理 | ❌ | ✅ |

## 🔄 迁移计划

1. **阶段1**: 配置RAGFlow连接（当前阶段）
2. **阶段2**: 迁移现有ChromaDB数据（如果有）
3. **阶段3**: 更新所有工具使用RAGFlow API
4. **阶段4**: 停用本地ChromaDB（可选）

## ❓ 常见问题

### Q: RAGFlow API文档在哪里？
A: RAGFlow通常提供Swagger文档，访问 `http://your-server-ip:port/docs` 或 `http://your-server-ip:port/api/docs`

### Q: 如何获取知识库ID？
A: 在RAGFlow Web界面中，进入知识库详情页，URL或页面中会显示知识库ID

### Q: 如果RAGFlow服务不可用怎么办？
A: 可以保留ChromaDB作为备用方案，或实现自动降级机制

### Q: 如何确保数据安全？
A: 
- 使用内网访问
- 启用API认证
- 定期备份数据
- 使用HTTPS（如果公网访问）

## 📞 技术支持

如果遇到问题，请检查：
1. RAGFlow服务是否正常运行
2. 网络连接是否正常
3. 环境变量配置是否正确
4. API密钥是否有效
5. 知识库ID是否正确

