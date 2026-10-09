# Project Memory Protocol

Project Memory Protocol 是我从长期 AI 辅助科研和开发过程中整理出来的一个小工具，用来减少跨对话工作时的上下文丢失。

普通摘要很方便，但时间久了容易丢失决策原因、失败路线、不确定性和原始证据；把全部对话都塞回上下文又太重。这个工具采用一组可直接阅读的 Markdown/JSONL 文件保存不同类型的项目状态，再根据当前问题生成较小的上下文包。

它目前支持：

- 保存显式注册的对话或 JSONL 证据，并记录哈希和快照关系；
- 分开记录当前状态、未完成工作、决策、专题理解、历史阶段和原子声明；
- 使用本地 SQLite FTS 检索，不依赖在线模型或托管服务；
- 生成带来源位置和省略清单的问题范围上下文；
- 检查归档完整性、声明结构、隐私风险和恢复能力。

## 快速开始

```bash
python -m pip install git+https://github.com/EnterUniverse/project-memory-protocol.git
pmem init
pmem source add path/to/conversation.jsonl --id design-session --kind generic-jsonl
pmem archive sync
pmem index --include-archive
pmem compile --query "为什么修改了存储格式？"
pmem audit --full-hash
```

原始归档、索引和本机来源注册表默认不进入 Git。程序不会自动扫描用户主目录或聊天记录，所有证据源都需要显式注册。

这个工具不会替你判断结论是否正确，也不能替代对当前代码、数据、日志和进程的检查。记忆的作用是帮助人和智能体找到证据、恢复问题背景，而不是把历史结论变成新的权威。

完整使用说明见英文 [README](README.md) 和 [`docs/`](docs/)。仓库示例均为虚构内容，不包含原项目的对话、研究内容、个人信息、路径或 Git 历史。
