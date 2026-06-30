# ODPlatform 通用工具层（common/）与项目初始化系统

# 产品需求文档（PRD）

| 文档编号 | ODP-PRD-2026-002 |
| --- | --- |
| 文档名称 | ODPlatform 通用工具层与项目初始化系统 产品需求文档 |
| 产品 / 项目 | ODPlatform（通用目标检测开发平台） |
| 所属里程碑 | V1.0 — D2 阶段 |
| 文档版本 | v1.0 |
| 文档状态 | 已评审（Approved） |
| 密级 | 内部公开 |
| 作者（Owner） | 雨霓（Platform Team） |
| 评审人 | 架构组 / QA 组 / 平台组负责人 |
| 评审日期 | 2026-05-08 |
| 生效日期 | 2026-05-08 |
| 文档语言 | 简体中文 |

---

## 修订记录（Change Log）

| 版本 | 日期 | 修订人 | 修订内容 | 评审人 |
| --- | --- | --- | --- | --- |
| v0.1 | 2026-04-22 | 雨霓 | 初稿，仅包含背景与功能列表 | — |
| v0.5 | 2026-04-29 | 雨霓 | 补充 NFR、验收标准、风险章节 | 架构组（initial） |
| v0.9 | 2026-05-05 | 雨霓 | 评审反馈修订：补充 RTM、跨平台需求、APP_DIR 设计约束 | 架构组、QA |
| **v1.0** | **2026-05-08** | **雨霓** | **正式评审通过，进入开发执行阶段** | **架构组 / QA / 平台组** |

> **变更管理说明**：本文档生效后，任何范围变更须走 CR（Change Request）流程，由 Owner 提交、架构组评审、对应 QA Lead 二次确认后方可合入主干。次要文字勘误可由 Owner 直接修订并在本表登记，不需要重新评审。

---

## 目录

1. 引言
2. 产品概述
3. 范围说明
4. 干系人与用户角色
5. 功能需求（Functional Requirements）
6. 非功能需求（Non-Functional Requirements）
7. 系统约束与设计原则
8. 验收标准与 Definition of Done
9. 项目里程碑与交付计划
10. 风险评估与应对
11. 需求追踪矩阵（RTM）
12. 附录

---

# 1. 引言

## 1.1 文档目的

本文档面向 ODPlatform 项目 D2 阶段（通用工具层 + 项目初始化系统）开发周期，给出：

- 本期需要交付的**功能边界**（做什么、不做什么）
- 各功能项的**输入、输出、处理逻辑、异常处理**
- **非功能需求**（性能、可移植性、可维护性等）
- **验收标准**与**测试覆盖要求**
- **风险与依赖**

本文档是后续设计文档（HLD/LLD）、开发任务拆解、测试用例编写的**唯一权威输入**。开发人员、测试人员、Reviewer 在出现需求理解分歧时，**以本文档为准**。

## 1.2 阅读对象

| 角色 | 阅读重点 |
| --- | --- |
| 产品负责人 / PM | 第 1–4 章（背景、范围、用户场景） |
| 架构师 | 第 5–7 章（功能、非功能、设计约束） |
| 开发工程师 | 第 5–8 章（功能详述、验收标准） |
| 测试工程师 | 第 5、6、8、11 章（功能、NFR、AC、RTM） |
| 运维 / DevOps | 第 6.5、7、9 章（部署、可移植、里程碑） |
| 新人 / 后续接手者 | 全文 |

## 1.3 术语与缩略语

| 术语 | 含义 |
| --- | --- |
| ODPlatform | 通用目标检测开发平台（本产品） |
| Monorepo | 单仓库多项目模式 |
| Workspace | 仓库根目录，统一管理多个 app/package |
| App | apps/ 下的一个独立"端"，如 platform、web-backend、desktop |
| Marker file | 工作区根标记文件（本项目为 `.odp-workspace`） |
| ROOT_DIR | 工作区根路径常量 |
| APP_DIR | 当前 app 的根路径常量 |
| Entry-point | Python 包通过 pyproject.toml 注册的命令行入口 |
| Editable install | `pip install -e .` 模式安装，源码改动即时生效 |
| CJK | 中日韩统一表意字符（Chinese / Japanese / Korean） |
| ADR | 架构决策记录（Architecture Decision Record） |
| RTM | 需求追踪矩阵（Requirements Traceability Matrix） |
| FR | 功能需求（Functional Requirement） |
| NFR | 非功能需求（Non-Functional Requirement） |
| AC | 验收标准（Acceptance Criteria） |
| DoD | 完成定义（Definition of Done） |
| CI | 持续集成（Continuous Integration） |
| MTTR | 平均故障恢复时间 |

## 1.4 参考文档

| 编号 | 文档 | 关系 |
| --- | --- | --- |
| REF-01 | 《ODPlatform 目录设计推导讲义》（D1） | 上游输入：本期落地的目录结构来源 |
| REF-02 | 《ODPlatform D2 common/ 层的诞生》开发文档 | 同期：实现细节与教学叙事 |
| REF-03 | ADR-001 采用 Monorepo + apps/ 布局 | 架构决策依据 |
| REF-04 | PEP 517 / PEP 518 / PEP 621 | Python 打包标准 |
| REF-05 | PyPA "src/ layout" 推荐 | 包目录布局规范 |
| REF-06 | Conventional Commits 1.0.0 | git commit 规范 |
| REF-07 | Semantic Versioning 2.0.0 | 版本号规范 |
| REF-08 | 公司《Python 开发规范 v3.2》 | 内部编码规范 |
| REF-09 | 公司《代码评审指南 v2.0》 | Code Review 流程 |

---

# 2. 产品概述

## 2.1 产品定位

ODPlatform 是面向算法工程师与研究者的**通用目标检测开发平台**，覆盖从原始数据接入、格式转换、训练、评估、推理到工程化交付的全流程。本期交付物（D2 阶段）是平台**最底层的工程基础设施**——通用工具层（common/）与项目初始化系统。

## 2.2 业务背景与问题陈述

D1 阶段已完成 ODPlatform 的 Monorepo 目录架构设计（约 19 个目录的 workspace 树）。但目前该结构**仅停留在文档层面**，存在以下落地痛点：

1. **新成员上手摩擦大**：克隆仓库后需手动按文档创建运行时目录，易遗漏、易出错；30 人规模团队反复出现"目录不存在导致脚本崩溃"的问题。
2. **路径管理混乱**：现有原型代码中的目录路径以硬编码字符串散落各处，重构时改动成本高，且对 cwd 敏感（不同目录执行结果不同）。
3. **可观测性缺失**：现有脚本以 `print` 输出运行信息，无时间戳、无级别、无落盘、无颜色，问题排查极度依赖人工记忆。
4. **复现性差**：训练 / 推理日志中缺乏环境快照（OS、Python、PyTorch、GPU 等），三个月后无法复现实验结果。
5. **多端预留不足**：当前结构仅支持 platform 一个端，未来扩展 web-backend / desktop 时，端私有资源（日志、配置）的隔离机制不到位。
6. **工程化程度不足**：没有 `pyproject.toml`、没有 CLI 入口注册，安装与发布流程不清晰，与公司其他成熟项目的工程标准存在差距。

## 2.3 产品目标（Product Goals）

D2 阶段需达成下列业务与工程目标：

| 编号 | 目标 | 衡量指标 |
| --- | --- | --- |
| G1 | **零摩擦初始化**：新成员克隆仓库后，单条命令完成所有运行时环境搭建 | 从 `git clone` 到首次跑通耗时 ≤ 5 分钟 |
| G2 | **路径治理收口**：消除业务代码中的硬编码路径 | 业务代码 `git grep` 不出现裸字符串路径常量 |
| G3 | **结构化可观测**：所有运行时输出统一通过日志层 | 关键脚本 0 处 `print()`；日志文件 100% 可归档 |
| G4 | **可复现性保障**：每次重要操作输出环境快照 | 训练 / 推理日志含完整 OS/Py/Torch/GPU 信息 |
| G5 | **多端架构落地**：共享资产与端私有资产物理隔离 | 路径常量明确区分 ROOT_DIR / APP_DIR |
| G6 | **工程化交付**：符合 PyPA 标准的可安装 Python 包 | `pip install -e ./apps/platform` 一次成功 |
| G7 | **跨平台兼容**：Windows / macOS / Linux 三端开发体验一致 | 三端均可完整跑通验收用例 |

## 2.4 非目标（Non-Goals）

为避免范围蔓延，以下事项**明确不属于** D2 阶段交付内容：

