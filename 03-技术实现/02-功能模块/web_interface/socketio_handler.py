#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket实时更新处理器
"""

from flask_socketio import SocketIO, emit
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# 全局SocketIO实例（将在app.py中初始化）
socketio = None


def init_socketio(app):
    """
    初始化SocketIO
    
    Args:
        app: Flask应用实例
    """
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    return socketio


def emit_task_update(task_data: Dict[str, Any], event_type: str = "task_update"):
    """
    发送任务更新事件
    
    Args:
        task_data: 任务数据
        event_type: 事件类型
    """
    if socketio:
        # Flask-SocketIO新版本不支持broadcast参数，使用namespace=None来广播
        socketio.emit(event_type, task_data, namespace='/')
        logger.debug(f"发送任务更新事件: {task_data.get('id', 'unknown')[:8]}...")


def emit_workflow_update(workflow_data: Dict[str, Any], event_type: str = "workflow_update"):
    """
    发送工作流更新事件
    
    Args:
        workflow_data: 工作流数据
        event_type: 事件类型
    """
    if socketio:
        socketio.emit(event_type, workflow_data, namespace='/')
        logger.debug(f"发送工作流更新事件: {workflow_data.get('id', 'unknown')[:8]}...")


def emit_statistics_update(stats_data: Dict[str, Any]):
    """
    发送统计信息更新事件
    
    Args:
        stats_data: 统计数据
    """
    if socketio:
        socketio.emit("statistics_update", stats_data, namespace='/')
        logger.debug("发送统计信息更新事件")


def emit_digital_human_update(human_data: Dict[str, Any]):
    """
    发送数字人状态更新事件
    
    Args:
        human_data: 数字人数据
    """
    if socketio:
        socketio.emit("digital_human_update", human_data, namespace='/')
        logger.debug(f"发送数字人更新事件: {human_data.get('name', 'unknown')}")


def register_socketio_handlers(socketio_instance):
    """
    注册SocketIO事件处理器
    
    Args:
        socketio_instance: SocketIO实例
    """
    global socketio
    socketio = socketio_instance
    
    @socketio.on('connect')
    def handle_connect():
        """处理客户端连接"""
        logger.info("客户端已连接")
        emit('connected', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        logger.info("客户端已断开连接")
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        """
        处理订阅请求
        
        Args:
            data: 订阅数据，包含订阅类型
        """
        subscribe_type = data.get('type', 'all')
        logger.info(f"客户端订阅: {subscribe_type}")
        emit('subscribed', {'type': subscribe_type, 'status': 'success'})

