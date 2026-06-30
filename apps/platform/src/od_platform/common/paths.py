#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  : paths.py
# @Author    : 雨霓同学
# @Project   : ODPlatform
# @Function  : 集中定义项目路径常量
#              - 使用 marker file 模式定位 ROOT_DIR(workspace 根)
#              - 引入 APP_DIR 概念,把【共享资产】和【端私有资产】分开

from pathlib import Path
from typing import List, Tuple

# ============================================================
# Workspace 根目录定位 (marker file 模式)
# ============================================================
WORKSPACE_MARKER: str = ".odp-workspace"


def _find_workspace_root(
    start: Path,
    markers: Tuple[str, ...] = (WORKSPACE_MARKER,),
) -> Path:
    """
    从 start 开始沿父目录向上查找,返回包含任一 marker 文件的目录。

    Args:
        start: 起始路径(通常是 Path(__file__))
        markers: 一组 marker 文件名,任一存在即视为找到

    Returns:
        Path: workspace 根目录

    Raises:
        FileNotFoundError: 一直爬到文件系统根仍没找到
    """
    current = start.resolve()
    if current.is_file():
        current = current.parent

    for parent in [current, *current.parents]:
        for marker in markers:
            if (parent / marker).exists():
                return parent

    raise FileNotFoundError(
        f"找不到 workspace marker 文件 ({markers})。"
        f"请确认仓库根存在 {WORKSPACE_MARKER} 文件。"
    )


# 计算 ROOT_DIR(模块加载时执行一次)
ROOT_DIR: Path = _find_workspace_root(Path(__file__))


# ============================================================
# 端根目录 APP_DIR (platform 这一个端的根)
# ============================================================
APP_DIR: Path = ROOT_DIR / "apps" / "platform"


# ============================================================
# 【共享资产】(在 ROOT_DIR 下,所有端可访问)
# ============================================================
DATA_DIR: Path = ROOT_DIR / "data"
MODELS_DIR: Path = ROOT_DIR / "models"
RUNS_DIR: Path = ROOT_DIR / "runs"

# 模型子目录
PRETRAINED_MODELS_DIR: Path = MODELS_DIR / "pretrained"  # 下载的预训练权重(输入)
TRAINED_MODELS_DIR: Path = MODELS_DIR / "trained"        # 训练产出、长期保留的权重(产物)
CHECKPOINTS_DIR: Path = MODELS_DIR / "checkpoints"       # 训练过程 checkpoint(恢复训练用)

# 数据集子目录
# 设计依据见 D0 决定 5:原始(只读)与派生(可再生)分家。
# train/val/test 划分属于派生产物,会在数据处理那天用固定种子一次性
# 冻结进 processed/ 内;init 阶段只建 raw / processed 两个空目录。
RAW_DATA_DIR: Path = DATA_DIR / "raw"                    # 原始数据:只读,绝不就地改
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"        # 派生数据集:含冻结后的 train/val/test
YOLO_STAGED_LABELS_DIR: Path = RAW_DATA_DIR / "yolo_staged_labels"  # YOLO 格式暂存标注

# 数据集 train/val/test 划分目录（在 data/ 下，属共享资产）
TRAIN_DIR: Path = DATA_DIR / "train"
VAL_DIR: Path = DATA_DIR / "val"
TEST_DIR: Path = DATA_DIR / "test"

TRAIN_IMAGES_DIR: Path = TRAIN_DIR / "images"
TRAIN_ANNOTATIONS_DIR: Path = TRAIN_DIR / "annotations"
VAL_IMAGES_DIR: Path = VAL_DIR / "images"
VAL_ANNOTATIONS_DIR: Path = VAL_DIR / "annotations"
TEST_IMAGES_DIR: Path = TEST_DIR / "images"
TEST_ANNOTATIONS_DIR: Path = TEST_DIR / "annotations"


