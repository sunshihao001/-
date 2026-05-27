# grill-with-docs 指导：Solana Meme Research & Paper Execution OS 下一步开工前问诊

生成时间：2026-05-26
项目根目录：`/root/sikk-gmgn/`
用途：指导后续 agent 使用 grill-with-docs，把“交易结构系统阶段认知”转成可执行 OS 契约，而不是直接写代码或继续泛理论。

---

## 1. 本次 grill-with-docs 的目标

本次不是重新讨论项目方向，也不是问用户“还要不要做”。

本次 grill 的目标是：

```text
把 Solana Meme Research & Paper Execution OS 的阶段结构、层次边界、状态机输出、纸面执行闭环，问清楚、冻结下来，然后写入工程契约。
```

最终应服务于：

```text
/root/sikk-gmgn/docs/os_workflow_spec.md
/root/sikk-gmgn/tasks/os/TASK-OS-001-current-authority-and-task-state-reconciliation.md
/root/sikk-gmgn/tasks/os/task_tree.md
```

---

## 2. 必须先读的文件

执行 grill 前，必须读取：

```text
/root/sikk-gmgn/AGENTS.md
/root/sikk-gmgn/CONTEXT.md
/root/sikk-gmgn/docs/specs.md
/root/sikk-gmgn/docs/acceptance.md
/root/sikk-gmgn/docs/freeze_record.md
/root/sikk-gmgn/docs/trading_system_stage_layer_design.md
/root/sikk-gmgn/reports/updated_project_cognition_v2_20260526.md
/root/sikk-gmgn/tasks/task_tree.md
```

可辅助读取：

```text
/root/sikk-gmgn/design/README.md
/root/sikk-gmgn/design/phase0-workflow-contract.md
/root/sikk-gmgn/reports/review.md
/root/sikk-gmgn/reports/final_acceptance.md
```

---

## 3. grill-with-docs 的工作方式

主 agent 作为 interviewer，一次只问一个高价值问题。

每个问题必须用于确定以下之一：

```text
目标
边界
输入
输出
状态机
阻断条件
下游交接
验证方式
```

不能问泛问题，例如：

```text
你觉得还要不要继续？
你想做成什么样？
还有什么补充？
```

要问能冻结成文档的问题。

---

## 4. 本项目的核心前提

后续 agent 必须先接受：

```text
1. 本项目不是找庄家。
2. 本项目不是找买点。
3. 本项目不是 live trading。
4. 本项目是状态机系统。
5. 核心输出是 EXCLUDE / RECORD_ONLY / WATCHING / RISK_MONITOR / PAPER_READY / REVIEW_REQUIRED。
6. 安全和市场硬风险是乘法门禁。
7. 钱包结构解决筹码控制权问题，不解决入场时机问题。
8. K 线策略解决纸面参与位置问题，不替代钱包结构判断。
9. PAPER_READY 只允许纸面验证，不允许真实交易。
10. 所有复盘要看判断链哪里错了，而不是只看盈亏。
```

---

## 5. 推荐 grill 问题顺序

### Q1：当前 OS 的第一版验收物是什么？

建议提问：

```text
我们这次不是继续写代码，而是把交易结构系统认知转成运行契约。第一版验收物是否定义为 docs/os_workflow_spec.md + tasks/os/task_tree.md + TASK-OS-001？如果不是，必须替换成什么具体文件？
```

要冻结的答案：

```text
第一版交付文件清单
哪些是必须产物
哪些不是本轮目标
```

---

### Q2：状态机输出是否以新状态为准？

建议提问：

```text
最终状态是否统一为 EXCLUDE / RECORD_ONLY / WATCHING / RISK_MONITOR / WALLET_SUPPORT / WALLET_PAUSE / WALLET_BLOCK / PAPER_READY / REVIEW_REQUIRED？旧的 BLOCK / WATCH / PAPER_ONLY 是否只作为兼容字段保留？
```

要冻结的答案：

```text
状态枚举
旧状态兼容方式
PAPER_ONLY 与 PAPER_READY / PAPER_OBSERVATION_ALLOWED 的关系
```

---

### Q3：安全门禁和市场门禁是否必须前置独立？

建议提问：

```text
是否确认安全硬风险和市场硬风险必须在钱包结构分析前完成？它们是独立 skill，还是先作为现有 token-panel/trade-gate 输出字段落地？
```

要冻结的答案：

```text
安全门禁归属
市场门禁归属
是否新增 meme-safety-gate / meme-market-gate
阻断后是否允许继续分析
```

---

### Q4：钱包结构层和 K 线策略层如何分权？

建议提问：

