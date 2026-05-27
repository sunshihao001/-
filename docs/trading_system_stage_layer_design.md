# Solana Meme 交易结构系统阶段层次设计

生成时间：2026-05-26
项目根目录：`/root/sikk-gmgn/`
文档状态：SYSTEM_STAGE_LAYER_DESIGN_V1
来源认知：`交易系统的本质：阶段化拆解 (2)`

---

## 1. 核心定位

本系统不是“发现一个币然后找买点”。

本系统的本质是一个状态机系统：

```text
新代币出现
→ 排除安全硬风险
→ 排除市场硬风险
→ 识别早期钱包与第一波控盘结构
→ 判断早期结构资金是否仍有筹码控制权
→ 判断是否已经派发完成或正在派发
→ 结合 K 线、成交量、箱体、钱包持仓、生命周期
→ 输出：排除 / 记录 / 风险监控 / 观察 / 策略候选 / 纸面验证
```

最关键认知：

```text
不是找庄家。
而是持续判断：
1. 结构侧是否仍然掌握筹码控制权；
2. 当前参与是否会成为结构侧的退出流动性。
```

因此，当前系统应被定义为：

```text
Solana Meme Research & Paper Execution OS
= 代币筛选 + 钱包结构分析 + 策略候选判断 + 风险监控 + 纸面验证 + 复盘沉淀
```

不是：

```text
全自动买卖系统
live trading system
wallet signing system
swap execution system
```

---

## 2. 总阶段图

阶段必须按顺序执行，不能跳过安全和市场硬风险过滤直接进入钱包结构分析。

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

阶段 11 是在原 10 阶段基础上的 OS 闭环补充，用于对接当前项目目标中的 paper trading、monitor、review、rule update proposal。

---

## 3. 阶段表

### 阶段 0：系统边界定义

目标：定义系统做什么、不做什么、输出什么、风险边界在哪里。

输入数据：

```text
项目目标
安全边界
允许状态
禁止动作
证据等级定义
```

判断逻辑：

```text
系统是否只做研究 / 纸面验证 / 状态输出；
是否明确排除 live trading、swap、private key、signing、broadcast；
是否区分事实、证据、推断、结论。
```

输出状态：

```text
BOUNDARY_DEFINED
BOUNDARY_INCOMPLETE
BOUNDARY_BLOCKED
```

阻断条件：

```text
未定义禁止行为；
把疑似结构资金写成确定庄家；
把钱包结构直接作为买入依据；
允许真实交易动作。
```

不能作为买入依据的判断：

```text
疑似结构钱包
疑似同源执行组
GMGN 标签
早期钱包买入
```

---

### 阶段 1：新代币发现

目标：发现刚出现或刚进入候选池的代币，并保存发现时快照。

输入数据：

```text
token 创建时间
系统发现时间
发现时市值
发现时流动性
发现时成交量
交易池地址
初始 holder
GMGN trending / trenches / signal
```

判断逻辑：

```text
比较开盘市值、发现时市值、当前市值、钱包判断时市值、策略信号时市值；
判断是否已经错过早期结构阶段；
判断是否值得进入安全过滤。
```

输出状态：

```text
DISCOVERED
DISCOVERY_RECORD_ONLY
DISCOVERY_TOO_LATE
DISCOVERY_NEED_MORE_DATA
```

输出字段：

```text
token_discovery_snapshot
discovery_market_cap_usd
discovery_liquidity_usd
discovery_volume
token_age_at_discovery
pool_address
initial_holder_snapshot
```

阻断条件：

```text
token address 无效；
缺少基本发现字段；
发现时已明显错过生命周期窗口；
数据来源不可追溯。
```

不能作为买入依据的判断：

```text
GMGN trending
GMGN signal
热门标签
候选池排名
```

---

### 阶段 2：安全硬风险过滤

目标：先排除不能碰的 token。安全风险优先于钱包结构。

输入数据：

```text
honeypot / 貔貅风险
freeze 权限
mint 权限
blacklist 权限
tax / fee
pool / LP risk
fake pool / fake token flags
contract permission flags
```

判断逻辑：

