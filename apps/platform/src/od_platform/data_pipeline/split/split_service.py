"""split 调度层 —— 按策略名查表、校验前置条件、分发。

它是项目其它部分（orchestrator / CLI / 测试）唯一该调用的"划分入口"。
关键性质：【永不增长】—— 无论将来支持多少种划分策略，本文件一行都不用改。
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from od_platform.common.constants import DEFAULT_RANDOM_STATE, DEFAULT_SPLIT_STRATEGY
from od_platform.data_pipeline.split.strategy_registry import SplitOptions, get_strategy
from od_platform.data_pipeline.split.manifest import PairList, SplitManifest

logger = logging.getLogger(__name__)


def split_pairs(
    pairs: PairList,
    train_rate: float = 0.8,
    val_rate: float = 0.1,
    random_state: int = DEFAULT_RANDOM_STATE,
    *,
    strategy: str = DEFAULT_SPLIT_STRATEGY,
    labels_per_image: Optional[Dict[str, List[str]]] = None,
    group_per_image: Optional[Dict[str, str]] = None,
) -> SplitManifest:
    """统一入口：按 strategy 名分发到具体划分策略，返回 SplitManifest。

    Raises:
        ValueError: 策略需要 labels_per_image 但未提供。
    """
    entry = get_strategy(strategy)
    if entry.requires_labels and labels_per_image is None:
        raise ValueError(f"划分策略 {strategy!r} 需要 labels_per_image，但未提供")
    logger.info("用策略 %s 划分 %d 对样本 (train=%.0f%%/val=%.0f%%)",
                strategy, len(pairs), train_rate * 100, val_rate * 100)
    options = SplitOptions(
        train_rate=train_rate, val_rate=val_rate, random_state=random_state,
        labels_per_image=labels_per_image, group_per_image=group_per_image,
    )
    return entry.func(pairs, options)
