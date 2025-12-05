from flask import Flask, render_template, jsonify, request
from functools import wraps
from datetime import datetime
import sys
import os
import time
import logging

# 导入SocketIO
try:
    from socketio_handler import init_socketio, emit_task_update, emit_workflow_update, emit_statistics_update, register_socketio_handlers
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    register_socketio_handlers = None
    logging.warning("Flask-SocketIO未安装，WebSocket功能将不可用")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加数字人模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from digital_humans import (
    ProjectManager, SystemArchitect, FrontendEngineer,
    BackendEngineer, DevOpsEngineer, SmartProductPlanner,
    RealTimeRecorder, QualityObserver, KnowledgeAdministrator
)

# 导入工作流模块
from workflow import TaskManager, TaskScheduler, WorkflowEngine, TaskPriority
from workflow.workflow_templates import register_all_templates

# 导入同步管理模块
try:
    from sync_manager import SyncManager
    SYNC_MANAGER_AVAILABLE = True
except ImportError:
    SYNC_MANAGER_AVAILABLE = False
    logger.warning("同步管理模块未找到，同步功能将不可用")

app = Flask(__name__)

# 初始化SocketIO
if SOCKETIO_AVAILABLE:
    socketio = init_socketio(app)
    if register_socketio_handlers:
        register_socketio_handlers(socketio)
else:
    socketio = None

# API响应时间统计装饰器
def log_api_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"API {func.__name__} 耗时: {elapsed:.3f}秒")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"API {func.__name__} 错误 (耗时: {elapsed:.3f}秒): {e}")
            raise
    return wrapper

# 统一错误处理
def handle_error(error_msg: str, status_code: int = 400):
    """统一错误响应格式"""
    return jsonify({
        "success": False,
        "error": error_msg,
        "timestamp": time.time()
    }), status_code

# 初始化数字人实例
digital_humans = {
    "智能产品规划师": SmartProductPlanner(),  # 核心角色，项目的"灵魂"
    "项目经理": ProjectManager(),
    "系统架构师": SystemArchitect(),
    "前端工程师": FrontendEngineer(),
    "后端工程师": BackendEngineer(),
    "运维工程师": DevOpsEngineer(),
    "实时记录员": RealTimeRecorder(),
    "质量观察员": QualityObserver(),
    "知识管理员": KnowledgeAdministrator()
}

# 初始化工作流系统
task_manager = TaskManager()
task_scheduler = TaskScheduler(task_manager)
workflow_engine = WorkflowEngine(task_manager)

# 注册工作流模板
register_all_templates(workflow_engine)

# 模拟数据
DEPARTMENTS = [
    {"id": 1, "name": "PMO", "roles": 6},
    {"id": 2, "name": "解决方案中心", "roles": 5},
    {"id": 3, "name": "研发中心", "roles": 5},
    {"id": 4, "name": "交付运营中心", "roles": 4},
    {"id": 5, "name": "业务支持中心", "roles": 4}
]

ROLES = [
    {"id": 1, "name": "智能产品规划师", "department": "解决方案中心", "is_core": True},
    {"id": 2, "name": "项目经理", "department": "PMO"},
    {"id": 3, "name": "系统架构师", "department": "解决方案中心"},
    {"id": 4, "name": "前端工程师", "department": "研发中心"},
    {"id": 5, "name": "后端工程师", "department": "研发中心"},
    {"id": 6, "name": "运维工程师", "department": "交付运营中心"},
    {"id": 7, "name": "实时记录员", "department": "业务支持中心"},
    {"id": 8, "name": "质量观察员", "department": "业务支持中心"},
    {"id": 9, "name": "知识管理员", "department": "PMO"}
]

@app.route('/')
def index():
    """统一的数字人队伍管理平台首页"""
    return render_template('index.html')

@app.route('/smart-planner')
def smart_planner():
    """智能产品规划师聊天界面"""
    return render_template('smart_planner.html')