- 配置管理系统（Pydantic schema、三源合并）→ **D3-D4 阶段**
- 数据格式转换（VOC/COCO → YOLO）→ **D5 阶段**
- 训练 / 评估 / 推理子系统 → **D7-D9 阶段**
- web-backend / web-frontend / desktop 任何实现代码 → **V1.1+**
- 跨端 E2E 自动化测试 → **V1.1+**
- 模型存储后端（MinIO / S3 等远程存储）→ **后续版本**
- CI/CD 流水线接入 → 由 DevOps 团队在 V1.0 GA 阶段统一对接

## 2.5 产品价值

| 维度 | 价值 |
| --- | --- |
| **效率** | 节省每位新成员 1–3 小时的环境搭建调试时间；30 人团队累计节省 ≥ 60 工时 |
| **质量** | 通过环境快照与结构化日志，实验复现成功率从约 60% 提升至 ≥ 95% |
| **可扩展性** | 为 V1.1 多端架构（web-backend / desktop）提供可直接复用的基础设施，新端接入预估节省 5–8 人天 |
| **工程文化** | 输出 ADR、commit 规范、占位 README 等工程产物，作为团队工程实践范本 |

---

# 3. 范围说明

## 3.1 本期交付范围（In Scope）

### 3.1.1 代码模块

| 模块 | 路径 | 说明 |
| --- | --- | --- |
| 路径管理 | `apps/platform/src/od_platform/common/paths.py` | 集中式路径常量与工作区根定位 |
| 日志工具 | `apps/platform/src/od_platform/common/logging_utils.py` | 双端（控制台 + 文件）日志，彩色，CJK 友好 |
| 字符串工具 | `apps/platform/src/od_platform/common/string_utils.py` | CJK 字符宽度感知，表格对齐 |
| 系统信息工具 | `apps/platform/src/od_platform/common/system_utils.py` | 环境快照（OS、Python、PyTorch、CPU、GPU、内存） |
| 性能工具 | `apps/platform/src/od_platform/common/performance_utils.py` | `@time_it` 装饰器，自动单位切换 |
| 项目初始化 CLI | `apps/platform/src/od_platform/cli/init_project.py` | 集成上述工具的项目初始化入口 |
| 开发期入口 | `scripts/init_project.py` | 不依赖 pip install 的开发期调用入口 |

### 3.1.2 工程化产物

| 产物 | 路径 | 说明 |
| --- | --- | --- |
| 子项目配置 | `apps/platform/pyproject.toml` | platform 端的依赖与 entry-point |
| 工作区配置 | `pyproject.toml` | workspace 级开发工具（ruff/mypy/pytest）配置 |
| 工作区标记 | `.odp-workspace` | marker file |
| 忽略规则 | `.gitignore` | 涵盖 Python / 虚拟环境 / IDE / 数据 / 模型等 |

### 3.1.3 文档产物

| 产物 | 路径 | 说明 |
| --- | --- | --- |
| 架构决策 | `docs/architecture/ADR-001-monorepo.md` | Monorepo 决策记录 |
| 端 README | `apps/platform/README.md` | platform 端使用说明 |
| 占位 README | `apps/{web-backend, web-frontend, desktop}/README.md` 等 | 为未来端预留架构位 |
| 数据/模型 README | `data/README.md`、`models/*/README.md`、`runs/README.md` | 共享资产说明 |

### 3.1.4 CLI 命令

- `odp-init`（pip install 后注册的 console_script）

## 3.2 不在范围内（Out of Scope）

明确**不**在本期交付：

| 事项 | 原因 / 后续计划 |
| --- | --- |
| 配置管理 / Pydantic schema | D3-D4 单独立项 |
| 业务子系统（数据转换 / 训练 / 推理 / 评估） | D5-D9 各自立项 |
| `odp-reset` 反向清理命令 | 已规划至 D2.5 单独交付 |
| 单元测试 / 集成测试代码 | 测试代码补全在 D2.5 阶段（与 reset 同期） |
| 多端代码（web-backend 等）的实际功能 | V1.1+ 启动；本期只创建占位目录与 README |
| Docker / 容器化 | DevOps 在 V1.0 GA 阶段统一处理 |
| 公网发布到 PyPI | 暂不发布；仅内网使用 |

## 3.3 上下游依赖

```
┌─────────────────────┐
│ D1: 目录架构设计    │  ← 上游输入（已完成）
│ ADR-001 (Monorepo)  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ D2 (本期)            │
│ common/ + init      │
└──────────┬──────────┘
           ▼
   ┌───────┴───────────┬─────────────┬─────────────┐
   ▼                   ▼             ▼             ▼
┌──────┐         ┌──────────┐  ┌──────────┐  ┌──────────┐
│ D2.5 │         │ D3-D4    │  │ D5-D9    │  │ V1.1+    │
│ reset│         │ config   │  │ 业务子系统│  │ 多端     │
└──────┘         └──────────┘  └──────────┘  └──────────┘
```

**外部依赖**：

| 依赖 | 类型 | 版本 | 备注 |
| --- | --- | --- | --- |
| Python | 运行时 | ≥ 3.10 | pyproject.toml 强制声明 |
| colorlog | 业务依赖 | ≥ 6.7.0 | 彩色控制台日志 |
| psutil | 软依赖 | ≥ 5.9.0 | 内存信息（缺失时降级显示） |
| torch | 业务依赖 | ≥ 2.0.0 | 用于 GPU 信息查询 |
| ultralytics | 业务依赖 | ≥ 8.0.0 | 项目核心引擎依赖 |
| pyyaml | 业务依赖 | ≥ 6.0 | 后续阶段使用，提前声明 |
| pydantic | 业务依赖 | ≥ 2.0 | D3-D4 使用，提前声明 |

**开发依赖**：ruff ≥ 0.1.0、mypy ≥ 1.5.0、pytest ≥ 7.4.0、pytest-cov ≥ 4.1.0、pre-commit ≥ 3.4.0。

---

# 4. 干系人与用户角色

## 4.1 项目干系人（RACI 矩阵简版）

| 干系人 | 职责 | R | A | C | I |
| --- | --- | :-: | :-: | :-: | :-: |
| 产品 Owner（雨霓） | 需求定义、文档维护、范围把控 | ● | ● | | |
| 架构组 | 技术方案评审、ADR 审定 | | ● | ● | |
| 开发工程师 | 编码实现 | ● | | ● | |
| QA 工程师 | 测试用例设计、验收测试 | ● | | ● | ● |
| Code Reviewer（资深工程师） | 代码评审 | | | ● | |
| 平台 / DevOps | 环境支持、CI 接入咨询 | | | ● | ● |
| 终端用户（算法工程师） | 试用反馈 | | | | ● |

> R = Responsible（实施方），A = Accountable（最终负责），C = Consulted（被咨询），I = Informed（被告知）

## 4.2 用户角色（User Personas）

### 角色 A：算法工程师（核心用户）

- **背景**：3–5 年深度学习经验，熟悉 PyTorch/YOLO，关注模型效果。
- **关注点**：能否快速跑通流程；命令是否简洁；日志是否清晰可追溯。
- **痛点**：跨机器复现训练结果困难；脚本运行报错信息不足；环境配置散乱。

### 角色 B：研究员 / 实习生（次要用户）

- **背景**：刚入职，Python 与命令行经验有限。
- **关注点**：上手成本；文档清晰度；错误提示是否友好。
- **痛点**：克隆仓库后不知道下一步；目录用途不明；环境搭建容易卡住。

### 角色 C：平台维护者 / 架构师

- **背景**：负责平台演进、跨端协作、技术债务管理。
- **关注点**：可扩展性；重构成本；与多端架构的兼容性。
- **痛点**：路径硬编码导致重构困难；缺少架构决策记录。

## 4.3 典型使用场景（User Story）

### US-01 新成员首次上手

> **作为**新加入团队的算法工程师，**我希望**克隆仓库后通过单条命令完成所有运行时目录的创建与环境检查，**以便**在 5 分钟内开始第一次训练实验。

**主流程**：

1. `git clone <repo> && cd ODPlatform`
2. `conda create -n odp python=3.10 && conda activate odp`
3. `pip install -e ./apps/platform`
4. `odp-init`
5. 查看输出的环境快照与目录创建结果，确认 OK
6. 将数据集放入 `data/raw/<dataset_name>/`
7. 进入下一阶段

**预期成果**：所有 15 个运行时目录建出；环境信息完整记录于日志文件；存在数据集时给出明确路径反馈，缺失时给出明确指引。

### US-02 多机环境复现实验

> **作为**算法工程师，**我希望**每次运行 `odp-init` 都自动记录当前机器的完整环境信息（OS、Python、PyTorch、GPU 等），**以便**未来在另一台机器上能快速比对环境差异并定位问题。

