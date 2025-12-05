# RAGFlow 服务器信息

## 📋 服务器连接信息

### 访问地址
- **Web界面**：`https://ragflow.suuntoyun.com`
- **公网IP**：`119.130.140.184:9380`
- **内网IP**：`192.168.13.33:9380`（仅内网访问）

### SSH连接信息
- **公网IP**：`119.130.140.184`
- **SSH端口**：`2222`
- **用户名**：`singer2622525`
- **SSH配置别名**：`ragflow-server`

### 快速连接命令
```bash
# SSH连接
ssh ragflow-server

# 或者直接连接
ssh -p 2222 singer2622525@119.130.140.184
```

---

## 🔧 API配置

### 环境变量配置
```bash
# 在 ~/DeveloperConfig/环境变量/.env.work 中添加：

# RAGFlow配置
RAGFLOW_BASE_URL=https://ragflow.suuntoyun.com
# 如果域名不可用，使用公网IP
# RAGFLOW_BASE_URL=http://119.130.140.184:9380

# 登录认证（推荐使用用户名密码）
RAGFLOW_USERNAME=your-username
RAGFLOW_PASSWORD=your-password

# API密钥（如果需要，通常不需要）
RAGFLOW_API_KEY=

# API版本
RAGFLOW_API_VERSION=v1
```

### API端点
- **基础URL**：`https://ragflow.suuntoyun.com/api/v1`
- **知识库列表**：`GET /api/v1/kb`
- **创建知识库**：`POST /api/v1/kb`
- **上传文档**：`POST /api/v1/document/upload`
- **文档检索**：`POST /api/v1/retrieval`

---

## 📚 知识库信息

### 已部署的8个知识库
1. **organization_knowledge** - 组织架构知识库
2. **project_experience** - 项目经验知识库
3. **technical_knowledge** - 技术知识库
4. **business_knowledge** - 业务知识库
5. **digital_human_knowledge** - 数字人知识库
6. **error_knowledge** - 错误知识库
7. **best_practices** - 最佳实践知识库
8. **company_development** - 公司发展知识库

---

## 🔍 模型配置状态

### 已配置 ✅
- **Embedding模型**：TEI (`http://tei:80`)
- **文档解析**：DeepDOC
- **向量检索**：可用

### 需要配置 ⚠️
- **LLM模型**：未配置（文档检索不需要LLM）
- **问答功能**：需要LLM才能使用

---

## 🧪 测试连接

### 方式1：Web界面测试
1. 访问：`https://ragflow.suuntoyun.com`
2. 登录账号
3. 检查知识库列表

### 方式2：API测试
```bash
cd "04-知识库建设/06-RAGFlow配置"
python3 test_ragflow_connection.py
```

### 方式3：SSH连接测试
```bash
ssh ragflow-server
# 检查RAGFlow服务状态
sudo systemctl status ragflow
```

---

## 📝 重要提示

1. **API认证**：
   - RAGFlow可能不需要API密钥（取决于配置）
   - 如果API调用失败，检查是否需要登录认证

2. **网络访问**：
   - 优先使用域名：`https://ragflow.suuntoyun.com`
   - 如果域名不可用，使用公网IP：`http://119.130.140.184:9380`

3. **API端点**：
   - RAGFlow的API端点可能因版本而异
   - 如果API调用失败，检查RAGFlow的API文档

---

## 🔗 相关文档

- **部署指南**：`/Users/a1/Documents/Projects/cursor/00公司知识库ragflow/完整部署指南.md`
- **测试说明**：`/Users/a1/Documents/Projects/cursor/00公司知识库ragflow/RAGFlow知识库测试功能说明.md`
- **知识库规划**：`知识库规划.md`
- **操作指南**：`知识库建设操作指南.md`

---

*最后更新：2024年*
