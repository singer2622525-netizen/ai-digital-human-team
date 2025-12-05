#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步管理模块
支持GitHub同步和多种存储方案
"""

import os
import subprocess
import json
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SyncManager:
    """同步管理器"""
    
    def __init__(self, project_root: str):
        """
        初始化同步管理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.db_path = os.path.join(project_root, "03-技术实现/02-功能模块/storage/digital_humans.db")
        
    def get_sync_status(self) -> Dict[str, Any]:
        """
        获取同步状态
        
        Returns:
            同步状态信息
        """
        status = {
            "git": self._check_git_status(),
            "database": self._check_database_status(),
            "storage_options": self._get_storage_options()
        }
        return status
    
    def _check_git_status(self) -> Dict[str, Any]:
        """检查Git状态"""
        try:
            # 检查是否在Git仓库中
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {
                    "available": False,
                    "message": "未初始化Git仓库"
                }
            
            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            has_changes = len(result.stdout.strip()) > 0
            
            # 检查远程仓库
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            has_remote = "origin" in result.stdout
            
            return {
                "available": True,
                "has_changes": has_changes,
                "has_remote": has_remote,
                "message": "Git已配置" if has_remote else "Git已初始化，但未配置远程仓库"
            }
        except Exception as e:
            logger.error(f"检查Git状态失败: {e}")
            return {
                "available": False,
                "message": f"Git检查失败: {str(e)}"
            }
    
    def _check_database_status(self) -> Dict[str, Any]:
        """检查数据库状态"""
        db_exists = os.path.exists(self.db_path)
        db_size = 0
        
        if db_exists:
            db_size = os.path.getsize(self.db_path)
        
        return {
            "exists": db_exists,
            "size": db_size,
            "size_mb": round(db_size / 1024 / 1024, 2) if db_size > 0 else 0,
            "path": self.db_path
        }
    
    def _get_storage_options(self) -> List[Dict[str, Any]]:
        """获取可用的存储选项"""
        options = []
        
        # 1. iCloud
        icloud_path = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/DigitalHumanDB")
        if os.path.exists(os.path.dirname(icloud_path)):
            options.append({
                "type": "iCloud",
                "path": icloud_path,
                "available": True,
                "description": "iCloud云存储（Mac自动同步）"
            })
        
        # 2. Dropbox
        dropbox_path = os.path.expanduser("~/Dropbox/DigitalHumanDB")
        if os.path.exists(os.path.dirname(dropbox_path)):
            options.append({
                "type": "Dropbox",
                "path": dropbox_path,
                "available": True,
                "description": "Dropbox云存储"
            })
        
        # 3. 外部SSD（检查挂载的卷）
        volumes = ["/Volumes"]
        if os.path.exists("/Volumes"):
            for item in os.listdir("/Volumes"):
                volume_path = os.path.join("/Volumes", item)
                if os.path.isdir(volume_path) and not item.startswith("."):
                    # 检查是否是外部存储（排除系统卷）
                    if item not in ["Macintosh HD", "Macintosh HD - Data"]:
                        options.append({
                            "type": "External SSD",
                            "path": os.path.join(volume_path, "DigitalHumanDB"),
                            "available": True,
                            "description": f"外部SSD: {item}",
                            "volume_name": item
                        })
        
        # 4. Dell服务器（通过SSH/网络路径）
        # 这里需要用户配置服务器地址
        dell_server_path = os.getenv("DELL_SERVER_PATH", "")
        if dell_server_path:
            options.append({
                "type": "Dell Server",
                "path": dell_server_path,
                "available": os.path.exists(dell_server_path),
                "description": "公司Dell服务器存储"
            })
        
        return options
    
    def sync_to_git(self, commit_message: str = None) -> Dict[str, Any]:
        """
        同步代码到Git
        
        Args:
            commit_message: 提交信息
            
        Returns:
            同步结果
        """
        try:
            if not commit_message:
                commit_message = f"Auto sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 添加所有更改
            result = subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Git add失败: {result.stderr}"
                }
            
            # 提交
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 检查是否有更改（如果没有更改，commit会失败，这是正常的）
            has_changes = result.returncode == 0
            
            # 推送到远程
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                # 检查是否是因为没有远程仓库
                if "no upstream branch" in result.stderr or "remote" not in result.stderr.lower():
                    return {
                        "success": False,
                        "error": "未配置远程仓库，请先在终端中运行: git remote add origin <url>"
                    }
                return {
                    "success": False,
                    "error": f"Git push失败: {result.stderr}"
                }
            
            return {
                "success": True,
                "message": "代码已同步到GitHub",
                "has_changes": has_changes
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Git操作超时"
            }
        except Exception as e:
            logger.error(f"Git同步失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_from_git(self) -> Dict[str, Any]:
        """
        从Git拉取最新代码
        
        Returns:
            同步结果
        """
        try:
            # 拉取最新代码
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                if "no upstream branch" in result.stderr:
                    return {
                        "success": False,
                        "error": "未配置远程仓库"
                    }
                return {
                    "success": False,
                    "error": f"Git pull失败: {result.stderr}"
                }
            
            return {
                "success": True,
                "message": "代码已从GitHub同步",
                "output": result.stdout
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Git操作超时"
            }
        except Exception as e:
            logger.error(f"Git拉取失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_database(self, storage_type: str, storage_path: str) -> Dict[str, Any]:
        """
        同步数据库文件到指定存储
        
        Args:
            storage_type: 存储类型（iCloud/Dropbox/SSD/Server）
            storage_path: 存储路径
            
        Returns:
            同步结果
        """
        try:
            if not os.path.exists(self.db_path):
                return {
                    "success": False,
                    "error": "数据库文件不存在"
                }
            
            # 创建目标目录
            os.makedirs(storage_path, exist_ok=True)
            
            target_path = os.path.join(storage_path, "digital_humans.db")
            
            # 检查目标文件是否存在
            if os.path.exists(target_path):
                # 比较时间戳，使用最新的
                local_time = os.path.getmtime(self.db_path)
                remote_time = os.path.getmtime(target_path)
                
                if local_time > remote_time:
                    # 本地更新，上传
                    shutil.copy2(self.db_path, target_path)
                    action = "上传"
                elif remote_time > local_time:
                    # 远程更新，下载
                    shutil.copy2(target_path, self.db_path)
                    action = "下载"
                else:
                    action = "已同步"
            else:
                # 首次同步，上传
                shutil.copy2(self.db_path, target_path)
                action = "首次上传"
            
            return {
                "success": True,
                "message": f"数据库已{action}到{storage_type}",
                "local_path": self.db_path,
                "remote_path": target_path,
                "action": action
            }
        except Exception as e:
            logger.error(f"数据库同步失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def setup_git_remote(self, remote_url: str) -> Dict[str, Any]:
        """
        设置Git远程仓库
        
        Args:
            remote_url: 远程仓库URL
            
        Returns:
            设置结果
        """
        try:
            # 检查是否已有远程仓库
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # 更新现有远程仓库
                result = subprocess.run(
                    ["git", "remote", "set-url", "origin", remote_url],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                action = "更新"
            else:
                # 添加新远程仓库
                result = subprocess.run(
                    ["git", "remote", "add", "origin", remote_url],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                action = "添加"
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"设置远程仓库失败: {result.stderr}"
                }
            
            return {
                "success": True,
                "message": f"远程仓库已{action}",
                "remote_url": remote_url
            }
        except Exception as e:
            logger.error(f"设置Git远程仓库失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

