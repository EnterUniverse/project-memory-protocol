# Project Memory Protocol

[![CI](https://github.com/EnterUniverse/project-memory-protocol/actions/workflows/ci.yml/badge.svg)](https://github.com/EnterUniverse/project-memory-protocol/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

[English](README.md)

为 AI 辅助工作保存可延续的项目上下文。

Project Memory Protocol（`pmem`）是一个本地命令行工具，用于在多次开发或研究会话之间延续项目上下文。它把当前状态保存在可直接阅读的文件中，只归档用户明确指定的来源，并为当前任务组装一份精简的上下文。

所有处理都在本地完成。核心功能不调用模型 API，不依赖托管服务，运行时仅使用 Python 标准库。

## 快速开始

```bash
python -m pip install git+https://github.com/EnterUniverse/project-memory-protocol.git@v0.1.0
cd your-project
pmem init
```

`pmem init` 会创建 `.project-memory/`。首先可以编辑其中两个文件：

- `WORKING_SET.md`：让新会话快速了解项目的简短索引；
- `CURRENT.md`：需要延续到下一次会话的当前状态和推理。

随后建立本地索引，并围绕具体任务提取上下文：

```bash
pmem index
pmem compile --query "为什么修改了存储格式？"
```

输出是普通 Markdown，可以直接阅读，也可以交给 AI 智能体。上下文包会保留来源位置，并列出因 token 预算未纳入的相关内容。

## 保存的内容

```text
.project-memory/
├── RECOVERY.md             # 新会话的恢复步骤
├── WORKING_SET.md          # 简短项目索引
├── CURRENT.md              # 当前状态和推理
├── OPEN_LOOPS.md           # 未完成工作和承诺
├── DECISIONS.md            # 决策及理由
├── PROJECT_NARRATIVE.md    # 较长期的项目历史
├── claims/CLAIMS.jsonl     # 声明及证据链接
├── modules/                # 按主题组织的记录
└── stages/                 # 已完成的迭代
```

这些都是普通 Markdown 或 JSONL 文件，即使不再使用 `pmem` 也能继续阅读。生成的索引、本机来源路径和原始归档默认不会进入 Git。

## 添加来源材料

很多项目只需要维护上述文件。如果还希望保存对话、工具轨迹或其他追加式 JSONL 文件，需要显式注册：

```bash
pmem source add path/to/conversation.jsonl --id design-session --kind generic-jsonl
pmem archive sync
pmem index --include-archive
```

首次同步保存完整快照，后续的追加内容保存为增量；如果已有前缀发生变化，则重新建立快照。归档记录包含 SHA-256 哈希和前后关系。

`pmem` 不会自行搜索主目录中的对话，也不会上传项目数据。

## 常用流程

```text
维护的项目记录 ──────────────┐
                             ├─> 本地索引 ─> 当前任务上下文
显式注册的来源 ─> 本地归档 ──┘
        │                         │
        └──────── 完整性和恢复检查
```

一次典型的会话交接可以这样完成：

```bash
pmem archive sync
pmem index --include-archive
pmem compile --query "导入流程还有哪些问题没有解决？" --token-budget 8000
pmem audit --full-hash
```

需要更广泛的恢复时，可使用 `--profile orient`、`--profile startup` 或 `--profile full`。项目也可以在 `.project-memory/recovery_probes.json` 中保存实际的检索问题，再用 `pmem drill` 做回归检查。

## 命令

| 命令 | 用途 |
|---|---|
| `pmem init` | 创建项目记忆文件 |
| `pmem source add` | 注册本地来源 |
| `pmem archive sync` | 保存快照或追加内容 |
| `pmem index` | 重建本地 SQLite FTS 索引 |
| `pmem compile` | 针对问题或恢复档位生成上下文 |
| `pmem claim add` | 记录带状态和证据的声明 |
| `pmem audit` | 检查文件结构和归档完整性 |
| `pmem privacy scan` | 查找常见密钥和个人标识 |
| `pmem drill` | 运行检索回归检查 |

使用 `pmem <command> --help` 查看参数。

## 设计边界

项目记忆用于导航，不替代项目本身。代码、数据、产物、进程和日志等可能变化的状态，仍应从现场来源核实。

工具有意区分来源材料与维护后的记录、当前状态与历史阶段、声明与证据，以及长期文件与可重新生成的索引。这样可以修正当前理解，同时保留形成该理解的历史依据。具体设计见 [Design](docs/architecture.md)。

## 文档

- [文档索引](docs/README.md)
- [与 AI 智能体配合使用](docs/agent-integration.md)
- [设计与存储模型](docs/architecture.md)
- [文件格式与上下文包参考](docs/schema.md)
- [隐私与限制](docs/threat-model.md)
- [声明状态](docs/epistemic-model.md)
- [恢复检查](docs/evaluation.md)
- [发布流程](docs/releasing.md)

## 项目状态

当前版本已经可以使用，但仍处于早期阶段。文件格式保持开放、可检查；在 1.0 之前，命令行和格式细节仍可能调整。尤其欢迎基于真实上下文恢复问题的反馈。

## 开发

```bash
git clone https://github.com/EnterUniverse/project-memory-protocol.git
cd project-memory-protocol
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
```

提交修改前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
