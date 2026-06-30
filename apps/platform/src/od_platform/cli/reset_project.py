#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  : reset_project.py
# @Author    : 雨霓同学
# @Project   : ODPlatform
# @Function  : 项目重置工具——安全、可控、可追溯地清理 init_project 创建的运行时产物
#
# 安全设计（详见 ADR-002）：
#   - 默认安全（Safe by Default）：无 --yes 绝不删除
#   - 双层防护（Two-layer Defense）：Allowlist（get_dirs_to_reset）+ Denylist（PROTECTED_DIRS）
#   - 自指安全：工具日志写入 META_LOGGING_DIR，与业务 LOGGING_DIR 物理隔离
#   - 审计追踪：每次执行落盘独立审计日志

import argparse
import io
import logging
import os
import shutil
import stat
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from od_platform.common.audit_utils import _audit_context, format_audit_line
from od_platform.common.decorators import log_call, timing
from od_platform.common.logging_utils import get_logger
from od_platform.common.paths import (
    META_LOGGING_DIR,
    ROOT_DIR,
    get_dirs_to_reset,
    is_protected,
)
from od_platform.common.string_utils import format_table_row, format_table_separator
from od_platform.common.system_utils import _format_size

# ---- 修复 Windows GBK 终端 emoji 编码问题 ----
if sys.stdout.encoding and sys.stdout.encoding.upper() in ("GBK", "GB2312", "GB18030"):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

# ============================================================
# 常量
# ============================================================

LINE_WIDTH: int = 70
LARGE_DIR_THRESHOLD: int = 1 * 1024**3  # 1 GiB，超过此阈值打印预警

logger = logging.getLogger(__name__)


# ============================================================
# 目录扫描
# ============================================================

def _scan_dir(path: Path) -> Tuple[int, int]:
    """
    递归扫描目录，统计文件数与总字节数。

    Args:
        path: 目标目录路径

    Returns:
        (file_count, total_bytes) 元组。
        目录不存在时返回 (0, 0)。
        扫描中遇到权限错误时记录 WARNING 并返回已统计的部分结果。
    """
    if not path.exists():
        return 0, 0

    file_count = 0
    total_bytes = 0

    try:
        for entry in path.rglob("*"):
            try:
                if entry.is_file():
                    file_count += 1
                    total_bytes += entry.stat().st_size
            except (PermissionError, OSError) as e:
                logger.warning(f"跳过无法访问的文件: {entry.relative_to(ROOT_DIR)} ({e})")
    except (PermissionError, OSError) as e:
        logger.warning(f"扫描目录时出错: {path.relative_to(ROOT_DIR)} ({e})")

    return file_count, total_bytes


# ============================================================
# 删除计划展示
# ============================================================

def _print_plan(
    targets: List[Path],
    scans: Dict[Path, Tuple[int, int]],
    dry_run: bool,
) -> None:
    """
    输出删除计划表格。

    Args:
        targets: 待删除目录列表
        scans: 扫描结果 {path: (file_count, total_bytes)}
        dry_run: 是否为 dry-run 模式
    """
    header = (
        "📋 [DRY-RUN] 计划如下（未实际删除）"
        if dry_run
        else "⚠️  即将删除以下目录"
    )
    logger.info(header)

    widths = [34, 14, 16]
    aligns = ["left", "right", "right"]

    logger.info(format_table_row(["目录", "文件数", "大小"], widths, aligns))
    logger.info(format_table_separator(widths))

    total_files = 0
    total_bytes = 0

    for d in targets:
        rel = str(d.relative_to(ROOT_DIR))
        fc, tb = scans.get(d, (0, 0))
        total_files += fc
        total_bytes += tb
        size_str = _format_size(tb) if tb > 0 else "0 B"
        logger.info(format_table_row([rel, str(fc), size_str], widths, aligns))

    logger.info(format_table_separator(widths))
    logger.info(
        format_table_row(
            ["合计", str(total_files), _format_size(total_bytes)],
            widths,
            aligns,
        )
    )

    # 明确列出不会被触碰的目录
    logger.info("")
    logger.info("🔒 以下目录不会被触碰（受保护）：")
    logger.info(f"   • data/raw/          — 原始数据（只读）")
    logger.info(f"   • models/pretrained/ — 预训练权重")
    logger.info(f"   • apps/              — 代码（git-tracked）")
    logger.info(f"   • .git/              — 版本控制")
    logger.info(f"   • meta_logging/      — 审计日志")


# ============================================================
# Windows 只读文件处理
# ============================================================

def _on_rm_error(func, path, exc_info):
    """
    shutil.rmtree 的 onerror 回调。

    处理 Windows 上只读文件导致的 PermissionError：
    尝试 chmod +w 后重试一次，仍失败则传播异常。

    Args:
        func: 失败的操作函数
        path: 失败的文件/目录路径
        exc_info: sys.exc_info() 三元组
    """
    exc_type, exc_value, _ = exc_info
    # 仅在权限类错误时尝试 chmod
    if exc_type in (PermissionError, OSError):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)  # 重试一次
            return
        except Exception:
            pass
    # 重试失败或非权限错误 → 传播
    raise exc_value