```text
任何安全硬风险命中，直接 SAFETY_BLOCK；
轻微或信息不完整，输出 SAFETY_WARN 或 NEED_MORE_DATA；
安全不过，不进入钱包结构分析。
```

输出状态：

```text
SAFETY_PASS
SAFETY_WARN
SAFETY_BLOCK
SAFETY_NEED_MORE_DATA
```

阻断条件：

```text
能买不能卖；
冻结或转账限制；
可增发 / 拉黑 / 改税；
池子可撤或假池；
买卖税异常；
恶意合约特征。
```

不能作为买入依据的判断：

```text
安全通过只能说明没有发现硬安全风险，不代表值得参与。
```

---

### 阶段 3：市场硬风险过滤

目标：排除市场条件不适合继续分析的 token。

输入数据：

```text
liquidity
market_cap
volume
buy_sell_ratio
pool_depth
top_holder_concentration
current_gain
volatility_quality
slippage_estimate
```

判断逻辑：

```text
流动性太低、市值过高、成交量虚弱、买卖极不平衡、涨幅过大、死亡插针等，都可能导致 MARKET_BLOCK 或 MARKET_WARN；
区分市场热度高和结构机会好。
```

输出状态：

```text
MARKET_PASS
MARKET_WARN
MARKET_BLOCK
MARKET_NEED_MORE_DATA
```

阻断条件：

```text
流动性不足；
池子深度不足；
成交量缺失或疑似虚假；
当前涨幅已经完成主要拉升；
大户过度集中且无后续解释；
波动质量极差。
```

不能作为买入依据的判断：

```text
热度高
成交量高
涨幅强
市值小
```

这些只能进入后续判断，不是策略触发。

---

### 阶段 4：开盘时间窗口与早期结构识别

目标：从 token 开盘开始识别第一批参与资金和早期筹码结构。

输入数据：

```text
0-1 分钟买入钱包
1-5 分钟买入钱包
5-15 分钟买入钱包
15-30 分钟交易和持仓变化
30-120 分钟价格/成交量/持仓结构
早期钱包买入金额
早期钱包剩余持仓
早期钱包卖出状态
```

判断逻辑：

```text
不是只找买得早的钱包；
要找买得早、买得集中、行为相似、资金来源相似、没有完全派发、后续仍影响走势的钱包群。
```

输出状态：

```text
EARLY_STRUCTURE_FOUND
EARLY_STRUCTURE_WEAK
EARLY_STRUCTURE_NOT_FOUND
EARLY_STRUCTURE_NEED_MORE_DATA
```

输出字段：

```text
early_wallet_list
early_buy_window
early_chip_concentration
early_wallet_remaining_ratio
early_wallet_sell_status
```

阻断条件：

```text
早期窗口数据缺失；
早期钱包已全部清仓；
早期结构无法和普通散户区分；
无法追踪剩余筹码。
```

不能作为买入依据的判断：

```text
买得早
早期钱包多
早期成交活跃
```

---

### 阶段 5：早期钱包与资金来源分析

目标：判断早期钱包角色、资金来源和同源关系。

输入数据：

```text
钱包创建时间
入金来源
买入时间
买入金额
当前余额
卖出记录
转账路径
同步行为
历史出现记录
```

钱包角色分类：

```text
新钱包狙击
临时执行钱包
同源执行组
核心资金源
分发接收钱包
派发钱包
利润回收钱包
接盘鲸鱼
```

判断逻辑：

```text
用证据语言表达：疑似结构钱包、疑似同源执行组、疑似主导侧资金、疑似派发路径；
不能把钱包地址直接等同于庄家。
```

输出状态：

```text
WALLET_FACTS_READY
SAME_SOURCE_EVIDENCE_FOUND
WALLET_ROLE_AMBIGUOUS
WALLET_RISK_HIGH
WALLET_NEED_MORE_DATA
```

输出字段：

```text
wallet_classification
same_source_groups
fund_flow_edges
wallet_role_evidence
wallet_risk_level
```

阻断条件：

```text
资金来源不可追踪；
钱包数据不足；
同源证据不足但被写成确定结论；
无法区分交易所/池子/普通钱包。
```

不能作为买入依据的判断：

