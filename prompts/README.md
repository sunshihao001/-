# GPT 提示词包 — 使用说明

## 文件清单

```
/root/sikk-gmgn/prompts/
├── 00-system-prompt.md        ← 先设为 System Prompt
├── 01-candidate-entry.md      ← Step 1: 地址验证
├── 02-token-panel.md          ← Step 2: 数据面板
├── 03-wallet-roles.md         ← Step 3: 钱包角色
├── 04-wallet-structure.md     ← Step 4: 钱包结构
├── 05-evidence-chain.md       ← Step 5: 证据链
├── 06-trade-gate.md           ← Step 6: 门控判断
├── 07-full-pipeline.md        ← 一键跑完 6 步
└── README.md                  ← 本文件
```

## 两种用法

### 用法 A：一键全流程（推荐）

1. 把 `00-system-prompt.md` 的内容设为 GPT 的 System Prompt
2. 把 `07-full-pipeline.md` 的内容发给 GPT，填入 token 地址
3. GPT 会逐步输出 gmgn-cli 命令
4. 你在终端跑命令，把结果粘回去
5. GPT 处理数据，输出每步摘要
6. 6 步完成后输出完整报告

### 用法 B：单步执行

1. 设好 System Prompt
2. 发送对应步骤的 prompt（01-06）
3. 适合只想跑某一步或从某步恢复

## 数据流

```
你 → GPT: "分析这个 token: {CA}"
GPT → 你: "请执行: gmgn-cli token info --chain sol --address {CA} --raw"
你 → 终端: 执行命令
你 → GPT: 粘贴命令输出
GPT → 你: "Step 1 PASS. 请执行: gmgn-cli token security ..."
...重复...
GPT → 你: 完整研究报告
```

## 注意事项

- 每个 prompt 里的 `{CA}` 替换成实际 token 地址
- `{creator_address}` 替换成从前置步骤获得的 dev 地址
- 时间戳用当前时间
- 如果某个 gmgn-cli 命令报错，把错误信息粘回去，GPT 会降级处理
- 一次只分析一个 token
