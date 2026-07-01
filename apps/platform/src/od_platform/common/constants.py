"""项目级共享常量——所有模块的"共同词汇表"。
放这里的标准:多模块共享(>=2 处用到) + 纯定义无逻辑 + 极少改动。本文件按需增长。
"""
from __future__ import annotations
from typing import Tuple

# —— 标注格式名(阶段 2:@register 要用,且会在多个 converter/CLI/测试复用)——
class AnnotationFormat:
    PASCAL_VOC = "pascal_voc"
    COCO       = "coco"
    YOLO       = "yolo"
    @classmethod
    def all(cls) -> Tuple[str, ...]:
        return cls.PASCAL_VOC, cls.COCO, cls.YOLO

# —— 任务类型(同上)——
class Task:
    DETECT  = "detect"
    SEGMENT = "segment"
    @classmethod
    def all(cls) -> Tuple[str, ...]:
        return cls.DETECT, cls.SEGMENT