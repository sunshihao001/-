# GMGN + Hermes Solana Meme 交易工作流 OS：概念对齐报告

生成时间：2026-05-26
来源：用户上传《GMGN 驱动的 Solana meme 交易工作流 OS _2_.md》
落盘目的：作为当前项目命名、边界和后续执行优先级的概念校准材料，不直接修改 frozen specs。

---

## 1. 最重要的修正

原表达：

> GMGN 驱动的 Solana meme 交易工作流 OS

更准确表达：

> 以 GMGN 数据为入口、运行在 Hermes 上的 Solana meme 交易工作流 OS。

再压缩：

> GMGN 数据入口 + Hermes 状态工作流 + Solana meme 交易门控。

核心区别：

- GMGN 不负责决策，只提供 token、钱包、风险标签、交易行为等原始线索。
- Hermes 不负责“聪明”，负责状态、任务调度、模块交接、中断恢复、交付物落盘。
- 交易门控不是直接下单，而是把人工经验拆成可执行、可追踪、可升级的流程。

---

## 2. 对当前项目的直接影响

当前系统不应该被描述成：

> 一个自动赚钱 / 自动交易 / 自动下单系统。

当前更准确的项目定位是：

> 一条以 GMGN 数据为入口，由 Hermes 持续运行、保存状态、调度 skill、生成证据链和门控结果的 Solana meme 交易工作流。

它的当前阶段能力是：

```text
GMGN trending 候选
→ candidate-entry
→ token-panel
→ wallet-roles
→ wallet-structure
→ evidence-chain
→ trade-gate
→ workflow-summary
```

当前全流程已实测跑通，最近一次 batch：

```text
Batch ID: 20260526T123011Z
Candidate Count: 4
Filtered Out Count: 1
Completed Count: 4
Final Decisions: 全部 NEED_MORE_DATA
```

这说明：

- 工作流连通性成立。
- GMGN 入口可用。
- Hermes 状态流水线可运行。
- 门控偏保守，尚未产生 PAPER_ONLY。
- 当前瓶颈不是“能不能跑”，而是“判断质量、数据充分性、门控规则和样本校准”。

---

## 3. 应该停止使用的模糊词

### 3.1 “GMGN 驱动”

问题：容易让 AI 误解成 GMGN 替系统做决策。

建议替换为：

> 以 GMGN 数据为入口。

### 3.2 “交易系统”

问题：不同角色会理解成完全不同的东西：

- 交易员：买卖规则
- 程序员：数据、策略、执行、风控、日志
- 量化人：因子、回测、组合、风险模型
- 链上玩家：看盘、看钱包、看聪明钱、抢速度

建议替换为：

> Solana meme 交易工作流 OS。

或者更精确：

> Solana meme 研究门控与执行准备工作流。

### 3.3 “OS”

OS 只有在满足四个条件时才成立：

1. 能持续运行
2. 能保存状态
3. 能把任务交给不同模块
4. 中断后能接着跑

当前项目已经具备其中大部分：

- `meme-workflow-controller`：任务调度
- `phase_state.json`：状态保存
- `data/runs/<token>/`：交接物落盘
- `state/active_runs.json` / `state/completed_runs.json`：运行索引
- `--from <phase>`：断点续跑入口

但仍需要继续强化：

- 异常统一归因
- 批量运行恢复
- 更清楚的 ERROR / BLOCK / NEED_MORE_DATA / TIMEOUT 语义
- 长期运行调度

---

## 4. 当前最准确的项目定义

建议作为后续对外/对 agent 的统一定义：

> 这是一个以 GMGN 数据为入口、运行在 Hermes 上的 Solana meme 交易工作流 OS。它通过候选发现、代币初筛、钱包结构分析、市场结构判断、证据链合成、策略门控和状态化复盘，把人工看盘与钱包判断逐步工程化为可持续运行、可接续、可验证、可升级的半自动/自动交易准备流程。

更短版本：

> GMGN 数据入口 + Hermes 状态工作流 + Solana meme 交易门控。

当前阶段版本：

> 当前阶段不是自动下单系统，而是 GMGN 数据入口到 Hermes 状态化研究门控的可运行流水线。

---

## 5. 与已完成工作的对齐

已经完成：

- P1：7 个 Hermes skill 的 `SKILL.md` 补齐
- P2：evidence-chain / trade-gate / controller 回归测试加强，全量 `27 passed`
- P3：跨 skill 字段契约文档：`docs/cross_skill_handoff_contract.md`
- P4：真实 GMGN trending batch 跑通

当前真实产物证明系统已经不是纯设想：

```text
/root/sikk-gmgn/data/runs/batches/20260526T123011Z/筛选结果.json
/root/sikk-gmgn/data/runs/batches/20260526T123011Z/筛选报告.md
/root/sikk-gmgn/data/runs/<token>/workflow_summary.md
```

---

## 6. 下一步优先级建议

按“距离真实核心目标”排序，不再做无用骨架：

### P5：归档 Walking Skeleton 过度设计

目的：避免继续把注意力放在 mock 骨架，而不是实际 GMGN 数据和门控质量。

交付物：

```text
reports/walking_skeleton_deprioritization_20260526.md
```

内容：

- 说明真实管线已跑通
- Walking Skeleton 保留为 smoke / regression 工具
- 不再作为主线验收目标

### P6：分析最近 batch 为什么全是 NEED_MORE_DATA

目的：找出门控偏保守的真实原因。

重点检查：

- 为什么 smart money 都是 0 / no_sm
- 钱包结构为什么多为 high / critical
- evidence-chain 为什么 dominant_behavior 多为 UNKNOWN
- gate_score 为什么集中在 27~33
- 是数据缺失、规则过严、还是上游字段解析不足

交付物：

```text
reports/batch_20260526T123011Z_need_more_data_analysis.md
```

### P7：补“样本校准任务卡”

目的：从真实 batch 中抽样，把 NEED_MORE_DATA 的原因变成可执行修复任务。

可能任务：

- wallet_roles 智能钱字段解析增强
- wallet_structure 风险阈值校准
- evidence_chain UNKNOWN 归因报告
- trade_gate NEED_MORE_DATA reason 展开

---

## 7. 一句话结论

你要做的不是“更轻的量化系统”，也不是“GMGN 自动交易脚本”。

你要做的是：

> 把你每天看 Solana meme 的隐性判断，拆成 Hermes 能持续运行、能保存状态、能交接模块、能失败恢复、能逐步升级到 paper / semi-auto / auto 的交易工作流。

当前系统已经完成了“能跑”的第一层。下一步不是再搭骨架，而是分析真实 batch 的 `NEED_MORE_DATA`，把判断质量往前推。
