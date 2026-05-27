# Solana Meme Research & Paper Execution OS — 更新后项目认知 v2

生成时间：2026-05-26
项目根目录：`/root/sikk-gmgn/`
状态：UPDATED_COGNITION_BASELINE_V2
新增依据：`交易系统的本质：阶段化拆解 (2)`
核心新增文档：`docs/trading_system_stage_layer_design.md`

---

## 1. 一句话定位

本项目不是普通 SOL 交易脚本，不是单币分析工具，也不是“发现一个币然后找买点”。

本项目的真实目标是：

> 构建一个运行在 Hermes 上的 Solana meme 市场全自动研究与纸面执行工作流 OS。

但更精确地说，它的本质是：

> 一个以安全门禁、市场门禁、钱包事实、结构证据、筹码控制权、生命周期判断、K 线策略适配和解释复盘为核心的状态机系统。

系统核心链路：

```text
新代币出现
→ 排除安全硬风险
→ 排除市场硬风险
→ 识别早期钱包与第一波控盘结构
→ 判断早期结构资金是否仍有筹码控制权
→ 判断是否已经派发完成或正在派发
→ 结合 K 线、成交量、箱体、钱包持仓、生命周期
→ 输出：排除 / 记录 / 风险监控 / 观察 / 策略候选 / 纸面验证
→ 纸面执行
→ 复盘沉淀
→ 规则更新候选
```

最重要的认知升级：

```text
不是找庄家。
不是找买点。
而是持续判断：
1. 结构侧是否仍然掌握筹码控制权；
2. 当前参与是否会成为结构侧的退出流动性；
3. 当前状态应该排除、记录、监控、观察，还是进入纸面验证。
```

---

## 2. 当前项目不能被误解为什么

### 2.1 不是旧 SIKK Quant Runner 主线

不要把 `/root/sikk-gmgn/` 和 `/root/sikk-quant-runner-restored/` 混为一谈。

当前项目是最近建立的独立 Solana meme / GMGN 工作流 OS 项目。

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

### 2.3 不是买点系统

系统输出不是“买 / 不买”。

系统输出应是：

```text
EXCLUDE
RECORD_ONLY
WATCHING
RISK_MONITOR
WALLET_SUPPORT
WALLET_PAUSE
WALLET_BLOCK
PAPER_READY
REVIEW_REQUIRED
```

### 2.4 不是只做钱包结构分析

钱包结构只解决：

```text
结构侧是否仍可能掌握筹码控制权
结构侧是否已经派发
是否存在继续操作或二段扩张的动机
```

钱包结构不解决：

```text
现在是否有参与位置
是否应该买入
是否应该真实交易
```

参与位置必须由 K 线策略层和状态机层共同判断，且当前只能进入纸面验证。

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

最近验证结果：

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

## 4. 新增系统阶段认知

后续系统必须按以下阶段设计，不得乱序：

```text
阶段 0：系统边界定义
阶段 1：新代币发现
阶段 2：安全硬风险过滤
阶段 3：市场硬风险过滤
阶段 4：开盘时间窗口与早期结构识别
阶段 5：早期钱包与资金来源分析
阶段 6：第一波控盘箱体识别
阶段 7：筹码状态与派发进度判断
阶段 8：主导侧生命周期与行为意图判断
阶段 9：K 线转强与策略适配
阶段 10：状态输出与后续监控
阶段 11：纸面执行与复盘沉淀
```

关键顺序原则：

```text
安全硬风险 > 市场硬风险 > 钱包结构 > 筹码状态 > 生命周期 > K 线策略 > 状态机输出 > 纸面验证
```

不能跳过前面的硬风险过滤，直接进入钱包结构分析。

---

## 5. 新增系统层次认知

阶段是时间顺序，层次是系统结构。

系统分 9 层：

```text
第 1 层：数据层
第 2 层：安全过滤层
第 3 层：市场过滤层
第 4 层：钱包事实层
第 5 层：结构证据层
第 6 层：行为推断层
第 7 层：盘面策略层
第 8 层：状态机决策层
第 9 层：解释与复盘层
```

各层边界：

```text
数据层：只负责接口调用、原始数据保存、字段标准化、快照、质量检查。
安全过滤层：只负责合约安全、交易限制、池子风险、权限风险。
市场过滤层：只负责市值、流动性、成交量、滑点、涨幅、池子深度。
钱包事实层：只输出钱包买入、卖出、持仓、资金来源、转账路径等事实。
结构证据层：只输出同源、同步、资金路径、派发路径、筹码集中度等证据。
行为推断层：输出主导侧生命周期、控筹状态、派发进度等推断，必须带不确定性。
盘面策略层：判断是否有纸面策略参与位置，不授权真实交易。
状态机决策层：输出排除、记录、监控、观察、纸面验证。
解释与复盘层：解释为什么这样判断、什么条件失效、判断链哪里错了。
```

---

## 6. 当前最大差距

当前系统更准确地说是：

```text
Solana meme 候选研究流水线
```

还不是完整的：

```text
Solana meme 全自动研究与纸面执行工作流 OS
```

主要差距：

### 6.1 缺 OS 主状态机

现在有 token 级别的 `phase_state.json`，但缺少 OS 级别状态。

需要新增：

```text
state/os_state.json
```

### 6.2 缺候选发现正式入口

需要形成：

```text
meme-candidate-discovery
meme-candidate-pool-manager
```

### 6.3 缺安全硬风险 / 市场硬风险的前置分层

当前 `meme-token-panel` 和 `meme-trade-gate` 有部分安全和市场判断，但 OS 认知要求更明确：

