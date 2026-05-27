# 02｜GMGN 入口和候选代币池

## 这一篇要解决的问题

本篇基于当前可见上下文生成：上一篇已经建立了流水线总图，随后又拆解了“GMGN 不能直接变成买入信号”，并用 chatroom 听了慢做与快做的不同视角。

这一篇解决第二个问题：GMGN 进入系统以后，到底应该提供什么，哪些字段只能参考，候选代币池承担什么责任。

## 正文

### 1. GMGN 在系统里的第一身份：入口

GMGN 最先承担的是入口责任。

入口的意思很简单：

```text
它把 token 带到系统面前。
```

一个 Solana meme token 可能因为很多原因出现在 GMGN：

- 成交突然变多；
- 价格短时间上涨；
- 新池子出现；
- 有钱包早期买入；
- 某些标签地址参与；
- 热榜排名上升；
- 风险提示看起来正常；
- 社区开始讨论。

这些现象可以让 token 进入候选池。

候选池的含义是：

```text
这个 token 值得被检查。
```

到这里为止，系统只完成了一件事：发现对象。

它还没有完成：

- 风险过滤；
- 钱包结构分析；
- 市场阶段判断；
- 策略门控；
- paper review；
- 人工审查；
- 任何执行许可。

所以 GMGN 的第一身份是入口，不承担裁判责任。

### 2. 候选代币池是什么

候选代币池可以理解成一个待检查列表。

它不是信号池。它也不是买入列表。

更准确的形状是：

```text
candidate_token_pool = 一组等待被系统检查的 token
```

一个候选 token 进入池子时，至少应该带上这些信息：

```text
token_id
source
发现时间
进入原因
GMGN 原始页面或请求来源
原始字段快照
当前状态
下一步检查项
```

比如：

```text
token: ABC
source: GMGN
entered_at: 2026-05-24 10:00:00
entry_reason: 24h volume spike + early wallet activity
state: CANDIDATE
next_check: risk_filter
```

这个记录看起来慢，但它以后会救命。

因为系统以后可以回答：

- 这个 token 为什么进来？
- 当时看到的字段是什么？
- 是谁把它放进候选池？
- 后面为什么被拒绝？
- 如果后面涨了，是系统错过，还是当时证据不足？
- 如果后面归零，是哪个风险字段没拦住？

没有这个候选池记录，后面的复盘只能靠回忆。

靠回忆做交易系统，等于主动放弃归因。

### 3. GMGN 应该提供哪些字段

GMGN 字段可以先分成 6 类。

#### 第一类：token 基础字段

这类字段帮助系统确认对象是谁。

包括：

- token 地址；
- token 名称；
- symbol；
- 创建时间；
- 所属链；
- 合约或 mint 信息；
- pair / pool 地址；
- 主要交易池。

这类字段的用途是建档。

系统先要知道自己正在检查哪一个对象。

如果 token 地址都不稳定，后面的热度、钱包、成交、风险都没有意义。

#### 第二类：市场活动字段

这类字段帮助系统判断 token 有没有进入观察范围。

包括：

- 当前价格；
- 市值；
- 流动性；
- 交易量；
- 买卖笔数；
- 买卖人数；
- 价格变化；
- 成交变化；
- 热榜位置。

这些字段可以决定是否进入候选池。

例如：

```text
短时间成交升高
+ 流动性达到最低观察线
+ 买卖人数不是个位数
→ 进入 CANDIDATE
```

注意，这一步只说明“值得检查”。

市场活动强，只能代表有人行动。它不能代表行动质量。

#### 第三类：风险提示字段

这类字段进入第一道风险过滤。

包括：

- 是否可卖；
- 是否有高税；
- 是否有黑名单风险；
- 是否有 mint / freeze / 权限风险；
- 是否有池子异常；
- 是否有流动性异常；
- 是否有持币集中；
- 是否有合约风险提示。

风险提示字段的优先级很高。

如果某个字段显示危险，系统可以快速进入：

```text
RISK_REJECTED
```

如果字段缺失，系统不要假装安全。

