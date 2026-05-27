# CONTEXT.freeze_candidate.md — Solana Meme 交易决策审计 OS 术语冻结候选

> 状态：FREEZE_CANDIDATE / G01 输出  
> 用途：领域语言词典，只定义术语，不定义实现方案、任务进度或验收标准。  
> 边界：本文件不授权 live trading、swap、private key、wallet signing、transaction broadcast、真实下单、paper runtime、controller implementation。

## 项目总名

`Solana Meme 交易决策审计与门控工作流 OS` 是指：一个以 GMGN 数据为入口、运行在 Hermes 上、围绕 Solana meme token 建立的状态化判断流程。它把候选 token 从市场噪音转成可审计、可回放、可降级、可交接的状态对象。

## GMGN 数据入口

`GMGN 数据入口` 是指：GMGN 提供 token、市场热度、钱包标签、风险提示、交易活动、holder 信息等原始线索。GMGN 只负责把对象送入检查流程，不负责判断买入、不负责授权 paper、不负责执行。

## Hermes 状态工作流

`Hermes 状态工作流` 是指：由 Hermes 保存状态、串联模块、生成交接物、支持中断恢复、记录证据和降级原因的工作流层。Hermes 是状态化工作流底座，不是策略本体。

## 候选池

`候选池` 是指：已经被发现、登记来源、登记进入原因、保存原始证据、等待系统检查的 token 对象集合。

候选池不是机会池，不是信号池，不是 paper 池，不是执行池。

## candidate_packet

`candidate_packet` 是指：候选 token 的标准入口对象。它记录 token 身份、来源、入池原因、发现时间、原始证据引用、基础市场位置、风险字段、holder / wallet 线索和缺失字段。

candidate_packet 不是买入信号，不是交易建议，不是 paper-ready 结论。

## entry_reason

`entry_reason` 是指：token 为什么被送入候选池。它只解释“为什么检查它”，不解释“为什么看好它”。

第一版审计分类包括：`manual_watchlist`、`gmgn_market_attention`、`gmgn_wallet_clue`、`gmgn_risk_clue`、`gmgn_liquidity_activity`、`gmgn_fixture_import`、`external_research_note`、`unknown`。

## raw_evidence_ref

`raw_evidence_ref` 是指：指向原始证据的引用，例如 GMGN fixture、原始响应、截图、页面快照或手动记录。它用于说明判断从哪里来。

raw_evidence_ref 不是结论，也不是信号。

## missing_fields

`missing_fields` 是指：当前候选对象中缺失且会影响判断的字段集合。字段缺失不能被系统脑补，也不能默认视为通过。

## stale_fields

`stale_fields` 是指：存在但已过期或不能代表当前市场状态的字段集合。

## unsupported_fields

`unsupported_fields` 是指：当前数据源不支持、无法提供或尚未接入的字段集合。

## 垃圾盘

`垃圾盘` 是指：在进入深度钱包结构分析前，已经触发安全、市场、结构或证据红旗，导致当前不值得继续消耗深度分析资源的 token。

垃圾盘不是指“一定不会涨”的 token，也不是卖出建议。

## 脏盘

`脏盘` 是指：在安全、市场、钱包、资金路径或生命周期上出现污染信号，导致当前不适合进入 paper 或 execution 的 token。

脏盘类型包括：安全脏盘、流动性脏盘、末端接盘脏盘、holder 集中脏盘、bundle/sniper 脏盘、同源执行脏盘、分发派发脏盘、数据不透明脏盘。

## 红旗

`红旗` 是指：用于预过滤的可检查阻断或降级条件。红旗必须能对应到字段、证据、缺失原因和输出状态。

红旗不是感觉判断。

## 字节

`字节` 是指：上游数据中可被系统读取、标准化、组合和验证的最小字段或事实单元。

例如 `token_address`、`market_cap_usd`、`liquidity_usd`、`top_10_holder_pct`、`early_wallet_remaining_ratio`、`honeypot_flag`、`sniper_count` 都是字节。

## 字节组合

`字节组合` 是指：多个字节共同支持一个结构判断。例如 `price_to_ath_ratio 高 + early_wallet_exit_ratio 高 + market_cap 扩张明显` 可以支持“末端接盘风险”红旗。

单个字节不能直接形成交易结论。

## 反向推理

`反向推理` 是指：从候选入口已有字节出发，判断该 token 是否命中垃圾盘红旗、是否证据不足、是否只能观察、或是否可以进入深度结构分析。

反向推理不是预测价格。

## risk_filter_result

`risk_filter_result` 是指：垃圾盘预过滤和风险门控的输出对象。它记录命中的红旗、证据字段、缺失字段、降级原因、输出状态和下一步动作。

## P0 过滤状态

`P0 过滤状态` 是指第一阶段预过滤输出，只包括：

- `REJECT`：明显垃圾盘或硬风险盘，当前阻断。
- `NEED_MORE_EVIDENCE`：关键证据缺失，不能通过。
- `WATCH_ONLY`：暂不阻断，但只能观察，不能进入 paper。
- `PASS_TO_DEEP_ANALYSIS`：通过垃圾盘预过滤，可以进入深度钱包结构或市场结构分析。