@app.route('/api/smart-planner/chat', methods=['POST'])
@log_api_time
def smart_planner_chat():
    """智能产品规划师聊天API"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', [])

        if not message:
            return handle_error("消息内容不能为空", 400)

        # 获取智能产品规划师实例
        planner = digital_humans.get("智能产品规划师")
        if not planner:
            return handle_error("智能产品规划师未初始化", 500)

        # 构建对话提示
        system_prompt = planner.get_system_prompt()

        # 构建对话历史
        messages = [{"role": "system", "content": system_prompt}]
        for item in context[-5:]:  # 只保留最近5轮对话
            messages.append({"role": item.get('role', 'user'), "content": item.get('content', '')})
        messages.append({"role": "user", "content": message})

        # 使用ollama的chat方法
        response = planner.ollama.chat(messages)

        return jsonify({
            "success": True,
            "response": response,
            "timestamp": time.time()
        })

    except Exception as e:
        logger.error(f"智能产品规划师聊天错误: {e}")
        import traceback
        traceback.print_exc()
        return handle_error(f"处理请求时出错: {str(e)}", 500)

@app.route('/test-api')
def test_api():
    """API测试页面"""
    return render_template('test_api.html')

@app.route('/workflows/<workflow_id>')
def workflow_detail(workflow_id):
    """工作流详情页面"""
    # 即使工作流不存在也显示页面，让前端处理错误显示
    return render_template('workflow_detail.html', workflow_id=workflow_id)

@app.route('/dashboard')
def dashboard():
    """数字人管理仪表盘（旧版，保留兼容）"""
    return render_template('dashboard.html', departments=DEPARTMENTS)

@app.route('/roles')
def role_management():
    """角色管理界面"""
    return render_template('roles.html', roles=ROLES)

@app.route('/tasks')
def tasks():
    """任务管理页面"""
    return render_template('tasks.html')

@app.route('/visualization')
def visualization():
    """任务依赖可视化页面"""
    return render_template('visualization.html')

@app.route('/docs/user-manual')
def user_manual():
    """用户操作手册页面"""
    try:
        import markdown
        md_file = os.path.join(os.path.dirname(__file__), '用户操作手册.md')
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
        return render_template('doc_viewer.html',
                             title='用户操作手册',
                             content=html_content)
    except Exception as e:
        logger.error(f"加载用户操作手册失败: {e}")
        return f"<h1>文档加载失败</h1><p>{str(e)}</p>", 500

@app.route('/docs/cursor-guide')
def cursor_guide():
    """Cursor配合使用指南页面"""
    try:
        import markdown
        md_file = os.path.join(os.path.dirname(__file__), 'Cursor配合使用指南.md')
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
        return render_template('doc_viewer.html',
                             title='Cursor配合使用指南',
                             content=html_content)
    except Exception as e:
        logger.error(f"加载Cursor配合使用指南失败: {e}")
        return f"<h1>文档加载失败</h1><p>{str(e)}</p>", 500

@app.route('/docs/technical-spec')
def technical_spec():
    """系统技术说明页面"""
    try:
        import markdown
        md_file = os.path.join(os.path.dirname(__file__), '系统技术说明.md')
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
        return render_template('doc_viewer.html',
                             title='系统技术说明',
                             content=html_content)
    except Exception as e:
        logger.error(f"加载系统技术说明失败: {e}")
        return f"<h1>文档加载失败</h1><p>{str(e)}</p>", 500

# ==================== 数据同步API ====================

if SYNC_MANAGER_AVAILABLE:
    # 初始化同步管理器
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sync_manager = SyncManager(project_root)

    @app.route('/api/sync/status', methods=['GET'])
    def get_sync_status():
        """获取同步状态"""
        try:
            status = sync_manager.get_sync_status()
            return jsonify(status)
        except Exception as e:
            logger.error(f"获取同步状态失败: {e}")
            return handle_error(str(e), 500)

    @app.route('/api/sync/git/push', methods=['POST'])
    def sync_git_push():
        """同步代码到GitHub"""
        try:
            data = request.json or {}
            commit_message = data.get('message')
            result = sync_manager.sync_to_git(commit_message)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Git推送失败: {e}")
            return handle_error(str(e), 500)

    @app.route('/api/sync/git/pull', methods=['POST'])
    def sync_git_pull():
        """从GitHub拉取代码"""
        try:
            result = sync_manager.sync_from_git()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Git拉取失败: {e}")
            return handle_error(str(e), 500)

    @app.route('/api/sync/git/setup', methods=['POST'])
    def setup_git_remote():
        """设置Git远程仓库"""
        try:
            data = request.json
            remote_url = data.get('remote_url')
            if not remote_url:
                return handle_error("缺少remote_url参数", 400)
            result = sync_manager.setup_git_remote(remote_url)
            return jsonify(result)
        except Exception as e:
            logger.error(f"设置Git远程仓库失败: {e}")
            return handle_error(str(e), 500)

    @app.route('/api/sync/database', methods=['POST'])
    def sync_database():
        """同步数据库文件"""
        try:
            data = request.json
            storage_type = data.get('storage_type')
            storage_path = data.get('storage_path')
            if not storage_type or not storage_path:
                return handle_error("缺少storage_type或storage_path参数", 400)
            result = sync_manager.sync_database(storage_type, storage_path)
            return jsonify(result)
        except Exception as e:
            logger.error(f"数据库同步失败: {e}")
            return handle_error(str(e), 500)

@app.route('/api/departments')
def get_departments():
    """获取部门数据API"""
    return jsonify(DEPARTMENTS)

@app.route('/api/roles')
def get_roles():
    """获取角色数据API"""
    return jsonify(ROLES)

@app.route('/api/digital-humans')
def get_digital_humans():
    """获取所有数字人状态"""
    statuses = {}
    for role_name, human in digital_humans.items():
        statuses[role_name] = human.get_status()
    return jsonify(statuses)

@app.route('/api/digital-humans/<role_name>/execute', methods=['POST'])
def execute_task(role_name):
    """执行数字人任务"""
    if role_name not in digital_humans:
        return jsonify({"success": False, "error": "角色不存在"}), 404

    task = request.json
    human = digital_humans[role_name]
    result = human.execute_task(task)
    return jsonify(result)

@app.route('/test')
def test():
    """测试页面"""
    return "<h1>✅ Flask应用运行正常！</h1><p>如果您看到这条消息，说明应用已成功启动。</p><p><a href='/'>返回仪表盘</a></p>"

# ==================== 任务管理API ====================

@app.route('/api/tasks', methods=['GET'])
@log_api_time
def get_tasks():
    """获取所有任务"""
    status_filter = request.args.get('status')
    role_filter = request.args.get('role')

    if status_filter:
        from workflow import TaskStatus
        status = TaskStatus[status_filter.upper()]
        tasks = task_manager.get_tasks_by_status(status)
    elif role_filter:
        tasks = task_manager.get_tasks_by_role(role_filter)
    else:
        tasks = list(task_manager.tasks.values())

    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
@log_api_time
def create_task():
    """创建任务"""
    data = request.json

    priority_map = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
        "urgent": TaskPriority.URGENT
    }

    priority = priority_map.get(data.get('priority', 'medium').lower(), TaskPriority.MEDIUM)

    task = task_manager.create_task(
        task_type=data['task_type'],
        input_data=data['input_data'],
        priority=priority,
        dependencies=data.get('dependencies'),
        metadata=data.get('metadata', {})
    )

    # 自动分配
    task_scheduler.auto_assign_pending_tasks()

    # 发送实时更新
    if SOCKETIO_AVAILABLE:
        emit_task_update(task.to_dict(), "task_created")

    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取单个任务"""
    task = task_manager.get_task(task_id)
    if not task:
        return handle_error("任务不存在", 404)
    return jsonify(task.to_dict())