```text
安全不过，不进入钱包结构分析。
市场不过，不进入早期结构分析。
```

因此后续应明确抽象：

```text
meme-safety-gate
meme-market-gate
```

或至少在现有 skill 输出中形成明确阶段字段。

### 6.4 缺开盘窗口和早期结构专门模块

当前钱包结构分析还不够精确区分：

```text
0-1 分钟
1-5 分钟
5-15 分钟
15-30 分钟
30-120 分钟
2 小时以上
```

需要新增或强化：

```text
early_wallet_window_analysis
early_chip_concentration
early_wallet_remaining_ratio
early_wallet_sell_status
```

### 6.5 缺控盘箱体 / 筹码派发 / 生命周期层

需要新增结构化输出：

```text
control_box_detected
chip_control_status
distribution_progress
dominant_side_lifecycle
dominant_side_intent
counter_evidence
```

### 6.6 缺 K 线策略适配层

钱包结构只是前提，不是纸面参与信号。

需要新增：

```text
meme-strategy-fit
```

判断：

```text
箱体突破回踩
深洗反转
二段扩张
风险监控
排除
```

### 6.7 缺 paper trading 生命周期

完整纸面执行至少需要：

```text
meme-paper-entry
meme-paper-monitor
meme-paper-exit
meme-paper-position-ledger
```

### 6.8 缺复盘沉淀结构化层

需要新增：

```text
meme-paper-review
meme-signal-effectiveness
meme-rule-update-proposal
meme-pattern-library
```

复盘不能只看盈亏，必须看判断链哪里错了。

---

## 7. 新状态机定义

最终输出不能是“买/不买”，而应是：

```text
EXCLUDE：安全、市场或结构硬风险，排除
RECORD_ONLY：信息不足或暂不适合，只记录
WATCHING：有结构迹象，但未转强
RISK_MONITOR：有机会但风险较高，需要持续监控
WALLET_SUPPORT：钱包结构支持继续观察
WALLET_PAUSE：钱包结构矛盾，暂停
WALLET_BLOCK：钱包结构明显风险，阻断
PAPER_READY：钱包 + K 线 + 策略条件满足，进入纸面验证
REVIEW_REQUIRED：数据冲突或不足，需要复查
```

`PAPER_READY` 只能表示：

```text
允许进入纸面验证 / paper observation / paper ledger
```

不能表示：

```text
允许真实买入
允许下单
允许签名
允许广播
```

---

## 8. 必须建立的核心表

后续 spec/schema 实现前，必须先把这些表落地：

```text
阶段表：每个阶段做什么、输入、输出、阻断条件、下一阶段条件
数据需求表：每个判断需要哪些字段、字段来源、事实/推断分类、缺失处理
钱包角色表：每类钱包如何识别、证据要求、风险等级、处理动作
筹码状态表：早期钱包剩多少、是否清仓、是否转移、是否派发、是否仍在 Top Holder
生命周期表：吸筹、控盘、洗盘、拉升、派发、再吸筹、二段扩张、撤退等分类
状态机表：什么条件下排除、记录、监控、观察、进入纸面验证
解释报告表：为什么判断、证据、反证、风险、失效条件、下次看什么
```

这些已经在：

```text
docs/trading_system_stage_layer_design.md
```

中形成第一版。

---

## 9. 系统公式

```text
Token Decision
=
Safety Gate
× Market Gate
× Wallet Fact Layer
× Structure Evidence Layer
× Chip Control Inference
× Market Structure Confirmation
× Strategy Fit
× Risk Explanation
```

说明：

```text
硬风险是乘法门禁；
结构证据是条件判断；
K 线是触发确认；
状态机是最终输出；
复盘是下一轮系统学习入口。
```

---

## 10. 下一步路线建议

不要直接跳到写 paper trading 代码。

推荐顺序：

```text
TASK-OS-001：当前权威与任务状态清账
TASK-OS-002：交易系统阶段层次 spec 对齐 docs/specs.md
TASK-OS-003：阶段表 / 数据需求表 / 状态机表 schema
TASK-OS-004：safety gate / market gate 输出契约
TASK-OS-005：early wallet window analysis 契约
TASK-OS-006：chip control / distribution progress 契约
TASK-OS-007：dominant lifecycle 契约
TASK-OS-008：strategy fit 契约
TASK-OS-009：paper position ledger schema
TASK-OS-010：paper review schema
TASK-OS-011：meme-os-controller minimal no-live loop
TASK-OS-012：end-to-end no-live OS dry run
```

---

## 11. 后续 agent 必须遵守的认知

后续任何执行端进入 `/root/sikk-gmgn/` 时，必须先接受以下判断：

```text
本项目目标是 Solana Meme Research & Paper Execution OS。
它不是买点系统，而是状态机系统。
系统核心输出不是买入，而是 EXCLUDE / RECORD_ONLY / WATCHING / RISK_MONITOR / PAPER_READY / REVIEW_REQUIRED。
安全和市场硬风险是乘法门禁，不能跳过。
钱包结构解决筹码控制权问题，不解决入场时机问题。
K 线策略解决纸面参与位置问题，不能替代钱包结构判断。
所有结构侧判断必须使用证据语言和假设语言，不能写成确定庄家。
所有自动化只允许发生在研究、纸面执行和复盘层，不允许触达真实交易、签名、广播和资金操作。
```

---

## 12. 一句话处方

> 现在不是找买点，也不是继续堆 skill，而是把交易结构系统变成阶段明确、层次清楚、证据可追溯、状态可复盘的 Hermes OS。