更合适的状态是：

```text
NEED_MORE_EVIDENCE
```

这就是“快做拒绝，慢做判断”。

明显危险要快拒绝。证据不足要慢补证据。

#### 第四类：钱包线索字段

这类字段进入钱包结构分析。

包括：

- 早期买入钱包；
- 大额买入钱包；
- 大额卖出钱包；
- top holders；
- smart money 标签；
- dev / insider / sniper 等标签；
- 钱包之间的交互；
- 钱包资金来源；
- 钱包历史行为；
- 同一批钱包是否多次共同出现。

钱包字段很有价值，也很容易误导。

一个钱包被标成 smart money，不代表这次一定对。

一个钱包早期买入，不代表它会拉盘。

一组钱包看起来同源，也要看资金来源、买入时序、卖出行为和历史复现。

所以钱包字段的使用方式应该是：

```text
GMGN wallet clue
→ raw evidence
→ wallet canonical object
→ wallet feature
→ wallet structure signal candidate
```

不能写成：

```text
smart money 买了
→ 买
```

### 4. 哪些字段只能做参考

GMGN 里有些字段很吸引人，但它们只能做参考。

#### 热榜只能做参考

热榜说明注意力来了。

注意力来了以后，可能出现三种情况：

- 早期启动；
- 中段拉升；
- 末端接盘。

同一个热榜字段，在不同阶段含义完全不同。

所以热榜适合触发检查，不适合输出结论。

#### 短时涨幅只能做参考

短时涨幅说明价格已经动了。

价格已经动了以后，要问：

- 是启动，还是拉升末端？
- 是真实买盘，还是薄池拉盘？
- 流动性够不够退出？
- 早期钱包有没有开始卖？
- 大户有没有集中分发？

涨幅只是现象。

市场阶段判断才能决定它的意义。

#### smart money 标签只能做参考

smart money 是外部标签。

外部标签需要重新进入系统验证。

系统要看：

- 这个钱包过去是否真的有优势；
- 它这次买入金额是否有意义；
- 它买入后有没有继续加仓；
- 它是否已经卖出；
- 它和其他钱包有没有同源关系；
- 它是否只是跟单路径的一环。

标签可以让系统更快发现线索。

判断要靠证据链。

#### GMGN 风险通过只能做参考

风险通过只说明 GMGN 当前视角没有发现某些风险。

它不能说明：

- 风险不存在；
- 数据完整；
- 字段最新；
- 系统可以进入 paper；
- 系统可以执行。

风险字段通过以后，还要进入系统自己的风险过滤。

### 5. GMGN 字段进入系统的正确路径

安全路径可以写成：

```text
GMGN 页面 / API / 截图 / 字段
→ raw_evidence
→ source_to_canonical_mapping
→ canonical_token / canonical_wallet / canonical_pool
→ feature_artifact
→ structure_signal
→ strategy_gate
→ workflow_state
```

每一层都有自己的责任。

#### raw_evidence 层

保存 GMGN 原始信息。

包括：

- 请求；
- 响应；
- 错误；
- 时间；
- 来源；
- 字段；
- 页面或接口版本；
- 采集上下文。

这一层不做判断。

#### canonical 层

把 GMGN 字段变成系统内部对象。

例如：

```text
GMGN 的 token 页面字段
→ canonical_token

GMGN 的钱包标签
→ canonical_wallet_label_evidence

GMGN 的池子数据
→ canonical_pool
```

这一层负责统一语言。

#### feature 层

从标准对象计算特征。

例如：

- 持币集中度；
- 早期买入比例；
- 钱包交互密度；
- 大户净买入；
- 大户净卖出；
- 流动性变化；
- 成交扩散度。

这一层负责把事实转成可比较的指标。

#### structure_signal 层

把特征组合成结构判断。

例如：

- 疑似同源钱包组；
- 疑似早期结构钱包；
- 分发风险；
- 出货风险；
- 洗盘候选；
- 二波候选。

这一层仍然不是交易许可。

#### strategy_gate 层