@app.route('/api/tasks/<task_id>/execute', methods=['POST'])
@log_api_time
def execute_task_api(task_id):
    """执行任务"""
    data = request.json or {}
    timeout = data.get('timeout')  # 可选超时参数

    result = task_scheduler.execute_task(task_id, timeout=timeout)

    # 添加执行时间信息
    if 'execution_time' not in result:
        result['execution_time'] = None

    # 发送实时更新
    if SOCKETIO_AVAILABLE:
        task = task_manager.get_task(task_id)
        if task:
            emit_task_update(task.to_dict(), "task_executed")
            emit_statistics_update(task_manager.get_statistics())

    return jsonify(result)

@app.route('/api/tasks/<task_id>/assign', methods=['POST'])
@log_api_time
def assign_task_api(task_id):
    """分配任务"""
    data = request.json
    if not data:
        return handle_error("请求体不能为空")

    role_name = data.get('role_name')
    if not role_name:
        return handle_error("缺少role_name参数")

    success = task_manager.assign_task(task_id, role_name)
    if success:
        task = task_manager.get_task(task_id)
        return jsonify(task.to_dict())
    else:
        return handle_error("分配失败（可能是依赖未完成或任务不存在）")

@app.route('/api/tasks/statistics', methods=['GET'])
@log_api_time
def get_task_statistics():
    """获取任务统计信息"""
    stats = task_manager.get_statistics()
    workload = task_scheduler.get_role_workload()
    stats['workload'] = workload

    # 添加系统健康信息
    stats['system_health'] = {
        "total_digital_humans": len(digital_humans),
        "active_tasks": stats['by_status'].get('in_progress', 0),
        "failed_tasks": stats['by_status'].get('failed', 0),
        "retry_tasks": stats.get('retry_count', 0)
    }

    return jsonify(stats)