**预期成果**：日志文件落盘至 `apps/platform/logging/init_project/init-project_<时间戳>.log`，含可机读的环境信息；可通过 diff 工具比较两次运行的环境差异。

### US-03 工程师重构 common 模块

> **作为**平台维护者，**我希望**调整 `paths.py` 的物理位置（如从 `common/` 上移一层）后无需修改 `paths.py` 内部任何代码，**以便**降低未来架构调整的成本。

**预期成果**：通过 marker file 模式，paths.py 在仓库内任意层级移动后仍能正确解析 ROOT_DIR。

### US-04 跨平台开发协作

> **作为**使用 Windows 的开发者，**我希望**与 Linux/macOS 同事使用同一份代码库时不会遇到平台相关的路径或编码问题，**以便**专注于业务逻辑。

**预期成果**：所有路径运算使用 `pathlib.Path`；日志、配置文件统一 UTF-8 编码；CLI 命令在三端表现一致。


---

# 5. 功能需求（Functional Requirements）

## 5.1 需求编号规则

需求编号格式：`FR-<模块代号>-<序号>`

| 模块代号 | 模块 |
| --- | --- |
| PATH | 路径管理 |
| LOG | 日志工具 |
| STR | 字符串工具 |
| SYS | 系统信息工具 |
| PERF | 性能工具 |
| INIT | 项目初始化 |
| PKG | 工程化打包 |
| DOC | 文档产物 |

每条需求按以下结构描述：

- **需求 ID** + **优先级**（P0 必须 / P1 重要 / P2 期望）
- **关联用户故事**
- **需求描述**
- **输入 / 输出**
- **处理规则**
- **异常处理**
- **验收标准**

---

## 5.2 路径管理模块（paths.py）

### FR-PATH-001 工作区根目录定位 [P0]

- **关联场景**：US-03、US-04
- **需求描述**：系统应通过 marker file（`.odp-workspace`）模式从当前文件位置向上递归查找仓库根目录，并将其暴露为 `ROOT_DIR` 常量（`pathlib.Path` 类型）。
- **输入**：模块加载时自动以 `Path(__file__)` 为起点。
- **输出**：`ROOT_DIR: Path`，绝对路径。
- **处理规则**：
  1. 从起始路径所在目录开始，依次检查当前目录及其所有父目录是否存在 `.odp-workspace` 文件。
  2. 找到第一个匹配目录即为 `ROOT_DIR`。
  3. 解析过程仅在模块导入时执行一次，结果缓存为模块级常量。
- **异常处理**：
  - 一直追溯到文件系统根仍未找到 marker → 抛出 `FileNotFoundError`，错误信息须明确提示"请在仓库根创建 `.odp-workspace`"。
- **验收标准**：
  - AC-1：在标准目录结构下，`ROOT_DIR` 解析为仓库根绝对路径。
  - AC-2：删除仓库根 `.odp-workspace` 后导入模块，抛出 `FileNotFoundError`，且错误信息包含文件名。
  - AC-3：将 paths.py 物理位置上移或下移一层，重新导入仍能正确解析 `ROOT_DIR`。

### FR-PATH-002 端根目录定义（APP_DIR）[P0]

- **关联场景**：US-03（多端架构预留）
- **需求描述**：系统应定义 `APP_DIR` 常量，表示当前 paths.py 所属端的根目录。本期取值 `ROOT_DIR / "apps" / "platform"`。
- **设计约束**：APP_DIR 取值不得依赖文件解析（即不能基于 `__file__` 反推），必须显式书写当前所属端，以保持模块语义清晰。
- **输出**：`APP_DIR: Path`。
- **验收标准**：
  - AC-1：`APP_DIR` 值等于 `ROOT_DIR / "apps" / "platform"`。
  - AC-2：未来添加 web-backend 端时，其各自的 paths.py 内 `APP_DIR` 应独立设定为对应端目录，互不冲突（设计可扩展性约束）。

### FR-PATH-003 路径常量集中定义 [P0]

- **关联场景**：US-01、US-03
- **需求描述**：系统应集中定义全部业务路径常量，按"共享资产"与"端私有资产"两类组织。
- **路径常量列表**：

| 常量 | 类别 | 取值 |
| --- | --- | --- |
| `DATA_DIR` | 共享 | `ROOT_DIR / "data"` |
| `MODELS_DIR` | 共享 | `ROOT_DIR / "models"` |
| `RUNS_DIR` | 共享 | `ROOT_DIR / "runs"` |
| `PRETRAINED_MODELS_DIR` | 共享（子级） | `MODELS_DIR / "pretrained"` |
| `CHECKPOINTS_DIR` | 共享（子级） | `MODELS_DIR / "checkpoints"` |
| `RAW_DATA_DIR` | 共享（子级） | `DATA_DIR / "raw"` |
| `YOLO_STAGED_LABELS_DIR` | 共享（子级） | `RAW_DATA_DIR / "yolo_staged_labels"` |
| `TRAIN_DIR` / `VAL_DIR` / `TEST_DIR` | 共享（子级） | `DATA_DIR / {train,val,test}` |
| `TRAIN_IMAGES_DIR` 等（共 6 个） | 共享（子级） | 对应 `images/`、`annotations/` |
| `CONFIGS_DIR` | 端私有 | `APP_DIR / "configs"` |
| `LOGGING_DIR` | 端私有 | `APP_DIR / "logging"` |
| `UNIT_TEST_DIR` | 端私有 | `APP_DIR / "tests"` |
| `DOCS_DIR` | 工程基础设施 | `ROOT_DIR / "docs"` |
| `SCRIPTS_DIR` | 工程基础设施 | `ROOT_DIR / "scripts"` |

- **设计约束**：
  - 所有常量类型必须显式标注 `Path`。
  - 模块禁止执行任何 I/O 操作（如 `mkdir`、文件读写）；本模块仅做"定义"。
  - 模块禁止依赖业务模块（避免循环依赖）。

### FR-PATH-004 待初始化目录列表函数 [P0]

- **关联场景**：US-01
- **需求描述**：提供 `get_dirs_to_initialize() -> List[Path]` 函数，返回全部需在初始化阶段创建的运行时目录列表。
- **返回值**：包含 15 个目录的 `List[Path]`（具体清单见 5.6 节 init_project 的输入说明）。
- **设计约束**：
  - 该函数是 init_project 模块的**唯一目录数据源**（Single Source of Truth）。
  - 列表内不应包含 git-tracked 的代码 / 文档目录。
- **验收标准**：
  - AC-1：调用返回值类型为 `List[Path]`。
  - AC-2：列表数量为 15（含子目录）；具体清单如下：data, runs, models, models/pretrained, models/checkpoints, data/raw, data/raw/yolo_staged_labels, data/train/images, data/train/annotations, data/val/images, data/val/annotations, data/test/images, data/test/annotations, apps/platform/configs, apps/platform/logging, apps/platform/tests, scripts, docs（共 18 个待初始化路径，去除已通过代码 / 占位 README 进入 git 的目录后实际新建数视环境而定）。
  - AC-3：未来若需调整目录范围，**仅需**修改本函数，不修改任何调用方。

> **设计说明**：FR-PATH-004 的 AC-2 数字与开发文档中"15 个 / 17 个 / 18 个"等不同表述存在混淆，本 PRD 以 `get_dirs_to_initialize()` 实际返回的列表长度为准；开发期由 QA 编写自动化用例对该数字进行断言，避免文档与实现漂移。

---

## 5.3 日志工具模块（logging_utils.py）

### FR-LOG-001 统一日志获取入口 [P0]

- **关联场景**：US-01、US-02
- **需求描述**：提供 `get_logger(...)` 函数，返回配置完成的 `logging.Logger` 实例，同时输出至控制台与文件。
- **输入参数**：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `base_path` | `Path` | 无默认（必填） | 日志根目录，通常传入 `paths.LOGGING_DIR` |
| `log_type` | `str` | `"general"` | 日志类型，决定子目录名与文件名前缀 |
| `model_name` | `str \| None` | `None` | 模型名（用于训练等场景），影响文件名 |
| `log_level` | `int` | `logging.INFO` | 日志级别 |
| `temp_log` | `bool` | `False` | 是否标记为临时日志（影响文件名前缀） |
| `encoding` | `str` | `"utf-8"` | 文件编码 |
| `logger_name` | `str` | `"ODPlatform"` | logger 实例名 |