```text
疑似同源
疑似聪明钱
疑似主导侧
疑似核心资金源
```

---

### 阶段 6：第一波控盘箱体识别

目标：判断第一波资金是否形成控盘结构。

输入数据：

```text
价格区间
成交量变化
回撤深度
POC
AVWAP
早期钱包剩余持仓
Top Holder 留存
OBV / CMF
派发迹象
```

判断逻辑：

```text
控盘箱体不是普通横盘；
必须同时结合 K 线结构、成交量、钱包持仓、早期筹码是否还在、是否出现派发。
```

输出状态：

```text
CONTROL_BOX_DETECTED
CONTROL_BOX_WEAK
CONTROL_BOX_INVALID
CONTROL_BOX_NEED_MORE_DATA
```

输出字段：

```text
control_box_detected
control_box_high
control_box_low
control_box_poc
control_box_avwap
control_box_validity
```

阻断条件：

```text
只有 K 线箱体但钱包已派发；
成交量结构不支持；
关键成本区失守；
无法计算 POC / AVWAP；
派发证据强于控盘证据。
```

不能作为买入依据的判断：

```text
箱体存在
横盘收敛
守住下沿
```

这些需要和筹码状态、策略触发共同判断。

---

### 阶段 7：筹码状态与派发进度判断

目标：判断早期结构资金是否仍有筹码控制权，以及是否正在派发。

输入数据：

```text
early_wallet_remaining_ratio
early_wallet_cleared_count
sell_while_pumping
transfer_to_receivers
top_holder_retention
distribution_progress
counterparty_pressure
chip_control_retention
```

判断逻辑：

```text
核心不是有没有庄；
核心是结构侧是否还没出完；
如果还没出完，它是否有继续拉升完成派发或二次扩张的动机。
```

输出状态：

```text
CHIP_CONTROL_RETAINED
PARTIAL_DISTRIBUTION
ACTIVE_DISTRIBUTION
STRUCTURE_COLLAPSE
INSUFFICIENT_DATA
```

阻断条件：

```text
早期钱包大面积清仓；
明显边拉边卖；
筹码转移到派发路径；
Top Holder 结构崩坏；
对手盘承接压力过高。
```

不能作为买入依据的判断：

```text
筹码仍在
控筹保留
派发未完成
```

这些只说明结构侧仍可能影响走势，不等于当前位置可参与。

---

### 阶段 8：主导侧生命周期与行为意图判断

目标：把钱包结构、筹码状态和盘面结构合成生命周期判断。

生命周期枚举：

```text
EARLY_ACCUMULATION
CONTROL_BOX
FIRST_PUMP
PARTIAL_DISTRIBUTION
WASH_AND_RECLAIM
RE_ACCUMULATION
SECOND_EXPANSION
ACTIVE_DISTRIBUTION
STRUCTURE_EXIT
DEAD_RANGE
REACTIVATION
```

行为意图假设：

```text
accumulation
control
wash
breakout_test
pump_distribution
partial_exit
re_accumulation
second_expansion
active_distribution
abandon_maintenance
```

判断逻辑：

```text
必须使用假设语言；
输出推断必须带 confidence 和 counter_evidence；
不能写“庄家一定要拉”。
```

输出字段：

```text
dominant_side_lifecycle
dominant_side_intent
chip_control_status
distribution_risk
confidence_level
counter_evidence
```

阻断条件：

```text
钱包证据和 K 线证据冲突；
生命周期无法分类；
推断缺少反证；
推断语言变成确定性表达。
```

不能作为买入依据的判断：

```text
疑似二段扩张
疑似控盘箱体
疑似洗盘回收
```

---

### 阶段 9：K 线转强与策略适配

目标：判断是否存在纸面策略参与位置。钱包结构只是前提，不是入场信号。

输入数据：

```text
箱体上沿/下沿
突破确认
回踩有效性
放量确认
POC
AVWAP
HL / HH
OBV / CMF
回踩缩量
```

策略类型：

```text
CONTROL_BOX_BREAKOUT_RETEST
DEEP_WASH_REVERSAL
SECOND_EXPANSION
RISK_MONITOR_ONLY
EXCLUDE
```

判断逻辑：