# ==================== 工作流API ====================

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """获取所有工作流"""
    workflows = workflow_engine.get_all_workflows()
    return jsonify([wf.to_dict() for wf in workflows])

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """创建工作流"""
    data = request.json

    # 从模板创建
    if 'template' in data:
        workflow = workflow_engine.create_from_template(
            data['template'],
            name=data.get('name', ''),
            description=data.get('description', ''),
            metadata=data.get('metadata', {})
        )
        if not workflow:
            return jsonify({"error": "模板不存在"}), 404
    else:
        # 直接创建
        workflow = workflow_engine.create_workflow(
            name=data['name'],
            description=data.get('description', ''),
            metadata=data.get('metadata', {})
        )

    return jsonify(workflow.to_dict()), 201

@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """获取单个工作流"""
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        return jsonify({"error": "工作流不存在"}), 404
    return jsonify(workflow.to_dict())

@app.route('/api/workflows/<workflow_id>/start', methods=['POST'])
def start_workflow(workflow_id):
    """启动工作流"""
    success = workflow_engine.start_workflow(workflow_id)
    if success:
        workflow = workflow_engine.get_workflow(workflow_id)
        return jsonify(workflow.to_dict())
    else:
        return jsonify({"error": "启动失败"}), 400

@app.route('/api/workflows/<workflow_id>/update', methods=['POST'])
def update_workflow(workflow_id):
    """更新工作流状态"""
    workflow_engine.update_workflow(workflow_id)
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        return handle_error("工作流不存在", 404)
    return jsonify(workflow.to_dict())

@app.route('/api/workflows/<workflow_id>/pause', methods=['POST'])
@log_api_time
def pause_workflow(workflow_id):
    """暂停工作流"""
    from workflow.workflow_pause import WorkflowPauseManager

    pause_manager = WorkflowPauseManager(workflow_engine)
    data = request.json or {}
    reason = data.get('reason', '')

    success = pause_manager.pause_workflow(workflow_id, reason)
    if success:
        workflow = workflow_engine.get_workflow(workflow_id)
        return jsonify(workflow.to_dict())
    else:
        return handle_error("暂停失败（工作流不存在或不在运行状态）")

