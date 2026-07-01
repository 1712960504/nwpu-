from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from od_platform.data_pipeline.split.manifest import PairList, SplitManifest

logger = logging.getLogger(__name__)

# 相对路径约定 —— yaml_writer 等模块从这里取，而不是各自硬编码。
TRAIN_IMAGES_REL = "train/images"
VAL_IMAGES_REL = "val/images"
TEST_IMAGES_REL = "test/images"
TRAIN_LABELS_REL = "train/labels"
VAL_LABELS_REL = "val/labels"
TEST_LABELS_REL = "test/labels"


@dataclass(frozen=True)
class SplitOutputDirs:
    train_images: Path
    val_images: Path
    test_images: Path
    train_labels: Path
    val_labels: Path
    test_labels: Path

    @classmethod
    def for_dataset_root(cls, root: Path) -> "SplitOutputDirs":
        return cls(
            train_images=root / TRAIN_IMAGES_REL,
            val_images=root / VAL_IMAGES_REL,
            test_images=root / TEST_IMAGES_REL,
            train_labels=root / TRAIN_LABELS_REL,
            val_labels=root / VAL_LABELS_REL,
            test_labels=root / TEST_LABELS_REL,
        )

    def all_dirs(self):
        return (self.train_images, self.train_labels,
                self.val_images, self.val_labels,
                self.test_images, self.test_labels)

def _place(src: Path, dst: Path) -> None:
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)

def _materialize_one(pairs: PairList, images_dir: Path, labels_dir: Path) -> int:
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    for img, lbl in pairs:
        _place(img, images_dir/ img.name)
        _place(lbl, labels_dir/ lbl.name)
    return len(pairs)

def materialize(manifest: SplitManifest, dirs: SplitOutputDirs) -> Dict[str, int]:
    """将 SplitManifest 中的文件对物化到输出目录，返回各子集文件对数。"""
    for d in dirs.all_dirs():
        if d.exists():
            shutil.rmtree(d)
    counts = {
        "train": _materialize_one(manifest.train, dirs.train_images, dirs.train_labels),
        "val": _materialize_one(manifest.val, dirs.val_images, dirs.val_labels),
        "test": _materialize_one(manifest.test, dirs.test_images, dirs.test_labels),
    }
    counts["total"] = sum(counts.values())
    logger.info("materialized %s samples to %s", counts, dirs)
    return counts