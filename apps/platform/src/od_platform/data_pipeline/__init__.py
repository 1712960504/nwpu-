"""data_pipeline - 数据流水线子系统

将 data/raw/ 下的原始标注转换成 YOLO 格式，划分 train/val/test，
生成可直接喂给 ultralytics 的 dataset.yaml。

子模块:
- convert: 标注格式转换（VOC / COCO / YOLO → YOLO）
"""
