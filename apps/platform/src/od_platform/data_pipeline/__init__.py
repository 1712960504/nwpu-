"""data_pipeline - 数据流水线子系统

将 data/raw/ 下的原始标注转换成 YOLO 格式，划分 train/val/test，
生成可直接喂给 ultralytics 的 dataset.yaml。

Public API:
    - DatasetPipeline: 编排器，一条命令串起 转换→报告→划分→落盘→yaml
    - convert_data_to_yolo, ConvertOptions: 格式转换入口
    - split_pairs, SplitOptions, list_strategies: 划分入口
    - SplitManifest, Pair, PairList: 数据类型
    - materialize, SplitOutputDirs: 落盘工具
    - write_dataset_yaml: yaml 生成
"""

from od_platform.data_pipeline.orchestrator import DatasetPipeline
from od_platform.data_pipeline.convert.service import convert_data_to_yolo
from od_platform.data_pipeline.convert.registry import ConvertOptions
from od_platform.data_pipeline.split.split_service import split_pairs
from od_platform.data_pipeline.split.strategy_registry import SplitOptions, list_strategies
from od_platform.data_pipeline.split.manifest import SplitManifest, Pair, PairList
from od_platform.data_pipeline.split.materializer import materialize, SplitOutputDirs
from od_platform.data_pipeline.split.yaml_writer import write_dataset_yaml