- **输出**：配置完毕的 `logging.Logger` 实例。
- **处理规则**：
  1. 通过 `logging.getLogger(logger_name)` 获取命名 logger。
  2. 若该 logger 已有 handlers，直接返回（防止重复配置）。
  3. 设置 `logger.propagate = False`，避免污染 root logger。
  4. 在 `base_path / log_type / ` 下生成日志文件，文件名格式：`<prefix>_<timestamp>[_<safe_model_name>].log`。
     - `prefix`：`temp_log=True` 时为 `"temp"`；否则为 `log_type` 中 `_` 替换为 `-`。
     - `timestamp`：`YYYYMMDD-HHMMSS-fff` 格式（毫秒精度）。
     - `safe_model_name`：仅保留字母 / 数字 / `_` / `-`，其余字符替换为 `_`。
  5. 配置 **文件 Handler**：详细格式（含文件名、行号、函数名）。
  6. 配置 **控制台 Handler**：彩色（colorlog），紧凑格式。
- **验收标准**：
  - AC-1：同一 `logger_name` 重复调用 `get_logger`，返回同一实例，handler 数不重复增长。
  - AC-2：日志文件按指定路径生成，UTF-8 编码可读。
  - AC-3：控制台输出彩色（DEBUG=白 / INFO=绿 / WARNING=黄 / ERROR=红 / CRITICAL=红底）。
  - AC-4：文件输出包含完整时间戳、级别、文件名、行号、函数名、消息；不含 ANSI 颜色码。

### FR-LOG-002 启动信息打印 [P1]

- **需求描述**：logger 创建完毕后自动输出一段启动信息，包括：日志文件路径、运行环境（OS）、阶段类型、日志级别、模型名（若有）。
- **验收标准**：
  - AC-1：每次新建 logger 时输出至少 7 行启动信息（含分隔符）。
  - AC-2：信息中"日志文件"字段为绝对路径。

### FR-LOG-003 端私有日志位置约束 [P0]

- **需求描述**：默认 `base_path` 必须传入 `paths.LOGGING_DIR`（即 `APP_DIR / "logging"`）；不得使用 `ROOT_DIR / "logging"`。
- **设计依据**：日志为端私有资产，不同端日志格式不一致，集中存放会造成混乱。
- **验收标准**：Code Review 时检查所有 `get_logger` 调用，`base_path` 参数必须来源于 `paths` 模块的端私有路径常量。

---

## 5.4 字符串工具模块（string_utils.py）

### FR-STR-001 显示宽度计算 [P0]

- **关联场景**：US-01、US-02（日志表格对齐）
- **需求描述**：提供 `get_display_width(text: str) -> int` 函数，计算字符串在等宽字体终端中的实际显示宽度（CJK 字符算 2，其余算 1）。
- **覆盖字符范围**：
  - 中日韩统一表意文字（U+4E00 – U+9FFF）→ 宽度 2
  - 中日韩标点符号（U+3000 – U+303F）→ 宽度 2
  - 全角字符（U+FF00 – U+FFEF）→ 宽度 2
  - 中日韩扩展 A（U+3400 – U+4DBF）→ 宽度 2
  - 平假名（U+3040 – U+309F）→ 宽度 2
  - 片假名（U+30A0 – U+30FF）→ 宽度 2
  - 韩文音节（U+AC00 – U+D7AF）→ 宽度 2
  - 其余（含 ASCII）→ 宽度 1
- **验收标准**：
  - AC-1：`get_display_width("hello") == 5`
  - AC-2：`get_display_width("你好") == 4`
  - AC-3：`get_display_width("hi你好") == 6`
  - AC-4：`get_display_width("") == 0`

### FR-STR-002 宽度感知填充 [P0]

- **需求描述**：提供 `pad_to_width(text: str, width: int, align: str = 'left') -> str` 函数，按显示宽度对字符串进行填充。
- **行为规范**：
  - `align="left"`：右侧补空格
  - `align="right"`：左侧补空格
  - `align="center"`：两侧均匀补空格（左侧 ≤ 右侧时左侧少 1 格）
  - 若字符串当前显示宽度 ≥ 目标宽度，原样返回（不截断）
- **验收标准**：
  - AC-1：`pad_to_width("你好", 10)` 返回长度满足显示宽度为 10。
  - AC-2：填充后字符串与目标宽度等长字符串拼接，终端可视对齐。

### FR-STR-003 表格格式化辅助函数 [P1]

- **需求描述**：提供：
  - `format_table_row(columns: list, widths: list, aligns: list = None) -> str`
  - `format_table_separator(widths: list, char: str = '-') -> str`
- **行为规范**：
  - `format_table_row`：列数 / 宽度 / 对齐数必须三者一致，否则抛 `AssertionError`。默认对齐方式为左对齐。
  - `format_table_separator`：返回长度 = `sum(widths) + len(widths) - 1` 的字符序列，等同于一行表格的总显示宽度。
- **验收标准**：表头与数据行连续打印时，分隔线长度与表格总宽度一致。

---

## 5.5 系统信息工具模块（system_utils.py）

### FR-SYS-001 环境信息采集 [P0]

- **关联场景**：US-02
- **需求描述**：提供 `get_basic_device_info() -> dict` 函数，采集并返回结构化的环境信息字典。
- **采集内容**（按四类组织）：

| 类别 | 字段 |
| --- | --- |
| 系统信息 | 操作系统（含版本与架构）、主机名、Python 版本、PyTorch 版本、Ultralytics 版本、当前时间 |
| CPU 信息 | CPU 型号、核心数 |
| 内存信息 | 总内存、可用内存、使用率 |
| GPU 信息 | CUDA 可用性、GPU 数量、各 GPU 型号、各 GPU 显存 |

- **依赖处理**：
  - `psutil` 必须作为**软依赖**：未安装时，内存信息字段降级为 `"Unknown (psutil 未安装)"`，**不得**抛异常。
  - `torch`、`ultralytics` 当前作为业务依赖在 `pyproject.toml` 中声明（`torch>=2.0.0`、`ultralytics>=8.0.0`）；若未来调整为可选，须同步更新本函数为软依赖处理。
- **设计约束**：CPU 核心数应使用 `os.cpu_count()`（需独立 `import os`），不得使用 `platform.os.cpu_count()` 等非公开 API（避免不同 Python 实现下行为差异）。
- **验收标准**：
  - AC-1：返回 dict 包含 4 个顶层 key（系统信息 / CPU 信息 / 内存信息 / GPU 信息）。
  - AC-2：CUDA 可用时输出每张 GPU 的型号与显存（GB 单位）。
  - AC-3：psutil 未安装时函数仍能返回完整 dict，仅内存字段为降级值。

### FR-SYS-002 环境信息打印 [P0]

- **需求描述**：提供 `log_device_info(logger: Optional[Logger] = None) -> dict` 函数，将环境信息按类别格式化输出到 logger，并返回原始字典。
- **格式要求**：
  - 使用 `string_utils.pad_to_width` 实现键名对齐。
  - 各类别用居中标题分隔，整体宽度 60。
- **验收标准**：
  - AC-1：未传 logger 时使用模块默认 logger。
  - AC-2：输出中中英文键名（如"操作系统"、"Python版本"）严格对齐。

### FR-SYS-003 字节单位格式化 [P2]

- **需求描述**：内部辅助函数 `_format_size(bytes_size)`，自动选择 KB / MB / GB。
- **验收标准**：> 1GB 输出 GB；1MB–1GB 输出 MB；< 1MB 输出 KB；`None` 或非数值输入返回 `"N/A"`。

---

## 5.6 性能工具模块（performance_utils.py）

### FR-PERF-001 通用计时装饰器 [P0]

- **需求描述**：提供 `time_it(iterations=1, name=None, logger_instance=None)` 装饰器工厂，对被装饰函数自动计时并通过 logger 输出耗时。
- **参数行为**：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `iterations` | `int` | 1 | 执行次数；> 1 时取平均并同时输出总耗时 |
| `name` | `str \| None` | None | 显示名；`None` 时使用 `func.__name__` |
| `logger_instance` | `Logger \| None` | None | 自定义 logger；`None` 时使用模块级默认 logger |

- **行为规则**：
  - 使用 `time.perf_counter()` 计时（高精度）。
  - 自动单位选择：< 1ms → 微秒；< 1s → 毫秒；< 60s → 秒；< 1h → 分钟+秒；≥ 1h → 小时+分钟+秒。
  - 必须使用 `functools.wraps` 保留被装饰函数的元信息。
  - **不得**修改被装饰函数的返回值或异常传播行为。
- **验收标准**：
  - AC-1：被装饰函数返回值原样透传。
  - AC-2：被装饰函数抛异常时，装饰器**不**吞异常（异常向外传播），但本次计时不输出（与"失败计时无意义"约定一致）。
  - AC-3：`iterations=10` 时输出格式为 `"... 执行 10 次 | 总耗时: X | 平均耗时: Y"`。
  - AC-4：单位切换边界值（如 0.999s、1s、59.999s、60s）输出格式正确。

