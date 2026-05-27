# Solana Meme Research & Paper Execution OS — 更新后项目认知

生成时间：2026-05-26
项目根目录：`/root/sikk-gmgn/`
状态：更新后认知基线 / 后续执行入口

---

## 1. 一句话定位

本项目不是普通的 SOL 交易脚本，也不是单币分析工具。

本项目的真实目标是：

> 构建一个运行在 Hermes 上的 Solana meme 市场全自动研究与纸面执行工作流 OS。

它以 GMGN / Solana meme 市场数据、钱包情报和链上结构分析为核心，把候选发现、token 数据面板、钱包结构分析、行为推断、风险门控、paper trading、复盘沉淀拆成多个 Hermes skills，由总控 skill 自动串联。

目标是做到：

```text
候选发现
→ 自动研究
→ 风险门控
→ 纸面执行
→ 持续监控
→ 复盘归因
→ 规则/知识沉淀
→ 下一轮自动继续
```

整个流程不应该依赖用户中途确认、手动切阶段或手动整理交接物。

---

## 2. 当前项目不能再被误解为什么

### 2.1 不是旧 SIKK Quant Runner 主线

不要把 `/root/sikk-gmgn/` 和旧的 `/root/sikk-quant-runner-restored/` 混为一谈。

当前项目是最近两天建立的独立 Solana meme / GMGN 工作流项目。

### 2.2 不是 live trading 系统

当前和近期目标不包含：

```text
live trading
swap
private key / seed phrase
wallet signing
transaction broadcast
real order placement
fund transfer
auto deploy
production/live trading readiness claim
```

### 2.3 不是只做研究报告

虽然当前有大量 `learning/`、`design/`、`reports/`，但最终目标不是文档沉淀，而是一个可自动运行、可恢复、可审计、可复盘的 Hermes 工作流 OS。

### 2.4 不是单个 `/sol <CA>` 分析工具

`/sol <CA>` 可以是入口之一，但不是全部目标。

完整 OS 还必须支持：

```text
自动候选发现
候选池队列
批量筛选
纸面仓位生命周期
定时监控
纸面退出
复盘沉淀
规则更新候选
```

---

## 3. 当前已有能力

当前 `/root/sikk-gmgn/` 已具备 Phase 1 研究流水线基础。

### 3.1 控制面

已有：

```text
AGENTS.md
CONTEXT.md
docs/specs.md
docs/acceptance.md
docs/freeze_record.md
tasks/task_tree.md
reports/review.md
reports/final_acceptance.md
```

作用：

- 定义角色边界
- 冻结 specs / acceptance / context
- 使用 task card 控制执行
- Backend / QA 只能按任务卡写入
- PM/review 只能给 INTERNAL_PASS
- human final acceptance 独立保留

### 3.2 研究 skill 流水线

已有核心 skill：

```text
skills/meme-candidate-entry/
skills/meme-token-panel/
skills/meme-wallet-roles/
skills/meme-wallet-structure/
skills/meme-evidence-chain/
skills/meme-trade-gate/
skills/meme-workflow-controller/
```

当前研究链路：

```text
meme-candidate-entry
→ meme-token-panel
→ meme-wallet-roles
→ meme-wallet-structure
→ meme-evidence-chain
→ meme-trade-gate
→ workflow_summary
```

### 3.3 规则 / fixture / 测试

已有：

```text
rules/gate_rules_v1.json
rules/downgrade_rules_v1.json
rules/entry_five_forces_rules_v1.json
fixtures/*.json
tests/*.py
```

当前验证结果：

```text
34 passed
规则 JSON 可解析
```

### 3.4 运行数据

已有：

```text
data/runs/<token_address>/candidate_entry.json
data/runs/<token_address>/token_panel.json
data/runs/<token_address>/wallet_roles.json
data/runs/<token_address>/wallet_structure.json
data/runs/<token_address>/evidence_chain.json
data/runs/<token_address>/trade_gate.json
data/runs/<token_address>/workflow_summary.md
```

说明项目已经不只是设计文档，而是已有可运行的研究流水线输出。

---

## 4. 当前最大差距

当前系统更准确地说是：

```text
Solana meme 候选研究流水线
```

还不是完整的：

```text
Solana meme 全自动研究与纸面执行工作流 OS
```

主要差距如下。

### 4.1 缺 OS 主状态机

现在有 token 级别的 `phase_state.json`，但缺少 OS 级别状态。

需要新增：

```text
state/os_state.json
```

它应该记录：

```json
{
  "current_cycle": "...",
  "candidate_queue": [],
  "researching": [],
  "gated": [],
  "paper_open": [],
  "paper_closed": [],
  "review_pending": [],
  "reviewed": [],
  "blocked": []
}
```

没有 OS state，系统无法全自动运转。

### 4.2 缺候选发现正式入口

当前已有候选池和 batch 数据，但还没有把候选发现正式定义成 OS 第一层。

需要形成：

```text
meme-candidate-discovery
meme-candidate-pool-manager
```

负责：

- GMGN trending
- GMGN trenches
- GMGN signal
- watchlist / blacklist
- 去重
- 候选池评分
- 自动进入研究队列

### 4.3 缺 paper trading 生命周期

当前只有 `PAPER_ONLY` 门控结论。

但 `PAPER_ONLY` 不是 paper trading。

完整纸面执行至少需要：

```text
meme-paper-entry
meme-paper-monitor
meme-paper-exit
meme-paper-position-ledger
```

并落地：

```text
data/paper_positions/<paper_trade_id>/paper_position_open.json
data/paper_positions/<paper_trade_id>/paper_position_update.json
data/paper_positions/<paper_trade_id>/paper_position_close.json
data/paper_positions/<paper_trade_id>/paper_trade_journal.md
data/paper_positions/<paper_trade_id>/paper_pnl_snapshot.json
```