# ============================================================
# 交互式确认
# ============================================================

def _confirm_dialog(target_count: int, input_func=input) -> bool:
    """
    不可逆操作前的交互式二次确认。

    使用裸 print（而非 logger），用视觉风格硬切打断用户的"扫日志惯性"，
    强制注意力切换为"主动决策"模式。

    Args:
        target_count: 将要删除的目录数量
        input_func:  输入函数（默认 stdin；测试时可注入）

    Returns:
        True 表示用户确认，False 表示取消
    """
    print()
    print("=" * LINE_WIDTH)
    print(f"⚠️  你正要删除 {target_count} 个目录的内容。这个操作不可撤销。")
    print(f"⚠️  如果确认，请精确输入大写的 'RESET'（其他任何输入都会取消）：")
    print("=" * LINE_WIDTH)
    try:
        user_input = input_func("> ")
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    return user_input.strip() == "RESET"


# ============================================================
# 实际删除执行
# ============================================================

@log_call(log_level=logging.INFO, log_args=True, log_result=True, max_arg_len=200)
@timing(log_level=logging.INFO, msg="删除阶段")
def _execute_deletion(
    targets: List[Path],
    scans: Dict[Path, Tuple[int, int]],
) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    """
    逐目录执行删除，输出进度。

    采用 best-effort 策略：单个目录失败不中断后续目录，
    最终汇总报告所有成功与失败项。

    Args:
        targets: 待删除目录列表
        scans:   扫描结果

    Returns:
        (success_list, failed_list)
        - success_list: 成功删除的目录列表
        - failed_list:  (path, error_message) 元组列表
    """
    total = len(targets)
    success: List[Path] = []
    failed: List[Tuple[Path, str]] = []

    for i, d in enumerate(targets, 1):
        rel = str(d.relative_to(ROOT_DIR))
        fc, tb = scans.get(d, (0, 0))
        size_str = _format_size(tb) if tb > 0 else "0 B"

        # 大目录预警
        if tb >= LARGE_DIR_THRESHOLD:
            logger.warning(f"[{i}/{total}] 删除 {rel} ({size_str}, {fc} 个文件) ——这可能需要一会...")
        else:
            logger.info(f"[{i}/{total}] 删除 {rel} ({size_str}, {fc} 个文件)")

        if not d.exists():
            logger.info(f"[{i}/{total}] ✅ 已不存在（跳过）: {rel}")
            success.append(d)
            continue

        try:
            shutil.rmtree(d, onerror=_on_rm_error)
            logger.info(f"[{i}/{total}] ✅ 已删除: {rel}")
            success.append(d)
        except Exception as e:
            logger.error(f"[{i}/{total}] ❌ 删除失败 {rel}: {e}")
            failed.append((d, str(e)))

    return success, failed


# ============================================================
# 执行汇总
# ============================================================

def _print_summary(success: List[Path], failed: List[Tuple[Path, str]]) -> None:
    """
    输出删除流程汇总。

    Args:
        success: 成功删除的目录列表
        failed:  (path, error_message) 元组列表
    """
    logger.info("=" * LINE_WIDTH)
    logger.info(f"完成: 成功 {len(success)} 个，失败 {len(failed)} 个")
    if failed:
        for path, err_msg in failed:
            rel = str(path.relative_to(ROOT_DIR))
            logger.error(f"  - {rel}: {err_msg}")


# ============================================================
# 业务函数（纯函数，可作为库调用）
# ============================================================