```text
钱包结构解决有没有结构侧继续操作的可能；
K 线策略解决现在是否有纸面参与位置；
两者不能混。
```

输出状态：

```text
STRATEGY_NOT_READY
WATCHING
RISK_MONITOR
PAPER_READY
BLOCKED
```

阻断条件：

```text
钱包支持但 K 线未转强；
突破无量；
回踩失守；
POC / AVWAP 未收复；
派发风险高于策略条件。
```

不能作为买入依据的判断：

```text
钱包支持
箱体有效
突破发生
```

只有状态机输出 `PAPER_READY` 才允许进入纸面验证，仍不允许真实交易。

---

### 阶段 10：状态输出与后续监控

目标：输出状态，而不是输出买入结论。

状态机：

```text
DISCOVERED
→ SAFETY_BLOCK / SAFETY_PASS
→ MARKET_BLOCK / MARKET_PASS
→ WALLET_SCANNING
→ STRUCTURE_ANALYZED
→ EXCLUDE / RECORD_ONLY / WATCHING / RISK_MONITOR / PAPER_READY / REVIEW_REQUIRED
```

最终状态定义：

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

最终输出必须包含：

```text
状态
核心理由
支持证据
反证
最大风险
失效条件
下一次复查时间
需要补充的数据
```

阻断条件：

```text
输出买入/卖出建议；
缺少反证；
缺少最大风险；
缺少失效条件；
PAPER_READY 被误写成真实执行许可。
```

---

### 阶段 11：纸面执行与复盘沉淀

目标：把 PAPER_READY 转为纸面仓位生命周期，并把结果沉淀成可消费的复盘资产。

输入数据：

```text
PAPER_READY 状态输出
策略类型
纸面入场假设
纸面入场价格
监控周期
失效条件
纸面退出条件
```

判断逻辑：

```text
只做纸面记录，不触发真实交易；
持续比较初始判断与后续走势；
复盘判断链哪里正确、哪里错误；
生成规则更新候选，而不是直接修改规则。
```

输出状态：

```text
PAPER_OPENED
PAPER_MONITORING
PAPER_EXITED
PAPER_REVIEWED
RULE_UPDATE_PROPOSED
```

输出文件建议：

```text
data/paper_positions/<paper_trade_id>/paper_position_open.json
data/paper_positions/<paper_trade_id>/paper_position_update.json
data/paper_positions/<paper_trade_id>/paper_position_close.json
data/paper_positions/<paper_trade_id>/paper_trade_journal.md
data/paper_positions/<paper_trade_id>/paper_review.json
data/paper_positions/<paper_trade_id>/paper_review.md
```

阻断条件：

```text
任何真实下单；
任何 swap；
任何 private key / signing / broadcast；
复盘只看盈亏，不分析判断链；
规则自动修改而无 proposal/review gate。
```

---

## 4. 系统层次图

阶段是时间顺序，层次是系统结构。

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

### 第 1 层：数据层

负责：

```text
接口调用
原始数据保存
字段标准化
时间快照
数据质量检查
```

不负责：

```text
判断庄家
判断买点
输出策略
```

### 第 2 层：安全过滤层

负责：

```text
合约安全
交易限制
池子风险
权限风险
```

输出：

```text
SAFETY_PASS / SAFETY_WARN / SAFETY_BLOCK
```

### 第 3 层：市场过滤层

负责：

```text
市值
流动性
成交量
滑点
涨幅
池子深度
波动质量
```

输出：

```text
MARKET_PASS / MARKET_WARN / MARKET_BLOCK
```

### 第 4 层：钱包事实层

负责：

```text
钱包买入
钱包卖出
当前持仓
资金来源
转账路径
Top Holder
```

只输出事实，不做推断。

### 第 5 层：结构证据层

负责：

```text
同源证据
同步行为
候选钱包组
资金路径
派发路径
筹码集中度
```

只输出证据，不直接下结论。

### 第 6 层：行为推断层

负责：

```text
主导侧生命周期
控筹状态
派发进度
二拉动机
对手盘压力
```

输出推断，必须带不确定性、置信度和反证。

### 第 7 层：盘面策略层

负责：

```text
箱体
突破
回踩
POC
AVWAP
HL/HH
成交量确认
```