### 4.4 缺复盘沉淀结构化层

当前有 reports / learning，但缺少系统可消费的复盘结构。

需要新增：

```text
meme-paper-review
meme-signal-effectiveness
meme-rule-update-proposal
meme-pattern-library
```

复盘输出不能只写 markdown，必须有结构化 JSON：

```json
{
  "paper_trade_id": "...",
  "initial_gate_decision": "PAPER_OBSERVATION_ALLOWED",
  "entry_thesis": "...",
  "result": "win | loss | invalidated | inconclusive",
  "effective_signals": [],
  "misleading_signals": [],
  "missed_risk_signals": [],
  "rule_update_candidate": true,
  "recommended_rule_patch": {}
}
```

### 4.5 总控 skill 还不是 OS controller

当前 `meme-workflow-controller` 更像研究流水线控制器。

未来需要升级为：

```text
meme-os-controller
```

负责全流程：

```text
discover
→ enqueue
→ research
→ gate
→ paper_execute
→ monitor
→ review
→ update_memory
→ report
```

它必须能：

- 自动跑完整周期
- 自动维护 state
- 自动写入 evidence
- 自动处理 BLOCK / WATCH / PAPER / NEED_MORE_DATA
- 自动生成复盘和规则更新候选
- 不需要用户手动切阶段

---

## 5. 必须更新的概念边界

### 5.1 “全自动”的定义

本项目里的“全自动”只能表示：

```text
全自动研究
全自动门控
全自动纸面执行
全自动纸面监控
全自动复盘
全自动报告/规则更新候选
```

明确不表示：

```text
全自动真实交易
自动下单
自动签名
自动广播
自动资金操作
```

### 5.2 PAPER_ONLY 的语义风险

`PAPER_ONLY` 容易被误解为“可以买，只是先纸面”。

建议后续统一改名或补充解释为：

```text
PAPER_OBSERVATION_ALLOWED
```

含义：

```text
允许进入纸面观察 / 模拟记录 / 复盘链路，不代表任何真实执行许可。
```

### 5.3 GMGN 数据的地位

GMGN 数据是候选发现和风险提示输入，不是买入信号。

必须保留：

```text
GMGN labels are hints, not final classification.
GMGN candidate is not a buy signal.
```

---

## 6. 推荐的新 OS 分层

### L1：候选发现层

```text
meme-candidate-discovery
meme-candidate-entry
meme-candidate-pool-manager
```

职责：自动发现、去重、初筛、候选池排序、进入研究队列。

### L2：研究分析层

```text
meme-token-panel
meme-wallet-roles
meme-wallet-structure
meme-evidence-chain
```

职责：token 面板、钱包角色、钱包结构、行为推断、证据链。

### L3：风险门控层

```text
meme-trade-gate
rules/gate_rules_v1.json
rules/downgrade_rules_v1.json
rules/entry_five_forces_rules_v1.json
```

职责：BLOCK / WATCH / PAPER_OBSERVATION_ALLOWED / NEED_MORE_DATA。

### L4：纸面执行层

```text
meme-paper-entry
meme-paper-monitor
meme-paper-exit
meme-paper-position-ledger
```

职责：纸面开仓、纸面监控、纸面退出、纸面账本。

### L5：复盘沉淀层

```text
meme-paper-review
meme-signal-effectiveness
meme-rule-update-proposal
meme-pattern-library
```

职责：复盘归因、信号有效性、规则更新候选、模式库。

### L6：OS 总控层

```text
meme-os-controller
state/os_state.json
```

职责：自动调度完整生命周期。

---

## 7. 新任务路线建议

不要直接跳到写 paper trading 代码。

下一步应先写 OS 级规格，再拆任务卡。

推荐任务顺序：

```text
TASK-OS-001：当前权威与任务状态清账
TASK-OS-002：OS workflow spec
TASK-OS-003：OS state schema
TASK-OS-004：candidate queue / discovery contract
TASK-OS-005：paper position ledger schema
TASK-OS-006：paper entry / monitor / exit contract
TASK-OS-007：paper review schema
TASK-OS-008：rule update proposal schema
TASK-OS-009：meme-os-controller minimal loop
TASK-OS-010：end-to-end no-live OS dry run
```

---

## 8. 明确的下一步动作

第一步不要写交易代码。

第一步应该创建：

```text
docs/os_workflow_spec.md
```

标题：

```text
Solana Meme Research & Paper Execution OS Spec
```

必须定义：

1. OS 目标：全自动研究 + 纸面执行 + 复盘沉淀
2. OS 非目标：live trading / swap / private key / signing / broadcast
3. OS 主状态机
4. skill 分层：discovery / research / gate / paper / review / memory
5. paper position schema
6. review schema
7. 自动调度规则：什么时候发现、什么时候研究、什么时候进入 paper、什么时候监控、什么时候退出、什么时候复盘、什么时候生成规则更新候选

完成这份 spec 后，再创建 `tasks/os/*.md` 任务卡。

---

## 9. 后续 agent 必须遵守的认知

后续任何执行端进入 `/root/sikk-gmgn/` 时，必须先接受以下判断：

```text
本项目目标是 Solana Meme Research & Paper Execution OS。
当前不是 live trading 系统。
当前要补的是 OS 闭环，不是单点 skill 堆叠。
研究流水线已经有基础，下一步重点是 OS state、candidate queue、paper lifecycle、review memory。
所有自动化只允许发生在研究和纸面执行层，不允许触达真实交易、签名、广播和资金操作。
```

---

## 10. 一句话处方

> 现在不是继续堆 skill，而是把 OS 画出来，让已有 skills 进入自动调度、纸面执行和复盘闭环。