def reset_project(
    yes: bool = False,
    force: bool = False,
    dry_run: bool = False,
    confirm: bool = False,
) -> int:
    """
    项目重置主流程。

    所有参数显式传入，不读取 sys.argv 或环境变量，
    便于测试以及作为库被其他工具调用。

    Args:
        yes:     （保留兼容）与 confirm 效果相同
        confirm: 是否确认执行删除（默认 False = 仅 dry-run）
        force:   是否跳过交互确认（仅在 confirm/yes=True 时有效）
        dry_run: 显式声明 dry-run；与 confirm 互斥时优先（更安全）

    Returns:
        进程退出码：
            0 = 成功 / dry-run 完成 / 用户取消
            1 = 部分删除失败
            2 = 全部删除失败 / 双层防护触发
    """
    # ---- 合并 --yes 和 --confirm ----
    confirmed = yes or confirm

    # ---- 参数冲突处理：dry_run 与 confirmed 互斥时优先 dry_run ----
    if dry_run and confirmed:
        logger.warning(
            "⚠️  同时给了 --dry-run 和 --confirm/--yes，以 --dry-run 为准（只打印不删除）"
        )
        confirmed = False

    # ---- 1. 装配日志（写入 META_LOGGING_DIR，与业务 LOGGING_DIR 隔离）----
    get_logger(
        base_path=META_LOGGING_DIR,
        log_type="reset_project",
        temp_log=False,
    )

    # ---- 2. 采集并落盘审计上下文 ----
    audit = _audit_context(tool_name="reset_project")
    logger.info(format_audit_line(audit))

    logger.info("=" * LINE_WIDTH)
    logger.info("项目重置工具")
    logger.info(f"项目根目录: {ROOT_DIR}")
    logger.info("=" * LINE_WIDTH)

    # ---- 3. 获取删除清单（第一层防护：Allowlist）----
    targets = get_dirs_to_reset()
    logger.info(f"候选目录共 {len(targets)} 个（白名单筛选）")

    # ---- 4. 第二层防护：Denylist 复核 ----
    for t in targets:
        if is_protected(t):
            logger.error(
                f"🛑 双层防护触发！以下路径命中受保护清单：{t.relative_to(ROOT_DIR)}"
            )
            logger.error("🛑 操作已中止，任何目录均未被删除。")
            logger.error(
                "🛑 这通常是因为 get_dirs_to_reset() 白名单配置错误，请联系开发者。"
            )
            return 2  # 立即中止，fail-fast

    # ---- 5. 扫描目标目录 ----
    logger.info("正在扫描目标目录...")
    scans: Dict[Path, Tuple[int, int]] = {}
    for d in targets:
        scans[d] = _scan_dir(d)

    # ---- 6. 输出删除计划 ----
    _print_plan(targets, scans, dry_run=not confirmed or dry_run)

    # ---- 7. 决策分支 ----
    if not confirmed or dry_run:
        # dry-run 模式 — 不执行删除
        logger.info("💡 这是 dry-run（默认行为）。要真正执行删除，请加 --confirm")
        logger.info("💡 示例: odp-reset --confirm")
        return 0

    # 真实删除前检查是否为空
    if not any(d.exists() for d in targets):
        logger.info("没有需要删除的目录（所有目标目录均不存在）。")
        return 0

    # 交互式确认（force 模式下跳过）
    if not force:
        confirmed = _confirm_dialog(len(targets))
        if not confirmed:
            logger.warning("❌ 用户取消，未执行删除")
            return 0

    # ---- 8. 执行删除 ----
    success, failed = _execute_deletion(targets, scans)

    # ---- 9. 输出汇总 ----
    _print_summary(success, failed)

    # ---- 10. 返回退出码 ----
    if len(failed) == 0:
        return 0
    elif len(failed) == len(targets):
        return 2  # 全部失败
    else:
        return 1  # 部分失败


# ============================================================
# CLI 参数解析
# ============================================================

def _build_parser() -> argparse.ArgumentParser:
    """构建 argparse 解析器。"""
    parser = argparse.ArgumentParser(
        prog="odp-reset",
        description=(
            "ODPlatform 项目重置工具——安全、可控地清理 init_project 创建的运行时产物。\n"
            "默认行为是 dry-run（仅预览不删除），必须显式给出 --confirm 才执行删除。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  odp-reset                    默认 dry-run，预览将要删除的内容\n"
            "  odp-reset --confirm           执行删除（需交互确认）\n"
            "  odp-reset --confirm --force   跳过确认，直接删除（CI 场景）\n"
            "  odp-reset --dry-run           显式 dry-run（与默认行为相同）\n"
            "\n"
            "确认机制:\n"
            "  --confirm / -y   确认要执行删除（默认仅 dry-run 预览）\n"
            "  --force          跳过交互式打字确认（仅在 --confirm 同时有效）\n"
            "\n"
            "安全机制:\n"
            "  默认 dry-run —— 无 --confirm 绝不删除\n"
            "  双层防护 —— 白名单 + 黑名单协同\n"
            "  二次确认 —— 输入 RESET 才执行\n"
            "  审计日志 —— 每次执行独立记录\n"
        ),
    )

    parser.add_argument(
        "--confirm", "-y",
        action="store_true",
        default=False,
        help="确认执行删除（默认仅 dry-run 预览，不会实际删除）",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        default=False,
        help="与 --confirm 相同（保留兼容）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="跳过交互式打字确认，直接删除（仅在 --confirm 同时有效）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="显式声明 dry-run（与默认行为相同，但在与 --confirm 冲突时更安全）",
    )

    return parser


# ============================================================
# CLI 主入口
# ============================================================

def main() -> int:
    """
    CLI 主入口。

    供 pyproject.toml console_scripts 注册、
    python -m 调用、以及 scripts/reset_project.py 转发。

    Returns:
        进程退出码
    """
    parser = _build_parser()
    args = parser.parse_args()

    return reset_project(
        yes=args.yes,
        confirm=args.confirm,
        force=args.force,
        dry_run=args.dry_run,
    )


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    # 当脚本直接运行时，转发到 main()
    sys.exit(main())