`PASS_TO_DEEP_ANALYSIS` 不是买入、不是 paper-ready、不是执行许可。

## 二段交易

`二段交易` 是指：第一段生命周期已经发生后，早期结构资金可能没有一次性派发完，结构侧仍可能保留筹码控制权，因此可能再次组织吸筹、洗盘、控盘、拉升、派发的一轮生命周期。

二段交易不是“涨完还会再涨”的简单价格判断。

## 二段结构候选

`二段结构候选` 是指：满足二段生命周期最低物理条件、值得进入更深钱包结构和市场结构审计的 token。

它必须至少能解释：第一段已发生、结构侧可能未完全派发、市值仍有可操作空间、流动性仍可承接、成交/注意力未死亡、没有安全硬阻断。

二段结构候选不是买入建议，不是 paper-ready。

## 第一段已发生

`第一段已发生` 是指：token 已经经历过一次有效注意力、成交量、市值或价格扩张。它是判断二段结构候选的前提。

第一段已发生不代表一定有第二段。

## 早期结构资金未完全派发

`早期结构资金未完全派发` 是指：早期钱包、疑似同源执行组或结构相关地址仍可能保留有意义筹码，且未出现大面积清仓或完全退出证据。

未完全派发不代表一定会继续拉升。

## 筹码控制权仍可能存在

`筹码控制权仍可能存在` 是指：剩余筹码仍可能集中在有组织的地址或地址组中，使结构侧仍可能影响后续走势。

筹码控制权判断必须使用疑似和证据语言，不能写成“确定庄家”。

## 市值可操作空间

`市值可操作空间` 是指：当前市值既没有小到无人关注和承接，也没有大到继续推升需要过量新流动性。

市值低不等于便宜，市值高不等于不能涨。

## 流动性可承接区间

`流动性可承接区间` 是指：流动性足够支持观察和承接，但没有薄到一卖就崩，也没有厚到完全推不动或成交死亡。

流动性好不等于结构好。

## 安全脏盘

`安全脏盘` 是指：存在疑似不能卖、高税、黑名单、冻结、mint 权限、LP 或其他安全退出风险的 token。

## 流动性脏盘

`流动性脏盘` 是指：市场看起来可交易，但流动性、池子深度、成交密度或市值/流动性比例显示承接能力不足或异常的 token。

## 末端接盘脏盘

`末端接盘脏盘` 是指：已经接近第一段高位或 ATH，且早期钱包、结构侧或持仓变化显示当前更像接退出流动性的 token。

## holder 集中脏盘

`holder 集中脏盘` 是指：top holder、dev、team、insider 或少数地址持仓过度集中，导致筹码结构风险较高的 token。

## bundle/sniper 脏盘

`bundle/sniper 脏盘` 是指：fresh wallet、sniper、bundle 或类似早期密集进入行为过多，导致早期结构污染明显的 token。

## 同源执行脏盘

`同源执行脏盘` 是指：多个钱包在资金来源、入金时间、买入时间、买入金额、卖出或回流路径上出现多项相似证据，显示疑似同源执行的 token。

同源执行脏盘不能写成确定庄家盘。

## 分发派发脏盘

`分发派发脏盘` 是指：token 被转给多个接收地址，且接收地址后续卖出、清仓或形成卖压路径的 token。

## 数据不透明脏盘

`数据不透明脏盘` 是指：关键风险、holder、交易、流动性或原始证据字段缺失、过期或不可追溯，导致系统无法安全判断的 token。

没有看到风险不等于没有风险。

## Phase 1

`Phase 1` 是指：当前项目的只读研究、契约、状态和 paper-only 前置阶段。Phase 1 不包含 live trading、真实下单、swap、私钥、签名、广播或自动执行。

## Safe Mode

`Safe Mode` 是指：强制禁止真实订单、私钥访问、钱包签名、交易广播、swap、auto deploy 和 production-ready 声明的执行边界。

## Evidence Pipeline

`Evidence Pipeline` 是指：任何判断都必须保存证据、反证、缺失字段、置信度、降级原因和阻断原因的证据链流程。

## Phase State

`Phase State` 是指：用于记录当前 token 工作流阶段、状态、阻断原因、缺失字段和恢复点的状态对象。

## PM/review

`PM/review` 是指：负责需求澄清、冻结文档、创建任务卡、审查结果和判断是否进入下一阶段的角色。

## Task Card

`Task Card` 是指：执行端开始工作的正式任务入口。没有任务卡，不应执行代码或实现工作。

## INTERNAL_PASS

`INTERNAL_PASS` 是指：AI 或 PM/review 内部审查通过。它不是用户最终验收，也不是生产授权。

## HUMAN_ACCEPTED

`HUMAN_ACCEPTED` 是指：用户明确接受某个阶段或交付物。

## 禁止授权词

以下词在当前阶段不得作为输出状态或授权语义使用：`BUY`、`SELL`、`EXECUTE`、`PAPER_READY`、`AUTO_READY`、`LIVE_READY`、`PRODUCTION_READY`、`READY_FOR_AGENT`、`READY_FOR_IMPLEMENTATION`、`FINAL_FROZEN`。
