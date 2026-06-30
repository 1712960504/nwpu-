#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  : scripts/reset_project.py
# @Author    : 雨霓同学
# @Function  : 项目重置的【开发阶段入口】(无需安装 package)
#
# 用法:
#   python scripts/reset_project.py               # dry-run 预览
#   python scripts/reset_project.py --yes --force  # 直接清理
"""ODPlatform 项目重置入口(开发阶段)"""

import sys
from pathlib import Path

# 从仓库根定位 platform 的 src 目录
REPO_ROOT = Path(__file__).resolve().parent.parent
PLATFORM_SRC = REPO_ROOT / "apps" / "platform" / "src"

# 把 src 加到 sys.path 最前面(优先于已安装版本)
sys.path.insert(0, str(PLATFORM_SRC))

# 导入 main()（不是 reset_project()）——确保 argparse 处理命令行参数
from od_platform.cli.reset_project import main

if __name__ == "__main__":
    sys.exit(main())