---

## 5.7 项目初始化模块（init_project.py）

### FR-INIT-001 主初始化入口 [P0]

- **关联场景**：US-01、US-02
- **需求描述**：提供 `initialize_project()` 函数，作为整套初始化流程的入口。
- **执行步骤**：
  1. 打印阶段标题（使用 `LINE_WIDTH = 60` 居中）。
  2. 输出项目根目录路径。
  3. 调用 `system_utils.log_device_info(logger=logger)` 打印环境快照。
  4. 遍历 `paths.get_dirs_to_initialize()`，逐个 mkdir：
     - 已存在：记录 INFO 日志"目录已存在: <relative_path>"。
     - 不存在：`mkdir(parents=True, exist_ok=True)` 后记录"成功创建: <relative_path>"。
     - 失败：记录 ERROR 日志，**fail-fast 退出**（`raise SystemExit(1)`）。
  5. 检查 `RAW_DATA_DIR` 状态（见 FR-INIT-002）。
  6. 输出对齐的汇总表格（使用 `string_utils.format_table_row`）。
  7. 输出"下一步指引"提示。
- **装饰器**：使用 `@time_it(iterations=1, name="项目初始化", logger_instance=logger)` 自动统计总耗时。

### FR-INIT-002 原始数据目录状态检查 [P0]

- **需求描述**：检查 `paths.RAW_DATA_DIR` 状态并给出明确反馈。
- **三种状态及响应**：

| 状态 | 响应 |
| --- | --- |
| 不存在 | WARNING 日志，提示用户创建并放入"以数据集名称命名的子文件夹（含 images/ 与 annotations/）" |
| 存在但为空 | WARNING 日志，提示用户放入至少一个数据集，并展示预期子结构 |
| 存在且包含子目录 | INFO 日志，列出全部子文件夹名称 |

- **验收标准**：三种状态均能正确识别并输出对应日志。

### FR-INIT-003 幂等性 [P0]

- **需求描述**：重复调用 `initialize_project()` 必须产生一致结果，已存在目录不重复创建、不报错。
- **验收标准**：连续调用两次，第二次的"已存在"目录数 ≥ 第一次"已创建 + 已存在"之和。

### FR-INIT-004 失败处理（fail-fast）[P0]

- **需求描述**：任何目录创建失败（如权限不足、磁盘满）必须立即终止程序，**禁止**部分初始化。
- **退出码**：失败时进程退出码 = 1。
- **理由**：部分初始化是难以下游推理的"模糊状态"。

### FR-INIT-005 开发期入口脚本 [P1]

- **需求描述**：在仓库根 `scripts/init_project.py` 提供开发期入口，使开发者**无需** `pip install` 即可运行。
- **实现要点**：
  - 通过 `Path(__file__).resolve().parent.parent` 定位仓库根。
  - 将 `apps/platform/src` 注入 `sys.path[0]`。
  - 导入并调用 `od_platform.cli.init_project.initialize_project`。
- **验收标准**：未安装包的全新环境下，`python scripts/init_project.py` 能正常运行。

### FR-INIT-006 三种调用方式并存 [P1]

| 方式 | 命令 | 适用场景 |
| --- | --- | --- |
| 1. Console script | `odp-init` | 安装后；推荐生产 |
| 2. 模块路径 | `python -m od_platform.cli.init_project` | 已安装；临时调试 |
| 3. 仓库根脚本 | `python scripts/init_project.py` | 未安装；新人首次试跑、CI |

- **验收标准**：三种方式产出相同。

---

## 5.8 工程化打包（pyproject.toml）

### FR-PKG-001 子项目配置 [P0]

- **路径**：`apps/platform/pyproject.toml`
- **需求描述**：定义 platform 子项目的元信息、依赖、构建后端、入口注册。
- **必备字段**：

| 字段 | 取值约束 |
| --- | --- |
| `[build-system]` requires | `setuptools>=61.0`、`wheel` |
| `[build-system]` build-backend | `setuptools.build_meta` |
| `[project] name` | `"odp-platform"` |
| `[project] version` | 动态读取自 `_version.py`（`dynamic = ["version"]`） |
| `[project] requires-python` | `">=3.10"` |
| `[project] dependencies` | 见 3.3 节外部依赖列表 |
| `[project.optional-dependencies] dev` | `pytest`、`pytest-cov`、`ruff`、`mypy` |
| `[project.scripts] odp-init` | `"od_platform.cli.init_project:initialize_project"` |
| `[tool.setuptools] package-dir` | `{ "" = "src" }` |

- **设计约束**：
  - 版本号**单一来源**：仅定义于 `_version.py`，pyproject.toml 通过 `attr` 动态读取。
  - 不允许在源码中硬编码版本号字符串。

### FR-PKG-002 工作区配置 [P1]

- **路径**：`pyproject.toml`（仓库根）
- **需求描述**：定义跨 app 共享的开发工具配置。
- **覆盖工具**：
  - **ruff**：line-length=100，target=py310，启用 E/W/F/I/B/C4/UP，known-first-party=od_platform。
  - **mypy**：python_version=3.10，warn_return_any，no_implicit_optional；对 colorlog/psutil/ultralytics/torch 忽略 missing imports。
  - **pytest**：testpaths 含 apps/platform/tests 与 tests/；定义 unit/integration/slow 三个 marker。
- **设计约束**：业务依赖**只**写在子项目 pyproject.toml；工作区 pyproject.toml 不含业务依赖。

### FR-PKG-003 可安装性验证 [P0]

- **验收命令**：
  ```bash
  pip install -e ./apps/platform
  python -c "import od_platform; print(od_platform.__version__)"
  odp-init --help     # 或直接 odp-init
  ```
- **验收标准**：
  - AC-1：`pip install -e` 一次成功，无 deprecation 警告以外的错误。
  - AC-2：导入包成功，版本号与 `_version.py` 一致。
  - AC-3：`odp-init` 命令可在 PATH 中找到并正常调用。

---

## 5.9 文档与版本控制产物

### FR-DOC-001 .gitignore 规则 [P0]

- **路径**：仓库根 `.gitignore`
- **必备覆盖项**：Python 缓存与构建产物（`__pycache__/`、`*.egg-info/` 等）、虚拟环境（`venv/`、`.venv/`、`env/`）、IDE 配置（`.idea/`、`.vscode/`）、操作系统文件（`.DS_Store`、`Thumbs.db`）、测试缓存（`.pytest_cache/`、`.coverage`）、ODPlatform 专属（`data/raw/`、`models/*/*.pt`、`runs/*`、`apps/*/logging/`、`*.log`、`*.pkl`、`*.h5`、`*.npz`）。
- **白名单规则**：保留 `data/README.md`、`runs/README.md`、`models/*/README.md` 等（通过 `!` 规则覆盖）。

### FR-DOC-002 占位 README [P1]

- **覆盖目录**：`apps/{platform, web-backend, web-frontend, desktop}`、`packages/shared-schemas`、`tests/e2e`、`data`、`models/{pretrained, checkpoints}`、`runs`、`docs/architecture`。
- **每份 README 必备字段**：当前状态（`Active` / `Placeholder`）、用途说明、未来计划、参考链接（如有）。

### FR-DOC-003 ADR-001 架构决策记录 [P0]

- **路径**：`docs/architecture/ADR-001-monorepo.md`
- **必备章节**：状态、决策日期、背景、备选方案、决定、理由、后果（正面/负面/中性）、撤销条件、参考资料。
- **设计意图**：为半年后的接手者保留"为什么这么做"的化石记录。

### FR-DOC-004 Conventional Commits 规范 [P1]

- **要求**：本期所有 git commit 必须符合 Conventional Commits 1.0.0 规范，前缀使用 `feat`、`fix`、`chore`、`refactor`、`docs`、`test`、`style`。
- **目标 commit 数**：约 11 次（参见开发文档"git commit 历史预告"）。
- **commit message body**：对引入新概念或重要决策的 commit，body 须解释"为什么这么做"。

---

# 6. 非功能需求（Non-Functional Requirements）

## 6.1 性能需求（Performance）