@app.route('/api/workflows/<workflow_id>/resume', methods=['POST'])
@log_api_time
def resume_workflow(workflow_id):
    """恢复工作流"""
    from workflow.workflow_pause import WorkflowPauseManager

    pause_manager = WorkflowPauseManager(workflow_engine)
    success = pause_manager.resume_workflow(workflow_id)
    if success:
        workflow = workflow_engine.get_workflow(workflow_id)
        return jsonify(workflow.to_dict())
    else:
        return handle_error("恢复失败（工作流不存在或不在暂停状态）")

@app.route('/api/workflows/paused', methods=['GET'])
@log_api_time
def get_paused_workflows():
    """获取所有暂停的工作流"""
    from workflow.workflow_pause import WorkflowPauseManager

    pause_manager = WorkflowPauseManager(workflow_engine)
    paused = pause_manager.get_paused_workflows()
    return jsonify({"paused_workflows": paused, "count": len(paused)})

@app.route('/api/workflows/templates', methods=['GET'])
@log_api_time
def get_workflow_templates():
    """获取工作流模板列表"""
    templates = list(workflow_engine.workflow_templates.keys())
    return jsonify({"templates": templates})

# ==================== 知识库API ====================

@app.route('/api/knowledge/search', methods=['POST'])
@log_api_time
def search_knowledge():
    """搜索知识库"""
    from knowledge import KnowledgeBase

    data = request.json
    if not data:
        return handle_error("请求体不能为空")

    query = data.get('query')
    if not query:
        return handle_error("缺少query参数")

    top_k = data.get('top_k', 5)

    kb = KnowledgeBase()
    results = kb.search(query, top_k=top_k)

    return jsonify({
        "success": True,
        "query": query,
        "results": results,
        "count": len(results)
    })

@app.route('/api/knowledge/add', methods=['POST'])
@log_api_time
def add_knowledge():
    """添加知识到知识库"""
    from knowledge import KnowledgeBase

    data = request.json
    if not data:
        return handle_error("请求体不能为空")

    content = data.get('content')
    if not content:
        return handle_error("缺少content参数")

    kb = KnowledgeBase()
    doc_id = kb.add_knowledge(
        content=content,
        title=data.get('title', ''),
        category=data.get('category', 'general'),
        metadata=data.get('metadata', {})
    )

    if doc_id:
        return jsonify({
            "success": True,
            "doc_id": doc_id
        }), 201
    else:
        return handle_error("添加知识失败（可能是RAGFlow未配置）")

# ==================== 批量操作API ====================

@app.route('/api/tasks/batch', methods=['POST'])
@log_api_time
def batch_create_tasks():
    """批量创建任务"""
    from utils.batch_operations import BatchOperations

    data = request.json
    if not data:
        return handle_error("请求体不能为空")

    tasks_data = data.get('tasks', [])
    if not tasks_data:
        return handle_error("缺少tasks参数")

    batch_ops = BatchOperations(task_manager, task_scheduler)

    # 转换优先级
    priority_map = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
        "urgent": TaskPriority.URGENT
    }

    for task_data in tasks_data:
        if 'priority' in task_data and isinstance(task_data['priority'], str):
            task_data['priority'] = priority_map.get(task_data['priority'].lower(), TaskPriority.MEDIUM)

    task_ids = batch_ops.batch_create_tasks(tasks_data)

    return jsonify({
        "success": True,
        "created": len(task_ids),
        "task_ids": task_ids
    }), 201

@app.route('/api/tasks/batch/execute', methods=['POST'])
@log_api_time
def batch_execute_tasks():
    """批量执行任务"""
    from utils.batch_operations import BatchOperations

    data = request.json
    if not data:
        return handle_error("请求体不能为空")

    task_ids = data.get('task_ids', [])
    if not task_ids:
        return handle_error("缺少task_ids参数")

    batch_ops = BatchOperations(task_manager, task_scheduler)
    results = batch_ops.batch_execute_tasks(task_ids)

    return jsonify({
        "success": True,
        "results": results
    })

# ==================== 导出API ====================

