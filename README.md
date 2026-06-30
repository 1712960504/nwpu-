# ODPlatform — 通用目标检测开发平台

ODPlatform 是面向算法工程师与研究者的**通用目标检测开发平台**，覆盖从原始数据接入、格式转换、训练、评估、推理到工程化交付的全流程。

## 快速开始

```bash
# 1. 创建并激活环境
conda create -n odplat python=3.12
conda activate odplat

# 2. 安装平台核心引擎（可编辑模式）
pip install -e ./apps/platform

# 3. 初始化项目目录
odp-init

# 4. 将数据集放入 data/raw/<数据集名>/ 下，开始使用
```

## 项目结构

```
ODPlatform/                    ← workspace 根
├── apps/                      ← 各"端"的家
│   ├── platform/              ← 核心引擎（训练 + 推理）
│   ├── web-backend/           ← 占位：Web 后端 (V1.1)
│   └── desktop/               ← 占位：桌面客户端 (V1.1+)
├── data/                      ← 共享数据集
├── models/                    ← 共享模型权重
├── runs/                      ← 训练运行结果
├── scripts/                   ← 开发期入口脚本
├── tests/                     ← 跨端测试
└── docs/                      ← 项目文档
```

## 文档

- 架构决策记录：[docs/architecture/](docs/architecture/)
- 设计指南：参见 D0 设计文档
- 开发日志：参见 D1-D9 系列文档

## 开发

```bash
# 安装开发依赖
pip install -e "./apps/platform[dev]"

# 代码风格检查
ruff check .

# 类型检查
mypy apps/platform/src

# 运行测试
pytest
```