```text
是否确认钱包结构只判断筹码控制权、派发进度、主导侧生命周期；K 线策略层才判断纸面参与位置？两者是否都必须通过，才允许 PAPER_READY？
```

要冻结的答案：

```text
钱包结构层输出
K 线策略层输出
PAPER_READY 的必要条件
哪些判断不能直接作为买入依据
```

---

### Q5：开盘窗口和早期钱包分析第一版做到多深？

建议提问：

```text
第一版是否必须支持 0-1m / 1-5m / 5-15m / 15-30m / 30-120m 时间窗口？如果数据不足，是否先定义 schema 和 NEED_MORE_DATA 行为，而不强行实现算法？
```

要冻结的答案：

```text
时间窗口枚举
必须字段
缺字段处理
第一版是否只做 schema/contract
```

---

### Q6：纸面执行第一版的边界是什么？

建议提问：

```text
第一版 paper execution 是否只允许创建 paper position ledger、定时更新纸面价格/状态、写复盘，不允许任何交易接口？paper entry 的触发条件是否必须来自 PAPER_READY？
```

要冻结的答案：

```text
paper entry 条件
paper monitor 频率
paper exit 条件
paper position ledger 字段
禁止真实交易边界
```

---

### Q7：复盘沉淀要沉淀什么？

建议提问：

```text
复盘是否必须输出 effective_signals、misleading_signals、missed_risk_signals、invalidated_by、rule_update_candidate、recommended_rule_patch？规则是否只能生成 proposal，不能自动修改？
```

要冻结的答案：

```text
paper_review schema
rule_update_proposal schema
复盘进入 pattern library 的条件
自动改规则是否禁止
```

---

### Q8：当前旧任务树怎么处理？

建议提问：

```text
现有 tasks/task_tree.md 里有旧 READY/已完成状态混杂。下一步是否先做 TASK-OS-001 清账，把已完成/INTERNAL_PASS/blocked/next-ready 状态对齐，再继续 OS spec？
```

要冻结的答案：

```text
是否先任务清账
清账范围
哪些任务保留为历史
哪些任务迁移到 tasks/os
```

---

## 6. grill 结束后的必交付物

grill 结束后，不能只输出聊天总结。

必须写文件：

```text
/root/sikk-gmgn/reports/grill_os_workflow_alignment_20260526.md
/root/sikk-gmgn/docs/os_workflow_spec.md
/root/sikk-gmgn/tasks/os/TASK-OS-001-current-authority-and-task-state-reconciliation.md
```

如果还没到写完整 spec，至少要输出：

```text
/root/sikk-gmgn/reports/grill_os_workflow_alignment_20260526.md
```

其中必须包含：

```text
1. 已确认目标
2. 已确认边界
3. 已确认状态机
4. 未决问题
5. 必须进入 spec 的条款
6. 下一步任务卡
```

---

## 7. 本轮禁止事项

```text
禁止直接写 paper trading 代码
禁止连接交易接口
禁止添加 swap / signing / broadcast 能力
禁止把 PAPER_READY 当真实交易许可
禁止把 GMGN candidate 当买入信号
禁止把疑似结构资金写成确定庄家
禁止绕过 task card 写实现
禁止继续堆 skill 而不先写 OS spec
```

---

## 8. 给后续 agent 的一段可直接使用提示词

```text
你现在在 /root/sikk-gmgn/ 项目中使用 grill-with-docs。

目标不是继续写代码，而是把 Solana Meme Research & Paper Execution OS 的交易结构系统认知转成运行契约。

必须先读取：
- AGENTS.md
- CONTEXT.md
- docs/specs.md
- docs/acceptance.md
- docs/freeze_record.md
- docs/trading_system_stage_layer_design.md
- reports/updated_project_cognition_v2_20260526.md
- tasks/task_tree.md

请按 grill-with-docs 方式，一次只问一个高价值问题，用于冻结：目标、边界、状态机、阶段输入输出、阻断条件、paper execution 边界、复盘沉淀方式、任务树清账方式。

核心前提：
- 本项目不是找庄家；
- 本项目不是找买点；
- 本项目不是 live trading；
- 本项目是状态机系统；
- 安全和市场硬风险是乘法门禁；
- 钱包结构解决筹码控制权问题；
- K 线策略解决纸面参与位置问题；
- PAPER_READY 只允许纸面验证；
- 复盘看判断链哪里错了，不只看盈亏。

最终必须产出：
1. reports/grill_os_workflow_alignment_20260526.md
2. docs/os_workflow_spec.md
3. tasks/os/TASK-OS-001-current-authority-and-task-state-reconciliation.md

禁止实盘、swap、private key、signing、broadcast、order placement。
```
