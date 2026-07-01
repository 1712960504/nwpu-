"""split - 数据集划分子系统

将转换后的 (image, label) 对按策略（随机 / 分层）划分为 train/val/test，
产生 SplitManifest，再由 materialize 物化到输出目录。
"""
