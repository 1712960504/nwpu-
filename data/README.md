# data/ — 数据集目录

本目录存放 ODPlatform 的全部数据集。

## 目录结构

```
data/
├── raw/            ← 原始数据:只读,绝不就地改
│   └── <数据集名>/
│       ├── images/
│       └── annotations/
└── processed/      ← 派生数据集:含冻结后的 train/val/test
    └── <数据集名>/
```

## 使用说明

1. 将下载的数据集放到 `data/raw/<数据集名>/` 下
2. 原始数据**只读**,数据流水线会读取它并将结果写入 `data/processed/`
3. `data/raw/` 和 `data/processed/` 不进 git(见 `.gitignore`)

参考: D0 设计指南 决定 5 — 原始(只读)与派生(可再生)分家
