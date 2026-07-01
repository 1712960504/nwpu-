"""split - 数据集划分子系统

将转换后的 (image, label) 对按策略划分为 train/val/test，
产生 SplitManifest，再由 materialize 物化到输出目录。

Public API:
    - split_pairs: 统一划分入口
    - SplitOptions, list_strategies: 策略注册表
    - SplitManifest, Pair, PairList: 数据类型
    - materialize, SplitOutputDirs: 落盘工具
    - write_dataset_yaml: 生成 dataset.yaml
"""

from od_platform.data_pipeline.split.split_service import split_pairs
from od_platform.data_pipeline.split.strategy_registry import SplitOptions, list_strategies
from od_platform.data_pipeline.split.manifest import SplitManifest, Pair, PairList
from od_platform.data_pipeline.split.materializer import materialize, SplitOutputDirs
from od_platform.data_pipeline.split.yaml_writer import write_dataset_yaml
