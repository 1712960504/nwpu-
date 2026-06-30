#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  : audit_utils.py
# @Author    : 雨霓同学
# @Project   : ODPlatform
# @Function  : 审计上下文采集——为元工具（reset_project 等）提供可追溯的操作记录
#
# 设计哲学:
#   - 本模块是"纯数据采集器"：只采集、只返回 dict，不写任何文件。
#   - 写文件由调用方（CLI 入口）负责，保持采集与持久化的职责分离。
#   - 所有采集失败均走降级策略（"unknown"），绝不因采集异常而中断业务流程。

import getpass
import json
import logging
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from od_platform._version import __version__
from od_platform.common.paths import ROOT_DIR

logger = logging.getLogger(__name__)


def _audit_context(tool_name: str = "reset_project") -> Dict[str, Any]:
    """
    采集结构化审计上下文字典。

    每次工具执行时调用一次，采集执行者身份、环境信息、调用参数等，
    用于事后追溯"谁在什么环境以什么方式调用了工具"。

    Args:
        tool_name: 工具名称，默认 "reset_project"。
                   调用方可传入自己的名称用于日志区分。

    Returns:
        包含以下字段的字典：
        - timestamp:      UTC 时间，ISO 8601 格式
        - tool_name:      工具名称
        - tool_version:   od_platform 版本号
        - user:           操作系统用户名（失败降级 "unknown"）
        - hostname:       主机名
        - cwd:            执行时的工作目录
        - root_dir:       仓库根目录
        - argv:           命令行参数列表
        - os_info:        操作系统名与版本
        - python_version: Python 版本
        - git_commit:     当前 HEAD commit hash（失败降级 "unknown"）
    """
    # --- 时间戳（UTC，ISO 8601）---
    timestamp: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- 用户（软依赖）---
    try:
        user: str = getpass.getuser()
    except Exception:
        user = "unknown"

    # --- 主机名 ---
    hostname: str = socket.gethostname()

    # --- 工作目录 ---
    cwd: str = str(Path.cwd())

    # --- 操作系统 ---
    os_info: str = f"{platform.system()}-{platform.release()}"

    # --- Python 版本 ---
    python_version: str = platform.python_version()

    # --- Git commit（软依赖：环境无 git 时降级）---
    git_commit: str = "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            git_commit = result.stdout.strip()
    except Exception:
        pass  # 任何失败都降级为 "unknown"，不抛异常

    return {
        "timestamp": timestamp,
        "tool_name": tool_name,
        "tool_version": __version__,
        "user": user,
        "hostname": hostname,
        "cwd": cwd,
        "root_dir": str(ROOT_DIR),
        "argv": sys.argv,
        "os_info": os_info,
        "python_version": python_version,
        "git_commit": git_commit,
    }


def format_audit_line(context: Dict[str, Any]) -> str:
    """
    将审计上下文字典序列化为单行 JSON，带 [AUDIT] 前缀。

    Args:
        context: _audit_context() 返回的字典

    Returns:
        单行字符串，格式：`[AUDIT] <JSON>`
    """
    return f"[AUDIT] {json.dumps(context, ensure_ascii=False)}"


if __name__ == "__main__":
    # 自测：采集并打印审计上下文
    ctx = _audit_context()
    print(format_audit_line(ctx))
    print()
    print("各字段:")
    for key, value in ctx.items():
        print(f"  {key:20s}: {value}")