| 编号 | 需求 | 指标 | 测量方法 |
| --- | --- | --- | --- |
| NFR-PERF-001 | `odp-init` 全流程总耗时（不含首次依赖安装） | ≤ 3 秒（typical 硬件） | `@time_it` 装饰器自报 |
| NFR-PERF-002 | `paths.py` 模块导入耗时 | ≤ 50 毫秒 | pytest benchmark |
| NFR-PERF-003 | `get_logger` 首次调用耗时 | ≤ 200 毫秒 | pytest benchmark |
| NFR-PERF-004 | `string_utils.get_display_width` 单字符调用 | ≤ 1 微秒（O(1)） | pytest benchmark |
| NFR-PERF-005 | `system_utils.get_basic_device_info` | ≤ 1 秒 | `@time_it` |

> typical 硬件参考：Intel i5 / AMD Ryzen 5 同档 CPU，16GB 内存，SSD 存储。

## 6.2 可移植性（Portability）

| 编号 | 需求 |
| --- | --- |
| NFR-PORT-001 | 支持 Linux（Ubuntu 20.04+ / CentOS 7+）、macOS（12+）、Windows 10/11 |
| NFR-PORT-002 | 所有路径运算必须使用 `pathlib.Path`，禁止裸字符串拼接路径 |
| NFR-PORT-003 | 文件编码统一为 UTF-8；不依赖系统默认编码 |
| NFR-PORT-004 | 不依赖任何特定 shell 内置命令（如 `cat << EOF`、`grep -P`）；如教学场景需演示，须提供 PowerShell 与 bash 双版本 |
| NFR-PORT-005 | 终端彩色输出在 Windows 10+ 默认终端、Windows Terminal、macOS Terminal、Linux 主流终端均可正常显示 |

## 6.3 可维护性（Maintainability）

| 编号 | 需求 |
| --- | --- |
| NFR-MAINT-001 | 所有公共函数必须有 docstring，含 Args / Returns / Raises 三段（如适用） |
| NFR-MAINT-002 | 类型标注覆盖率 100%（公共函数签名） |
| NFR-MAINT-003 | 单文件代码行数 ≤ 400 行；超出须拆分 |
| NFR-MAINT-004 | 单函数行数 ≤ 60 行；超出须拆分 |
| NFR-MAINT-005 | 圈复杂度 ≤ 10（ruff `C901`） |
| NFR-MAINT-006 | 公共 API 不允许使用 Python 私有 / 未公开接口（如 `platform.os.cpu_count`） |
| NFR-MAINT-007 | 重要架构决策须有 ADR；新增 / 修改 ADR 须经架构组评审 |

## 6.4 可扩展性（Scalability / Extensibility）

| 编号 | 需求 |
| --- | --- |
| NFR-EXT-001 | `paths.py` 物理位置任意层级移动后无需修改文件内容（marker file 模式保证） |
| NFR-EXT-002 | 增加新端（如 `apps/web-backend/`）时无需修改现有 `apps/platform/` 任何代码 |
| NFR-EXT-003 | 新增运行时目录仅需在 `get_dirs_to_initialize()` 增加一行 |
| NFR-EXT-004 | `time_it` 装饰器支持任意可调用对象（同步函数）；保留对未来异步函数支持的扩展空间 |

## 6.5 可测试性（Testability）

| 编号 | 需求 |
| --- | --- |
| NFR-TEST-001 | 所有 common/ 模块单元测试覆盖率 ≥ 80%（核心路径 100%） |
| NFR-TEST-002 | 模块禁止在导入时执行 I/O 副作用（除 paths.py 的 ROOT_DIR 解析外） |
| NFR-TEST-003 | `system_utils` 中对 `psutil`、`torch.cuda` 的访问应可被 mock |
| NFR-TEST-004 | `init_project` 主流程关键步骤可分别测试（目录创建 / 数据检查 / 汇总输出） |

> **本期范围说明**：单元测试代码本身在 D2 阶段不交付，由 D2.5 阶段统一补齐。NFR-TEST 项作为代码结构约束（"必须可测"）在本期生效，便于 D2.5 接入。

## 6.6 兼容性（Compatibility）

| 编号 | 需求 |
| --- | --- |
| NFR-COMPAT-001 | Python 版本：≥ 3.10，≤ 3.12（pyproject.toml `classifiers` 显式声明） |
| NFR-COMPAT-002 | 与现有 conda 环境兼容（`conda create -n odp python=3.10` 后 `pip install` 可用） |
| NFR-COMPAT-003 | 与 PyPA src/ layout 兼容；与 `pip install -e` 兼容 |
| NFR-COMPAT-004 | 与未来引入的 CI 工具（GitHub Actions / GitLab CI）兼容 |

## 6.7 安全性（Security）

| 编号 | 需求 |
| --- | --- |
| NFR-SEC-001 | 不输出敏感信息到日志（如 API key、密码、token） |
| NFR-SEC-002 | `model_name` 等用户输入字段须做字符过滤（仅保留 `[A-Za-z0-9_-]`）后用于文件名，防路径注入 |
| NFR-SEC-003 | 不引入已知 CVE 的依赖版本；依赖更新前由架构组评审 |

## 6.8 可观测性（Observability）

| 编号 | 需求 |
| --- | --- |
| NFR-OBS-001 | 所有关键操作（目录创建 / 失败 / 数据检查）必须有结构化日志 |
| NFR-OBS-002 | 日志文件命名包含时间戳，便于按时间归档与回溯 |
| NFR-OBS-003 | 日志文件须保留至少 30 天（运维侧规范，本期不实现轮转） |

## 6.9 文档质量（Documentation）

| 编号 | 需求 |
| --- | --- |
| NFR-DOC-001 | 每个公共模块开头有 `@FileName` / `@Function` 注释块 |
| NFR-DOC-002 | 每个 README 含"当前状态 / 用途 / 未来计划"三段 |
| NFR-DOC-003 | ADR 文档不少于 1 篇（ADR-001） |
| NFR-DOC-004 | `git log` 自解释（每次 commit 均可单独阅读理解） |

---

# 7. 系统约束与设计原则

## 7.1 技术栈约束

| 项 | 选型 | 理由 |
| --- | --- | --- |
| 语言 | Python 3.10+ | match-case 语法、TypeAlias、union type 写法 |
| 包管理 | pip + pyproject.toml (PEP 621) | 行业主流，避免与 conda 互斥 |
| 构建后端 | setuptools | 成熟稳定，PyPA 推荐之一 |
| 包布局 | src/ layout | 避免 import 路径混淆，PyPA 推荐 |
| Linter | ruff | 速度快，整合多个工具 |
| 类型检查 | mypy | 业界事实标准 |
| 测试框架 | pytest | 业界事实标准 |
| 日志库 | 标准 logging + colorlog | 标准库优先，仅彩色用第三方 |

## 7.2 目录结构约束

- 严格遵循 D1 阶段确定的 Monorepo + apps/ 布局。
- "共享资产"位于 `ROOT_DIR/`（`data/`、`models/`、`runs/`）。
- "端私有资产"位于 `APP_DIR/`（`configs/`、`logging/`、`tests/`）。
- 占位目录通过其 README 进入 git，**不得**使用 `.gitkeep` 空文件占位（README 同时承担文档职责）。

## 7.3 编码规范

继承公司《Python 开发规范 v3.2》（REF-08），本期重点强调：

| 规则 | 要求 |
| --- | --- |
| 命名 | 模块 / 函数 snake_case；常量 UPPER_SNAKE_CASE；类 PascalCase |
| Import 顺序 | 标准库 → 第三方 → 本地（ruff isort 自动） |
| 字符串格式化 | f-string 优先 |
| 路径操作 | 仅使用 `pathlib.Path` |
| 异常处理 | 不裸 catch `except:`；`except Exception` 仅在边界层使用 |
| Magic Number | 避免；提取为常量（如 `LINE_WIDTH = 60`） |
| 注释语言 | 中文 / 英文均可，单文件内保持一致 |

## 7.4 git 提交规范

- 遵循 Conventional Commits 1.0.0。
- 每次 commit 限定为一个"完整的、可工作的状态"——禁止提交反面教材代码、半成品代码。
- commit message body 必须解释"为什么"，特别是引入新概念时。

## 7.5 依赖管理原则

- 业务依赖 → 子项目 `pyproject.toml`
- 共享开发工具 → 工作区 `pyproject.toml`
- 软依赖 → 业务代码内 `try / except ImportError` 优雅降级
- 引入新依赖前评估"30 行标准库代码可否替代"

---

# 8. 验收标准与 Definition of Done

## 8.1 总体验收准则

本期交付通过 = 同时满足以下全部条件：

