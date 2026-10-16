# STS2 Climb Toolkit

<!-- moe-counter:start -->
<p align="center">
  <a href="https://github.com/journey-ad/Moe-Counter"><img src="https://count.getloli.com/get/@ppepperkok-hue.sts2-climb-toolkit?theme=asoul" alt="README views" width="360" /></a>
  <br /><sub>README views · Image requests, not unique visitors.</sub>
</p>
<!-- moe-counter:end -->

《杀戮尖塔 2》（Slay the Spire 2）AI 爬塔工具集。这套东西让 Codex 通过本地 HTTP API 直接操控游戏爬塔，同时附带一份完整的爬塔知识库（卡牌、敌人、遗物、路线、复盘教训）。

## 这是什么

爬塔靠一个游戏 mod「STS2 AI Agent」提供本地接口（`http://127.0.0.1:8080`），本仓库负责把「能用」变成「坏了能恢复」：

- 接口怎么调、状态怎么看 → 见脚本
- 每个怪/每张牌/每条路线怎么打 → 见知识库
- mod 本体在哪、怎么装 → 见 tools

## 仓库结构

```text
sts2-climb-toolkit/
├── sts2_helper.py            # API 客户端：请求游戏状态、下发动作
├── sts2_walk.py              # 遍历 /state 返回结构，排查字段用的
├── GameStateService.cs       # 从 mod 提取的状态服务源码（研究用，C#/Godot）
├── skills/
│   └── sts2-climber/         # Codex skill：爬塔知识库 + 操作手册 + 复盘
│       ├── SKILL.md          # skill 入口，Codex 会读这份
│       └── references/       # 卡牌/敌人/遗物/事件/路线/各职业策略
└── tools/
    └── sts2-ai-agent/
        └── STS2AIAgent.zip   # mod 分发包（作者 CharTyr，个人备份用）
```

## 怎么用

前置：已安装 Steam 版《杀戮尖塔 2》。

1. 装 mod：把 `tools/sts2-ai-agent/STS2AIAgent.zip` 解压到游戏目录的 `Mods/` 下，例如
   `D:\steam\steamapps\common\Slay the Spire 2\Mods\`。
   启动游戏后，浏览器或命令行访问 `http://127.0.0.1:8080/health`，返回 ok 就说明接口起来了。
2. 装 skill：把 `skills/sts2-climber/` 整个目录复制到
   `C:\Users\Administrator\.codex\skills\sts2-climber`。
3. 跑脚本：`python sts2_helper.py state` 能打印当前游戏状态（屏幕、手牌、敌人、可用动作）。

## 日常用法速查

```bash
python sts2_helper.py state      # 看当前状态
python sts2_helper.py action     # 交互式下发动作（脚本内有示例）
python sts2_walk.py              # 遍历状态里的消耗牌堆等字段
```

具体动作协议（出牌、选卡、SL、结束回合）都写进了 `skills/sts2-climber/references/agent-integration.md`，忘细节时去翻那份。

## 备注

- `STS2AIAgent.zip` 版权归原作者 CharTyr 所有，本仓库仅作个人备份与恢复用途。
- 本仓库只收录与爬塔相关的内容；人格配置、记忆库等个人资产不在这里。