把结构判断放进策略边界里。

输出状态可以先用：

```text
REJECT
WATCH
TRACK
PAPER_REVIEW_CANDIDATE
MANUAL_REVIEW_REQUIRED
EXECUTION_BLOCKED
```

这里故意不用“买入信号”。

因为“买入信号”会把观察、验证、审查、执行混成一个词。

### 6. 候选池的状态机

候选池不要只有一个列表。

它应该有状态。

第一版可以这样设计：

```text
DISCOVERED
→ CANDIDATE
→ RISK_CHECKING
→ RISK_REJECTED / RISK_PASSED / NEED_MORE_EVIDENCE
→ WALLET_ANALYSIS_PENDING
→ STRUCTURE_SIGNAL_CANDIDATE
→ MARKET_PHASE_CHECKING
→ WATCH / TRACK / PAPER_REVIEW_CANDIDATE / REJECT
```

这些状态让系统可以接续。

Hermes 在这里的价值就出现了：

- 记录 token 当前在哪一步；
- 记录上一步为什么通过；
- 记录哪些证据缺失；
- 记录下次补查什么；
- 记录被拒绝的原因；
- 记录进入观察的条件；
- 记录是否允许进入 paper review。

一个没有状态机的候选池，很快会变成收藏夹。

一个有状态机的候选池，才会变成工作流。

### 7. 慢做和快做怎么分

结合前面的 chatroom，可以把 GMGN 入口这一层分成两类。

#### 可以快做

这些环节低风险、可逆、偏机械：

- 拉取候选 token；
- 保存 GMGN 原始字段；
- 去重；
- 建立候选池记录；
- 标记缺失字段；
- 导出报告；
- 更新索引；
- 记录 workflow_state。

这里的快，是让系统更快看见材料。

#### 必须慢做

这些环节判断密集、容易误伤、会影响后续状态：

- 字段含义定义；
- 风险字段解释；
- smart money 标签解释；
- 钱包结构判断；
- 市场阶段判断；
- PAPER_REVIEW_CANDIDATE 条件；
- EXECUTION 类词汇边界；
- 报告和授权的分离。

这里的慢，是为了不把材料误读成命令。

### 8. 第一版 GMGN 候选池最小模型

第一版可以先做得很小。

只需要让每个候选 token 形成一张卡片。

```text
candidate_id:
token_address:
source: GMGN
entered_at:
entry_reason:
raw_evidence_ref:
risk_status:
wallet_analysis_status:
market_phase_status:
workflow_state:
missing_fields:
next_check:
forbidden_downstream:
```

其中 `forbidden_downstream` 很重要。

它应该默认写：

```text
no_live_trading
no_swap
no_private_key
no_signing
no_broadcast
no_execution_permission
```

这样每个候选 token 从进入系统第一刻起，就带着边界。

边界不是最后补的。边界从入口开始。

## 小结

- GMGN 的第一身份是入口，负责把 token 带到系统面前。
- 候选代币池是一组等待检查的对象，进入候选池不代表通过风险过滤。
- GMGN 字段分为基础字段、市场活动字段、风险提示字段、钱包线索字段等，不同字段进入不同下游。
- 热榜、短时涨幅、smart money 标签、风险通过都只能触发检查，不能直接输出交易许可。
- 安全路径是 raw evidence → canonical mapping → feature → structure_signal → strategy_gate → workflow_state。
- GMGN 入口层可以快做采集、去重、记录；必须慢做字段语义、钱包判断、市场阶段和授权边界。

## 下一篇预告

下一篇讲第一道门：风险过滤。

重点拆清楚：一个 token 进入候选池以后，系统应该先排除哪些归零风险、交易安全风险和证据缺口；哪些情况直接 `REJECT`，哪些情况进入 `NEED_MORE_EVIDENCE`，哪些情况才允许继续到钱包结构分析。

---

## 学习反馈

你可以写：

1. 哪里看懂了？
2. 哪里没看懂？
3. 哪个地方想展开？
4. 这个主题和你的真实问题有什么关系？

请写在这行下面：