@app.route('/api/export/tasks', methods=['GET'])
@log_api_time
def export_tasks():
    """导出任务"""
    from utils.batch_operations import BatchOperations
    import tempfile
    import os

    format_type = request.args.get('format', 'json')
    status_filter = request.args.get('status')
    role_filter = request.args.get('role')

    filters = {}
    if status_filter:
        filters['status'] = status_filter
    if role_filter:
        filters['role'] = role_filter

    batch_ops = BatchOperations(task_manager)

    # 创建临时文件
    suffix = '.json' if format_type == 'json' else '.csv'
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.close()

    success = batch_ops.export_tasks(temp_file.name, format_type, filters if filters else None)

    if success:
        from flask import send_file
        return send_file(temp_file.name, as_attachment=True,
                        download_name=f'tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}{suffix}')
    else:
        os.unlink(temp_file.name)
        return handle_error("导出失败")

@app.route('/api/export/report', methods=['GET'])
@log_api_time
def export_report():
    """导出性能报告"""
    from workflow.task_history import TaskHistoryManager
    from utils.export import Exporter
    import tempfile
    import os

    history_manager = TaskHistoryManager(task_manager)
    report = history_manager.get_performance_report()

    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
    temp_file.close()

    success = Exporter.export_report_to_markdown(report, temp_file.name)

    if success:
        from flask import send_file
        return send_file(temp_file.name, as_attachment=True,
                        download_name=f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
    else:
        os.unlink(temp_file.name)
        return handle_error("导出失败")

# ==================== 任务历史API ====================

@app.route('/api/tasks/history', methods=['GET'])
@log_api_time
def get_task_history():
    """获取任务历史"""
    from workflow.task_history import TaskHistoryManager
    from datetime import datetime

    history_manager = TaskHistoryManager(task_manager)

    # 获取查询参数
    task_id = request.args.get('task_id')
    role_name = request.args.get('role_name')
    task_type = request.args.get('task_type')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = int(request.args.get('limit', 100))

    # 解析日期
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
            pass

    # 解析状态
    task_status = None
    if status:
        from workflow.task_manager import TaskStatus
        try:
            task_status = TaskStatus[status.upper()]
        except:
            pass

    history = history_manager.get_task_history(
        task_id=task_id,
        role_name=role_name,
        task_type=task_type,
        status=task_status,
        start_date=start_dt,
        end_date=end_dt,
        limit=limit
    )

    return jsonify({
        "success": True,
        "count": len(history),
        "history": history
    })

@app.route('/api/tasks/history/recent', methods=['GET'])
@log_api_time
def get_recent_tasks():
    """获取最近的任务"""
    from workflow.task_history import TaskHistoryManager

    history_manager = TaskHistoryManager(task_manager)
    hours = int(request.args.get('hours', 24))
    limit = int(request.args.get('limit', 50))

    tasks = history_manager.get_recent_tasks(hours=hours, limit=limit)

    return jsonify({
        "success": True,
        "count": len(tasks),
        "tasks": tasks
    })

@app.route('/api/tasks/history/failed', methods=['GET'])
@log_api_time
def get_failed_tasks():
    """获取失败的任务"""
    from workflow.task_history import TaskHistoryManager

    history_manager = TaskHistoryManager(task_manager)
    limit = int(request.args.get('limit', 50))

    tasks = history_manager.get_failed_tasks(limit=limit)

    return jsonify({
        "success": True,
        "count": len(tasks),
        "tasks": tasks
    })

@app.route('/api/tasks/history/statistics', methods=['GET'])
@log_api_time
def get_task_statistics_history():
    """获取任务统计（按角色或任务类型）"""
    from workflow.task_history import TaskHistoryManager
    from datetime import datetime

    history_manager = TaskHistoryManager(task_manager)

    # 获取查询参数
    group_by = request.args.get('group_by', 'role')  # role 或 task_type
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 解析日期
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
            pass

    if group_by == 'role':
        stats = history_manager.get_statistics_by_role(start_dt, end_dt)
    elif group_by == 'task_type':
        stats = history_manager.get_statistics_by_task_type(start_dt, end_dt)
    else:
        return handle_error("group_by参数必须是'role'或'task_type'")

    return jsonify({
        "success": True,
        "group_by": group_by,
        "statistics": stats
    })

@app.route('/api/tasks/history/performance', methods=['GET'])
@log_api_time
def get_performance_report():
    """获取性能报告"""
    from workflow.task_history import TaskHistoryManager
    from datetime import datetime

    history_manager = TaskHistoryManager(task_manager)

    # 获取查询参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 解析日期
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
            pass

    report = history_manager.get_performance_report(start_dt, end_dt)

    return jsonify({
        "success": True,
        "report": report
    })

# ==================== 可视化API ====================

@app.route('/api/visualization/tasks/dependency', methods=['GET'])
@log_api_time
def get_task_dependency_graph():
    """获取任务依赖图"""
    from utils.visualization import TaskVisualizer

    # 获取所有任务
    tasks = [task.to_dict() for task in task_manager.tasks.values()]

    # 生成图数据
    graph_data = TaskVisualizer.generate_dependency_graph(tasks)

    return jsonify({
        "success": True,
        "graph": graph_data
    })

@app.route('/api/visualization/tasks/mermaid', methods=['GET'])
@log_api_time
def get_task_mermaid():
    """获取任务Mermaid图"""
    from utils.visualization import TaskVisualizer

    # 获取所有任务
    tasks = [task.to_dict() for task in task_manager.tasks.values()]
    logger.info(f"获取Mermaid图，任务数量: {len(tasks)}")

    # 生成Mermaid代码
    mermaid_code = TaskVisualizer.generate_mermaid_diagram(tasks)
    logger.info(f"生成的Mermaid代码长度: {len(mermaid_code)}")

    return jsonify({
        "success": True,
        "mermaid": mermaid_code,
        "task_count": len(tasks)  # 添加任务数量用于调试
    })

@app.route('/api/visualization/workflows/<workflow_id>/mermaid', methods=['GET'])
@log_api_time
def get_workflow_mermaid(workflow_id):
    """获取工作流Mermaid图"""
    from utils.visualization import TaskVisualizer

    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        return handle_error("工作流不存在", 404)

    workflow_dict = workflow.to_dict()
    mermaid_code = TaskVisualizer.generate_workflow_mermaid(workflow_dict)

    return jsonify({
        "success": True,
        "mermaid": mermaid_code
    })

@app.route('/api/visualization/tasks/d3', methods=['GET'])
@log_api_time
def get_task_d3_json():
    """获取任务D3.js格式数据"""
    from utils.visualization import TaskVisualizer

    # 获取所有任务
    tasks = [task.to_dict() for task in task_manager.tasks.values()]

    # 生成D3.js数据
    d3_data = TaskVisualizer.generate_d3_json(tasks)

    return jsonify({
        "success": True,
        "data": d3_data
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Flask应用启动中...")
    print("📍 访问地址:")
    print("   - 统一管理平台: http://localhost:5001/")
    print("   - 🌟 智能产品规划师: http://localhost:5001/smart-planner")
    print("   - 任务管理: http://localhost:5001/tasks")
    print("   - 可视化: http://localhost:5001/visualization")
    print("   - 角色管理: http://localhost:5001/roles")
    print("   - 测试页面: http://localhost:5001/test")
    print("\n📋 API接口:")
    print("   - 数字人状态: http://localhost:5001/api/digital-humans")
    print("   - 任务管理: http://localhost:5001/api/tasks")
    print("   - 工作流: http://localhost:5001/api/workflows")
    print("   - 工作流模板: http://localhost:5001/api/workflows/templates")
    print("=" * 50)

    # 使用SocketIO启动（如果可用）
    if SOCKETIO_AVAILABLE and socketio:
        try:
            socketio.run(app, debug=True, host='0.0.0.0', port=5001)
        except Exception as e:
            logger.error(f"SocketIO启动失败，使用普通模式: {e}")
            app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        app.run(debug=True, host='0.0.0.0', port=5001)
