"""split 核心数据类型：图像-标注对、划分结果清单。

Pair 使用 NamedTuple 让 p.image / p.label 自文档化，
同时保持 p[0] / p[1] 和解包 (img, lbl) 向后兼容。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, NamedTuple


class Pair(NamedTuple):
    """一对 (图像路径, 标签路径)。

    用法:
        p = Pair(img, lbl)
        p.image   # Path → 图像
        p.label   # Path → 标签
        p[0]      # 等价于 p.image（向后兼容）
        img, lbl = p  # 解包
    """
    image: Path
    label: Path


PairList = List[Pair]


@dataclass
class SplitManifest:
    """一次划分的完整结果：train/val/test 三组 Pair + 划分元数据。

    test_rate 由 train_rate + val_rate 导出（非独立字段），
    确保三者始终自洽。
    """
    train: PairList = field(default_factory=list)
    val: PairList = field(default_factory=list)
    test: PairList = field(default_factory=list)

    train_rate: float = 0.8
    val_rate: float = 0.1
    random_state: int = 114514
    strategy: str = "random"

    def __post_init__(self) -> None:
        """校验比例合法性。"""
        t = 1.0 - self.train_rate - self.val_rate
        if not (-1e-6 <= self.train_rate <= 1 and -1e-6 <= self.val_rate <= 1 and -1e-6 <= t <= 1):
            raise ValueError(
                f"比例越界: train={self.train_rate}, val={self.val_rate}, "
                f"test={t}"
            )

    @property
    def test_rate(self) -> float:
        """test 比例 = 1 - train_rate - val_rate（始终自洽）。"""
        return max(0.0, 1.0 - self.train_rate - self.val_rate)

    def summary(self) -> Dict[str, int]:
        return {
            "train": len(self.train),
            "val": len(self.val),
            "test": len(self.test),
            "total": len(self.train) + len(self.val) + len(self.test),
        }