# ============================================================
# 【端私有资产】(在 APP_DIR 下,只属于 platform 这个端)
# ============================================================
CONFIGS_DIR: Path = APP_DIR / "configs"
LOGGING_DIR: Path = APP_DIR / "logging"
META_LOGGING_DIR: Path = APP_DIR / "meta_logging"
UNIT_TEST_DIR: Path = APP_DIR / "tests"


# ============================================================
# 【顶层文档目录】(共享给所有人)
# ============================================================
DOCS_DIR: Path = ROOT_DIR / "docs"


# ============================================================
# 【工程基础设施目录】(共享)
# ============================================================
SCRIPTS_DIR: Path = ROOT_DIR / "scripts"


# ============================================================
# 对外暴露的"要初始化的目录列表"
# ============================================================
def get_dirs_to_initialize() -> List[Path]:
    """
    返回项目启动时需要确保存在的所有目录列表。

    这是 init_project.py 的【唯一数据源】——
    paths.py 决定要哪些目录,init_project 只负责创建。

    Returns:
        所有需要初始化的目录路径列表
    """
    return [
        # 共享资产 — 顶层
        DATA_DIR,
        RUNS_DIR,
        MODELS_DIR,
        # 共享资产 — 模型子目录
        PRETRAINED_MODELS_DIR,
        TRAINED_MODELS_DIR,
        CHECKPOINTS_DIR,
        # 共享资产 — 数据集子目录
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        YOLO_STAGED_LABELS_DIR,
        # 共享资产 — train/val/test 划分目录
        TRAIN_IMAGES_DIR,
        TRAIN_ANNOTATIONS_DIR,
        VAL_IMAGES_DIR,
        VAL_ANNOTATIONS_DIR,
        TEST_IMAGES_DIR,
        TEST_ANNOTATIONS_DIR,
        # 端私有资产
        CONFIGS_DIR,
        LOGGING_DIR,
        META_LOGGING_DIR,
        UNIT_TEST_DIR,
        # 工程基础设施
        SCRIPTS_DIR,
        DOCS_DIR,
    ]


# ============================================================
# reset_project 工具 —— 可重置目录（Allowlist）
# ============================================================

def get_dirs_to_reset() -> List[Path]:
    """
    返回 reset_project 允许清理的运行时产物目录列表（白名单）。

    这是 reset_project 的【唯一数据源】——
    调整可删除范围只需修改本函数，不修改任何调用方。

    设计约束：
        - 列表内严禁包含 RAW_DATA_DIR、PRETRAINED_MODELS_DIR、
          DOCS_DIR、SCRIPTS_DIR、任何代码目录。
        - 该列表与 PROTECTED_DIRS 不得有重合项。

    Returns:
        允许被 reset 工具删除的目录路径列表
    """
    return [
        RUNS_DIR,
        CHECKPOINTS_DIR,
        LOGGING_DIR,
        TRAIN_DIR,
        VAL_DIR,
        TEST_DIR,
    ]


# ============================================================
# reset_project 工具 —— 受保护目录（Denylist）
# ============================================================

PROTECTED_DIRS: Tuple[Path, ...] = (
    # 工作区根
    ROOT_DIR,
    # 版本控制
    ROOT_DIR / ".git",
    # 代码
    ROOT_DIR / "apps",
    # 工程基础设施
    ROOT_DIR / "scripts",
    ROOT_DIR / "docs",
    # 原始数据（只读，不可逆）
    ROOT_DIR / "data" / "raw",
    # 预训练权重（不可逆）
    ROOT_DIR / "models" / "pretrained",
    # 工作区标记
    ROOT_DIR / ".odp-workspace",
    # 端私有配置
    APP_DIR / "configs",
    # 元工具日志（自指安全）
    APP_DIR / "meta_logging",
)