1. **功能完整**：第 5 章所有 P0 需求 100% 实现并通过 AC；P1 需求 ≥ 90%；P2 需求 ≥ 50%。
2. **NFR 达标**：第 6 章所有指标可测量验证，无 P0 NFR 项不达标。
3. **代码质量**：ruff 与 mypy 在工作区根执行均无 error；warning 数量 ≤ 5 且经 Code Reviewer 评估可接受。
4. **文档齐备**：5.9 节列出的 4 类文档产物全部交付。
5. **跨平台验证**：在 Linux、macOS、Windows 至少各 1 台机器上完整跑通验收用例。
6. **Code Review 通过**：至少 1 位资深工程师签字。

## 8.2 关键验收用例（Acceptance Test Cases）

### AT-001 端到端首次跑通（覆盖 G1、US-01）

```bash
# 步骤
git clone <repo> ODPlatform-acceptance && cd ODPlatform-acceptance
conda create -n odp-at python=3.10 -y && conda activate odp-at
pip install -e ./apps/platform
odp-init
```

**通过标准**：
- 无未捕获异常
- 控制台输出彩色、含环境快照、含目录创建汇总
- 日志文件生成于 `apps/platform/logging/init_project/init-project_*.log`
- 全部 15 个目录可在文件系统中验证存在

### AT-002 幂等性验证（覆盖 FR-INIT-003）

```bash
odp-init           # 首次
odp-init           # 再次
```

**通过标准**：第二次执行所有目录均显示"已存在"，无错误，进程退出码 0。

### AT-003 marker file 健壮性（覆盖 FR-PATH-001、NFR-EXT-001）

将 `paths.py` 临时移动至以下位置后导入测试：
1. `apps/platform/src/od_platform/paths.py`（去掉 common 层）
2. `apps/platform/paths.py`（去掉 src 层）
3. `paths.py`（仓库根）

**通过标准**：1、2 位置仍能正确解析 `ROOT_DIR`；位置 3 也能解析（边界情形可接受）。

### AT-004 跨平台一致性（覆盖 NFR-PORT）

在三种 OS 上分别执行 AT-001：
- Ubuntu 22.04（bash）
- macOS 14（zsh）
- Windows 11（PowerShell + Git Bash）

**通过标准**：三端输出格式一致（仅时间戳、绝对路径不同），日志文件均可读。

### AT-005 CJK 表格对齐（覆盖 FR-STR-001/002）

调用 `format_table_row` 输出含中英文混合的多行表格。

**通过标准**：肉眼检查终端中各列纵向严格对齐；自动化测试中校验 `get_display_width` 各典型 case。

### AT-006 软依赖降级（覆盖 FR-SYS-001）

卸载 `psutil`，重新执行 `odp-init`。

**通过标准**：无异常；日志中"内存信息"类别字段显示 `Unknown (psutil 未安装)`。

### AT-007 fail-fast（覆盖 FR-INIT-004）

构造一个无写入权限的目录作为目标父目录，触发 mkdir 失败。

**通过标准**：进程立即退出，退出码 = 1；ERROR 日志清晰指出失败路径与原因；后续未执行的步骤不被执行。

## 8.3 Definition of Done（每个需求）

单条需求"完成"的统一定义：

- [x] 代码实现完成
- [x] 类型标注完整
- [x] docstring 完整
- [x] 通过 ruff / mypy 静态检查
- [x] 至少 1 位 Reviewer 通过 Code Review
- [x] 关联 AC 在本地复测通过
- [x] PR 描述与 commit message 符合规范
- [x] 相关文档（README / ADR / RTM）已同步更新

## 8.4 Definition of Done（整体里程碑）

整个 D2 阶段"完成"的统一定义：

- [x] 8.1 节六项总体准则全部满足
- [x] 8.2 节七个 AT 测试用例全部通过
- [x] 11 次 git commit 形成预期的提交历史，且每条 commit 满足 FR-DOC-004
- [x] 在三种 OS 上均完成 AT-001 验证
- [x] PRD、HLD、测试报告、ADR-001 四份文档归档至 `docs/`
- [x] 阶段评审会议通过

---

# 9. 项目里程碑与交付计划

## 9.1 阶段划分

| 里程碑 | 时间 | 交付物 | 责任人 |
| --- | --- | --- | --- |
| M1：需求评审 | T+0 | 本 PRD v1.0 评审通过 | Owner |
| M2：详细设计 | T+1 ~ T+2 | HLD + 接口契约文档 | 架构组 |
| M3：开发实施（阶段一） | T+3 ~ T+5 | paths / logging / string 三模块 + 第一版 init_project | Dev |
| M4：开发实施（阶段二） | T+6 ~ T+7 | system / performance 模块 + 集成 init_project | Dev |
| M5：工程化打包 | T+8 | pyproject.toml × 2 + entry-point 验证 | Dev |
| M6：文档完善 | T+9 | 占位 README + ADR-001 + 更新的 PRD 实现注 | Owner + Dev |
| M7：QA 验收 | T+10 ~ T+11 | 验收测试报告 | QA |
| M8：阶段评审 | T+12 | 阶段评审会议、归档 | Owner |
| **M9：上线发布** | **T+13** | **合入主干，对全员可用** | **Owner + 平台组** |

> T = 项目启动日；具体日期以项目计划表为准。

## 9.2 交付清单（Deliverables）

| 类别 | 交付物 | 路径 / 形式 |
| --- | --- | --- |
| 代码 | 5 个 common 模块 | `apps/platform/src/od_platform/common/*.py` |
| 代码 | init_project 入口 + 开发期入口 | `apps/platform/src/od_platform/cli/init_project.py`、`scripts/init_project.py` |
| 代码 | 包元信息 | `apps/platform/src/od_platform/__init__.py`、`_version.py` |
| 配置 | 双 pyproject.toml | `pyproject.toml`、`apps/platform/pyproject.toml` |
| 配置 | 仓库基线 | `.gitignore`、`.odp-workspace` |
| 文档 | PRD（本文档）| `docs/srs/PRD-ODPlatform-Common-D2-v1.0.md` |
| 文档 | ADR | `docs/architecture/ADR-001-monorepo.md` |
| 文档 | README × N | 各目录下 README.md |
| 文档 | 验收测试报告 | `docs/qa/D2-acceptance-report.md`（QA 出具） |

---

# 10. 风险评估与应对

| 编号 | 风险描述 | 概率 | 影响 | 等级 | 应对措施 | 责任人 |
| --- | --- | :-: | :-: | :-: | --- | --- |
| R-01 | 学员 / 开发者环境 Python 版本不足 3.10 | 中 | 高 | **高** | pyproject.toml 显式约束；README 与 PRD 1.4 节明确说明；启动检查脚本提示 | Dev |
| R-02 | Windows 终端不支持 ANSI 颜色码 | 低 | 中 | 中 | colorlog 自动降级；Windows 10+ 默认终端实测可用 | QA |
| R-03 | torch / ultralytics 体积大，初次 `pip install` 耗时长 | 高 | 中 | **高** | README 说明预期耗时；提供 conda 镜像源建议；后续考虑改为软依赖 | Dev、Owner |
| R-04 | marker file 模式被误删 | 低 | 高 | 中 | 文件内置警告注释 "DO NOT DELETE"；README 说明；后续可考虑加 git pre-commit 钩子防误删 | Owner |
| R-05 | 多端开发时 APP_DIR 命名冲突（如多个端都叫 `platform`） | 低 | 中 | 低 | ADR-001 与 README 明确命名规范；架构组评审新端时把关 | 架构组 |
| R-06 | 第三方库 colorlog / psutil 的未来版本不兼容 | 中 | 低 | 低 | pyproject.toml 仅给出最低版本约束；引入 dependabot 后定期更新 | Dev |
| R-07 | 业务代码绕过 paths.py 直接硬编码路径 | 中 | 中 | 中 | Code Review 检查清单；ruff 自定义规则（V1.1 引入） | Reviewer |
| R-08 | Conventional Commits 规范未被严格遵守，git log 退化 | 中 | 低 | 低 | 引入 commitlint pre-commit 钩子；新人入职引导 | Owner |
| R-09 | psutil 在某些受限容器内不可用 | 低 | 低 | 低 | 已设计为软依赖（FR-SYS-001），降级显示 "Unknown" | Dev |
| R-10 | 跨平台测试覆盖不足 | 中 | 中 | 中 | AT-004 强制三端验证；招募 Windows 用户参与 QA | QA |

> **等级说明**：高 = 必须立即应对，中 = 跟踪并定期回顾，低 = 接受。

---

# 11. 需求追踪矩阵（RTM）

> RTM 用于将 **需求 → 设计 → 实现 → 测试** 串成一条可追溯链路。Code Review、阶段评审、变更影响分析均依赖此表。

