# 数字人管理网页端

## 快速启动

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动应用**
   ```bash
   python app.py
   ```

3. **访问应用**
   - 仪表盘：http://localhost:5001
   - 角色管理：http://localhost:5001/roles
   - API接口：
     - http://localhost:5001/api/departments
     - http://localhost:5001/api/roles

## 功能说明

- **仪表盘**：展示各部门数字人角色分布图表
- **角色管理**：查看所有数字人角色列表
- **RESTful API**：提供数据接口供前端调用

## 下一步开发

- [ ] 添加任务管理功能
- [ ] 实现数字人状态监控
- [ ] 集成Ollama API
- [ ] 连接RAGFlow知识库


