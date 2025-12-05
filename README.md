# 🤖 AI数字人队伍管理系统

一个基于大语言模型的智能软件开发团队管理系统，通过AI数字人角色协作，实现自动化任务分配、代码生成、项目管理和知识沉淀。

## ✨ 核心特性

- 🤖 **AI数字人团队** - 项目经理、架构师、前端/后端工程师、运维工程师等角色
- 💻 **代码自动生成** - 基于Ollama + deepseek-coder模型，支持多种编程语言
- 📋 **任务管理系统** - 任务创建、分配、跟踪、优先级管理、依赖关系
- 🔄 **工作流引擎** - 可定义、执行、暂停/恢复的复杂工作流
- 📊 **可视化监控** - 实时任务状态、依赖关系可视化、统计报表
- 📚 **知识库集成** - 集成RAGFlow知识库，支持知识检索和自动沉淀
- 🌐 **Web管理界面** - 统一的Web管理平台，实时状态更新

## 🏗️ 系统架构

```
Web管理界面 (Flask)
    ↓
任务调度器 (TaskScheduler)
    ↓
数字人队伍 (DigitalHumans)
    ├── 项目经理 (ProjectManager)
    ├── 系统架构师 (SystemArchitect)
    ├── 前端工程师 (FrontendEngineer)
    ├── 后端工程师 (BackendEngineer)
    └── 运维工程师 (DevOpsEngineer)
    ↓
AI引擎 (Ollama + deepseek-coder:6.7b)
    ↓
知识库 (RAGFlow)
```

## 🚀 快速开始（3步即可试用）

### 前置要求

- Python 3.9+
- Ollama (可选，用于AI功能)
- 16GB RAM (推荐)

### 第一步：安装依赖

```bash
# 进入Web界面目录
cd "03-技术实现/02-功能模块/web_interface"

# 安装Web界面依赖
pip3 install -r requirements.txt

# 安装密码数据库依赖
pip3 install cryptography
```

### 第二步：启动Web服务

```bash
# 在web_interface目录下
./start.sh

# 或者
python3 app.py
```

**访问地址**：`http://localhost:5001`

### 第三步：体验功能

1. **浏览Web界面** - 数字人管理、任务创建、工作流管理
2. **使用密码数据库**（可选）- 管理服务凭证
3. **查看项目进度** - 进度跟踪工具

---

## 🎯 新增功能

### 密码数据库系统 ✅

集中管理所有服务的账号密码，支持自动收集和调用：

```bash
cd "03-技术实现/05-配置管理"
python credentials_manager.py add-service RAGFlow --type 知识库 --url https://ragflow.suuntoyun.com
```

详细使用：查看 `03-技术实现/05-配置管理/密码数据库使用指南.md`

---

## 📖 详细文档

- **快速开始指南**：`快速开始指南.md`
- **开始试用**：`开始试用.md`
- **用户操作手册**：`03-技术实现/02-功能模块/web_interface/用户操作手册.md`

## 📖 使用文档

- [用户操作手册](03-技术实现/02-功能模块/web_interface/用户操作手册.md)
- [Cursor配合使用指南](03-技术实现/02-功能模块/web_interface/Cursor配合使用指南.md)
- [系统技术说明](03-技术实现/02-功能模块/web_interface/系统技术说明.md)

## 🎯 功能模块

### 数字人角色

- **项目经理** - 项目计划、进度跟踪、风险识别
- **系统架构师** - 架构设计、技术选型、规范制定
- **前端工程师** - UI实现、性能优化、Bug修复
- **后端工程师** - API开发、数据库优化、业务逻辑
- **运维工程师** - 系统监控、部署脚本、自动化运维

### 核心功能

- ✅ 任务创建和分配
- ✅ 工作流定义和执行
- ✅ 代码自动生成
- ✅ 知识库检索和沉淀
- ✅ 实时状态监控
- ✅ 任务依赖管理
- ✅ 批量操作
- ✅ 数据导出

## 🔧 技术栈

- **后端**: Python 3.9+, Flask
- **AI引擎**: Ollama + deepseek-coder:6.7b
- **知识库**: RAGFlow (可选)
- **前端**: HTML/CSS/JavaScript
- **实时通信**: Flask-SocketIO
- **数据库**: SQLite

## 📋 项目结构

```
.
├── 01-项目构想/          # 项目规划和设计文档
├── 02-数字人设计/        # 数字人角色定义
├── 03-技术实现/          # 核心代码实现
│   └── 02-功能模块/
│       ├── digital_humans/    # 数字人实现
│       ├── workflow/          # 工作流引擎
│       ├── knowledge/        # 知识库集成
│       └── web_interface/     # Web管理界面
├── 04-知识库建设/        # 知识库相关文档
└── README.md            # 本文件
```

## 🔐 安全注意事项

⚠️ **重要**: 本项目使用环境变量管理敏感信息，请勿将以下内容提交到Git：

- `.env` 文件
- API密钥
- 数据库文件
- 日志文件

请参考 `.gitignore` 文件确保敏感信息不会被提交。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Ollama](https://ollama.ai/) - 本地大模型部署
- [deepseek-coder](https://github.com/deepseek-ai/deepseek-coder) - 代码生成模型
- [RAGFlow](https://github.com/infiniflow/ragflow) - 知识库平台
- [Flask](https://flask.palletsprojects.com/) - Web框架

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**⭐ 如果这个项目对你有帮助，请给个Star！**
