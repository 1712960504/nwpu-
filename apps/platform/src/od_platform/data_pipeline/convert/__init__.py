"""convert - 标注格式转换子系统

框架层（registry.py + service.py）永不增长；
加新格式 = 在 converters/ 下新增一个文件。

Public API:
    - convert_data_to_yolo: 统一转换入口
    - ConvertOptions: 转换参数包
    - available_formats, list_capabilities: 查询已注册格式
"""

from od_platform.data_pipeline.convert.service import convert_data_to_yolo
from od_platform.data_pipeline.convert.registry import (
    ConvertOptions,
    available_formats,
    list_capabilities,
)