只判断纸面策略是否有参与位置，不授权真实交易。

### 第 8 层：状态机决策层

负责综合：

```text
安全
市场
钱包
筹码
生命周期
K 线
策略
```

输出：

```text
排除 / 记录 / 监控 / 观察 / 纸面验证
```

### 第 9 层：解释与复盘层

负责：

```text
为什么排除
为什么记录
为什么监控
为什么进入纸面验证
什么条件失效
下次看什么
判断链哪里错了
规则是否需要更新候选
```

---

## 5. 数据需求表

| 判断对象 | 所需字段 | 来源方向 | 类型 | 缺失处理 |
|---|---|---|---|---|
| 新代币发现 | token 创建时间、发现时间、市值、流动性、成交量、池地址、初始 holder | GMGN / chain source | 事实 | DISCOVERY_NEED_MORE_DATA |
| 安全过滤 | honeypot、freeze、mint、blacklist、tax、pool risk、fake token | GMGN security / chain source | 事实 | SAFETY_NEED_MORE_DATA 或 SAFETY_BLOCK |
| 市场过滤 | liquidity、market_cap、volume、buy/sell、pool_depth、current_gain、volatility | GMGN market / kline | 事实 + 派生 | MARKET_NEED_MORE_DATA |
| 早期结构 | early wallets、buy window、remaining ratio、sell status | transactions / holders | 事实 + 证据 | EARLY_STRUCTURE_NEED_MORE_DATA |
| 钱包角色 | funding source、buy/sell、transfer、sync behavior、history | wallet activity | 事实 + 证据 | WALLET_NEED_MORE_DATA |
| 控盘箱体 | box high/low、volume contraction、POC、AVWAP、holder retention | kline + wallet | 证据 + 推断 | CONTROL_BOX_NEED_MORE_DATA |
| 筹码派发 | remaining ratio、cleared count、sell while pumping、receiver transfer | wallet + holder diff | 证据 + 推断 | INSUFFICIENT_DATA |
| 生命周期 | chip control、distribution risk、intent hypothesis、counter evidence | merged evidence | 推断 | REVIEW_REQUIRED |
| 策略适配 | breakout、retest、volume confirm、POC/AVWAP reclaim、HL/HH | kline / indicators | 策略交接 | STRATEGY_NOT_READY |
| 复盘 | paper entry、exit、PnL、invalidated_by、effective/misleading signals | paper ledger | 解释 + 复盘 | REVIEW_REQUIRED |

---

## 6. 钱包角色表

| 钱包角色 | 识别依据 | 风险等级 | 输出动作 |
|---|---|---|---|
| 新钱包狙击 | 刚创建或低历史、开盘极早买入 | medium/high | 进入早期结构证据 |
| 临时执行钱包 | 只服务当前 token、行为短促 | medium | 标记为执行钱包候选 |
| 同源执行组 | 入金来源相近、同步买入/卖出 | high | 进入 same_source_groups |
| 核心资金源 | 给多个执行钱包供资 | high | 进入 fund_flow_edges |
| 分发接收钱包 | 接收早期钱包转出筹码 | high | 标记派发路径候选 |
| 派发钱包 | 边拉边卖或集中卖出 | high | 提高 distribution_risk |
| 利润回收钱包 | 接收利润或资金回流 | medium/high | 进入回流路径证据 |
| 接盘鲸鱼 | 后期大额接收筹码 | medium/high | 判断 counterparty_pressure |

全部角色必须使用“疑似/证据显示/可能”语言，不允许写成确定庄家。

---

## 7. 筹码状态表

| 状态 | 条件方向 | 输出动作 |
|---|---|---|
| CHIP_CONTROL_RETAINED | 早期钱包剩余比例高、Top Holder 留存、派发弱 | 允许进入生命周期判断 |
| PARTIAL_DISTRIBUTION | 部分早期钱包卖出或转移，但仍有筹码控制 | 进入 RISK_MONITOR / 生命周期判断 |
| ACTIVE_DISTRIBUTION | 边拉边卖、接收钱包扩散、派发路径明显 | BLOCK 或 RISK_MONITOR |
| STRUCTURE_COLLAPSE | 早期结构清仓、箱体失效、Top Holder 崩坏 | EXCLUDE / BLOCKED |
| INSUFFICIENT_DATA | 缺少早期钱包或持仓变化数据 | RECORD_ONLY / REVIEW_REQUIRED |