| 需求 ID | 需求摘要 | 优先级 | 关联场景 | 设计文档 | 实现位置 | 验收用例 |
| --- | --- | --- | --- | --- | --- | --- |
| FR-PATH-001 | 工作区根定位 | P0 | US-03、US-04 | HLD §3.1 | paths.py `_find_workspace_root` | AT-003 |
| FR-PATH-002 | APP_DIR 定义 | P0 | US-03 | HLD §3.2 | paths.py `APP_DIR` | AC 内嵌 |
| FR-PATH-003 | 路径常量集中 | P0 | US-01、US-03 | HLD §3.3 | paths.py 全部常量 | AC 内嵌 |
| FR-PATH-004 | 待初始化目录列表 | P0 | US-01 | HLD §3.4 | paths.py `get_dirs_to_initialize` | AT-001 |
| FR-LOG-001 | 统一日志入口 | P0 | US-01、US-02 | HLD §4.1 | logging_utils.py `get_logger` | AT-001、AT-005 |
| FR-LOG-002 | 启动信息打印 | P1 | US-02 | HLD §4.2 | logging_utils.py | AT-001 |
| FR-LOG-003 | 端私有日志位置 | P0 | US-03 | HLD §4.3 | logging_utils + paths | Code Review |
| FR-STR-001 | 显示宽度计算 | P0 | US-01、US-02 | HLD §5.1 | string_utils.py `get_display_width` | AT-005 |
| FR-STR-002 | 宽度感知填充 | P0 | US-01、US-02 | HLD §5.2 | string_utils.py `pad_to_width` | AT-005 |
| FR-STR-003 | 表格格式化 | P1 | US-01 | HLD §5.3 | string_utils.py `format_table_row` | AT-005 |
| FR-SYS-001 | 环境信息采集 | P0 | US-02 | HLD §6.1 | system_utils.py `get_basic_device_info` | AT-001、AT-006 |
| FR-SYS-002 | 环境信息打印 | P0 | US-02 | HLD §6.2 | system_utils.py `log_device_info` | AT-001 |
| FR-SYS-003 | 字节单位格式化 | P2 | — | HLD §6.3 | system_utils.py `_format_size` | 单元测试 |
| FR-PERF-001 | 计时装饰器 | P0 | US-02 | HLD §7.1 | performance_utils.py `time_it` | AT-001 |
| FR-INIT-001 | 主入口 | P0 | US-01 | HLD §8.1 | init_project.py `initialize_project` | AT-001 |
| FR-INIT-002 | raw 数据检查 | P0 | US-01 | HLD §8.2 | init_project.py `_check_raw_data_status` | AT-001 |
| FR-INIT-003 | 幂等性 | P0 | US-01 | HLD §8.3 | init_project.py | AT-002 |
| FR-INIT-004 | fail-fast | P0 | US-01 | HLD §8.4 | init_project.py | AT-007 |
| FR-INIT-005 | 开发期入口 | P1 | US-01 | HLD §8.5 | scripts/init_project.py | AT-001 |
| FR-INIT-006 | 三种调用方式 | P1 | US-01 | HLD §8.6 | 多入口注册 | AT-001、人工 |
| FR-PKG-001 | 子项目配置 | P0 | US-01 | HLD §9.1 | apps/platform/pyproject.toml | AT-001 |
| FR-PKG-002 | 工作区配置 | P1 | — | HLD §9.2 | pyproject.toml | Code Review |
| FR-PKG-003 | 可安装性 | P0 | US-01 | HLD §9.3 | 双 pyproject 联合 | AT-001 |
| FR-DOC-001 | .gitignore | P0 | — | HLD §10.1 | .gitignore | Code Review |
| FR-DOC-002 | 占位 README | P1 | — | HLD §10.2 | 各目录 README.md | 文档评审 |
| FR-DOC-003 | ADR-001 | P0 | US-03 | HLD §10.3 | docs/architecture/ADR-001-*.md | 架构评审 |
| FR-DOC-004 | Conventional Commits | P1 | — | HLD §10.4 | git log | 阶段评审 |

> HLD（High Level Design）是详细设计文档，由架构组在 M2 里程碑产出，本 PRD 仅引用其章节号占位。

---

# 12. 附录

## 附录 A：目录创建机制三类原则（设计参考）

D1 阶段确立的"目录诞生三类"原则，指导本期的目录管理策略：

| 类别 | 出生时机 | 是否进 git | 本期处理 |
| --- | --- | --- | --- |
| A. 代码 / 文档目录 | 写入第一个文件时由编辑器自动创建 | ✅ 进 | 随代码 commit |
| B. 占位目录 | 写其 README 时显式 mkdir | ✅ 进（README 进 git） | 由 FR-DOC-002 落地 |
| C. 运行时目录 | 由 `init_project.py` 创建 | ❌ 不进 | 由 FR-PATH-004 + FR-INIT-001 落地 |

**核心原则**：目录的"创建机制"等同于其"本质"。一次性预建空目录会掩盖这种本质差异。

## 附录 B：字符 Unicode 范围参考（FR-STR-001 实现依据）

| Unicode 区段 | 起止 | 含义 | 显示宽度 |
| --- | --- | --- | --- |
| CJK 统一表意 | U+4E00 – U+9FFF | 常用汉字 | 2 |
| CJK 标点 | U+3000 – U+303F | 中文标点 | 2 |
| 全角 ASCII | U+FF00 – U+FFEF | 全角字符 | 2 |
| CJK 扩展 A | U+3400 – U+4DBF | 扩展汉字 | 2 |
| 平假名 | U+3040 – U+309F | 日文 | 2 |
| 片假名 | U+30A0 – U+30FF | 日文 | 2 |
| 韩文音节 | U+AC00 – U+D7AF | 韩文 | 2 |
| 其他 | — | ASCII 等 | 1 |

## 附录 C：日志文件命名规则示例

模板：`<prefix>_<YYYYMMDD-HHMMSS-fff>[_<safe_model_name>].log`

示例：

| 调用 | 文件名 |
| --- | --- |
| `get_logger(LOGGING_DIR, "init_project")` | `init-project_20260508-103045-123.log` |
| `get_logger(LOGGING_DIR, "train", model_name="yolo11n")` | `train_20260508-103045-123_yolo11n.log` |
| `get_logger(LOGGING_DIR, "debug", temp_log=True)` | `temp_20260508-103045-123.log` |

## 附录 D：Conventional Commits 类型对照表

| 类型 | 用途 | 示例 |
| --- | --- | --- |
| `feat` | 新功能 | `feat(common): add paths.py with marker-file ROOT_DIR + APP_DIR` |
| `fix` | bug 修复 | `fix(logging): prevent duplicate handlers on re-entry` |
| `chore` | 杂事（配置 / 依赖） | `chore: initial commit with .gitignore + .odp-workspace marker` |
| `refactor` | 重构（行为不变） | `refactor(paths): extract marker resolution into helper` |
| `docs` | 文档 | `docs: add ADR-001 documenting Monorepo decision` |
| `test` | 测试 | `test(paths): add cases for nested workspace detection` |
| `style` | 格式化 | `style: apply ruff format to common/` |

## 附录 E：术语补充

- **Single Source of Truth (SSoT)**：单一权威数据源原则。本 PRD 中体现为：版本号只写在 `_version.py`、目录列表只写在 `get_dirs_to_initialize()`。
- **Fail-fast**：错误尽早暴露原则。任何"模糊状态"应立即终止，避免下游基于错误状态继续运行。
- **Safe by default**：默认安全原则。危险操作的默认行为应是只读 / 预演，需显式确认才能执行（本期未完整覆盖；将在 D2.5 reset_project 中完整体现）。

## 附录 F：本 PRD 与开发文档的对应关系

| 本 PRD 章节 | 对应开发文档章节 |
| --- | --- |
| 5.2 paths | 阶段 2-3、阶段 12.1 |
| 5.3 logging | 阶段 5 |
| 5.4 string | 阶段 7 |
| 5.5 system | 阶段 8 |
| 5.6 performance | 阶段 9 |
| 5.7 init_project | 阶段 1、4、6、10 |
| 5.8 pyproject | 阶段 11 |
| 5.9 文档产物 | 阶段 0、阶段 12.2、12.3 |
| 8 验收 | 各阶段"检查点"汇总 |

> **写作说明**：开发文档以"撞墙→修复"的叙事推导为何这样实现；本 PRD 以"做什么、达到何种程度"定义需求。两者共同构成本期完整的设计-实现-验收闭环。

---

## 文档结束

| 文档负责人签字 | | 日期 | |
| --- | --- | --- | --- |
| 产品 Owner | 雨霓 | 2026-05-08 | |
| 架构组负责人 | | | |
| QA 负责人 | | | |
| 平台组负责人 | | | |

**— 本 PRD 终止于此 —**
