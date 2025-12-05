#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字人模块
"""

from .base import BaseDigitalHuman, OllamaClient
from .project_manager import ProjectManager
from .architect import SystemArchitect
from .frontend_engineer import FrontendEngineer
from .backend_engineer import BackendEngineer
from .devops_engineer import DevOpsEngineer
from .smart_product_planner import SmartProductPlanner
from .实时记录员 import RealTimeRecorder
from .质量观察员 import QualityObserver
from .知识管理员 import KnowledgeAdministrator

__all__ = [
    'BaseDigitalHuman',
    'OllamaClient',
    'ProjectManager',
    'SystemArchitect',
    'FrontendEngineer',
    'BackendEngineer',
    'DevOpsEngineer',
    'SmartProductPlanner',
    'RealTimeRecorder',
    'QualityObserver',
    'KnowledgeAdministrator'
]