---

## 8. 生命周期表

| 生命周期 | 典型证据 | 下游动作 |
|---|---|---|
| EARLY_ACCUMULATION | 早期集中买入、卖出弱、流动性初步形成 | WATCHING |
| CONTROL_BOX | 箱体收敛、关键位守住、筹码留存 | WATCHING / RISK_MONITOR |
| FIRST_PUMP | 放量上攻、结构钱包仍部分持仓 | RISK_MONITOR |
| PARTIAL_DISTRIBUTION | 拉升中卖出、接收钱包出现 | RISK_MONITOR / BLOCKED |
| WASH_AND_RECLAIM | 下压后收复关键位、早期筹码仍在 | WATCHING |
| RE_ACCUMULATION | 洗盘后重新吸筹证据 | WATCHING / PAPER_READY候选 |
| SECOND_EXPANSION | 长横盘、低波动压缩、放量突破 | PAPER_READY候选 |
| ACTIVE_DISTRIBUTION | 集中卖出、承接弱、结构退出 | EXCLUDE |
| STRUCTURE_EXIT | 主导侧资金离场 | EXCLUDE |
| DEAD_RANGE | 无量、无结构、无动机 | RECORD_ONLY |
| REACTIVATION | 老 token 出现新结构资金 | WATCHING / REVIEW_REQUIRED |

---

## 9. 状态机表

| 输出状态 | 条件 | 后续动作 |
|---|---|---|
| EXCLUDE | 安全、市场或结构硬风险 | 停止，保留记录 |
| RECORD_ONLY | 数据不足或暂不适合 | 只记录，不监控或低频监控 |
| WATCHING | 有结构迹象，但 K 线/策略未转强 | 设定下次复查时间 |
| RISK_MONITOR | 有机会但风险较高 | 高频监控，等待风险解除 |
| WALLET_SUPPORT | 钱包结构支持继续观察 | 进入盘面策略层 |
| WALLET_PAUSE | 钱包结构矛盾 | 暂停，等待新数据 |
| WALLET_BLOCK | 钱包结构明显风险 | 阻断后续策略 |
| PAPER_READY | 钱包 + K 线 + 策略条件满足 | 进入纸面验证，不是真实交易 |
| REVIEW_REQUIRED | 数据冲突或关键字段缺失 | 复查或人工审计 |

---

## 10. 解释报告模板

每个 token 最终报告必须包含：

```markdown
# Token 状态报告

## 1. Final State
- 状态：EXCLUDE / RECORD_ONLY / WATCHING / RISK_MONITOR / PAPER_READY / REVIEW_REQUIRED
- 是否允许纸面验证：yes/no
- 是否允许真实交易：no

## 2. Core Reason
- 一句话说明核心原因。

## 3. Evidence
- 支持证据 1
- 支持证据 2
- 支持证据 3

## 4. Counter Evidence
- 反证 1
- 反证 2

## 5. Risk
- 最大风险
- 次级风险

## 6. Invalidation Conditions
- 什么条件出现，本判断失效。

## 7. Next Review
- 下次复查时间
- 需要补充的数据

## 8. Layer Trace
- Safety Gate：PASS/WARN/BLOCK
- Market Gate：PASS/WARN/BLOCK
- Wallet Fact Layer：...
- Structure Evidence Layer：...
- Chip Control Inference：...
- Lifecycle：...
- Strategy Fit：...
```

---

## 11. 系统公式

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

## 12. 后续落地要求

后续工程实现不得直接跳到 paper trading 代码。

必须先补齐：

```text
阶段表
数据需求表
钱包角色表
筹码状态表
生命周期表
状态机表
解释报告模板
```

然后再进入 schema / examples / tests / controller 实现。

禁止：

```text
实盘执行逻辑
交易接口连接
钱包签名
广播交易
根据钱包结构直接生成买入建议
把 PAPER_READY 当真实交易许可
```