def is_protected(path: Path) -> bool:
    """
    判定给定路径是否属于受保护范围。

    判定规则（任一成立即视为受保护）：
        1. path 等于 PROTECTED_DIRS 中任一条目；
        2. path 是 PROTECTED_DIRS 中任一条目的子路径
           （ROOT_DIR 例外：仅精确匹配，不对其子路径生效，
             否则所有仓库内路径都会被判定为受保护）；
        3. path 不在 ROOT_DIR 之内（越界保护）。

    Args:
        path: 待判定的路径

    Returns:
        True 表示受保护（不可删除），False 表示可删除

    Raises:
        TypeError: 输入非 Path 类型
    """
    if not isinstance(path, Path):
        raise TypeError(f"path 必须为 pathlib.Path 类型，实际为 {type(path).__name__}")

    resolved_path = path.resolve()
    resolved_root = ROOT_DIR.resolve()

    # 规则 3：越界保护
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return True  # 路径不在 ROOT_DIR 内 → 受保护

    # 容器目录（只做精确匹配，不做子路径判定）
    # ROOT_DIR 和 apps 是容器目录——保护它们本身不被整体删除，
    # 但不阻止对其子目录的合法清理（如 apps/platform/logging）。
    _CONTAINER_DIRS = {resolved_root, (ROOT_DIR / "apps").resolve()}

    # 规则 1 + 2：等于或为子路径
    for protected in PROTECTED_DIRS:
        resolved_protected = protected.resolve()
        # 规则 1：精确匹配（对所有条目生效）
        if resolved_path == resolved_protected:
            return True
        # 规则 2：子路径判定（容器目录除外）
        if resolved_protected not in _CONTAINER_DIRS:
            try:
                resolved_path.relative_to(resolved_protected)
                return True  # path 是 protected 的子路径
            except ValueError:
                continue

    return False


if __name__ == "__main__":
    print(f"ROOT_DIR (workspace) = {ROOT_DIR}")
    print(f"APP_DIR  (platform)  = {APP_DIR}")
    print(f"\n共享资产:")
    print(f"  DATA_DIR             = {DATA_DIR.relative_to(ROOT_DIR)}")
    print(f"  MODELS_DIR           = {MODELS_DIR.relative_to(ROOT_DIR)}")
    print(f"  RUNS_DIR             = {RUNS_DIR.relative_to(ROOT_DIR)}")
    print(f"\n端私有资产:")
    print(f"  CONFIGS_DIR          = {CONFIGS_DIR.relative_to(ROOT_DIR)}")
    print(f"  LOGGING_DIR          = {LOGGING_DIR.relative_to(ROOT_DIR)}")
    print(f"  META_LOGGING_DIR     = {META_LOGGING_DIR.relative_to(ROOT_DIR)}")

    print(f"\n要初始化的目录共 {len(get_dirs_to_initialize())} 个:")
    for d in get_dirs_to_initialize():
        print(f"  - {d.relative_to(ROOT_DIR)}")

    print(f"\n可重置目录（白名单）共 {len(get_dirs_to_reset())} 个:")
    for d in get_dirs_to_reset():
        print(f"  - {d.relative_to(ROOT_DIR)}")

    print(f"\n受保护目录（黑名单）共 {len(PROTECTED_DIRS)} 个:")
    for d in PROTECTED_DIRS:
        print(f"  - {d.relative_to(ROOT_DIR)}")

    print(f"\nis_protected 自测:")
    print(f"  .git          → {is_protected(ROOT_DIR / '.git')}")
    print(f"  .git/objects  → {is_protected(ROOT_DIR / '.git' / 'objects')}")
    print(f"  data/raw/ds   → {is_protected(ROOT_DIR / 'data' / 'raw' / 'dataset_a')}")
    print(f"  runs          → {is_protected(ROOT_DIR / 'runs')}")
    print(f"  /tmp/outside  → {is_protected(Path('/tmp/somewhere'))}")
    print(f"  meta_logging  → {is_protected(META_LOGGING_DIR)}")
