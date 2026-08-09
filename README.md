# STS2 Climb Toolkit

《杀戮尖塔 2》AI 爬塔工具集：本地 API 客户端、爬塔知识库（Codex skill）与 mod 备份，让 Codex 直接操控游戏爬塔。

## 内容

- `sts2_helper.py` — STS2 AI Agent 本地 API（`127.0.0.1:8080`）的 Python 客户端。
- `sts2_walk.py` — 遍历游戏状态结构的探查脚本。
- `skills/sts2-climber/` — 爬塔知识库：卡牌 / 敌人 / 遗物 / 事件 / 路线策略与实战复盘。
- `tools/sts2-ai-agent/STS2AIAgent.zip` — 「STS2 AI Agent」mod 分发包（作者 CharTyr，仅供个人备份）。

## 新机器恢复

1. 把 `tools/sts2-ai-agent/STS2AIAgent.zip` 解压到游戏 `Mods/` 目录，启动游戏后确认 `http://127.0.0.1:8080` 可用。
2. 把 `skills/sts2-climber/` 复制到 `$CODEX_HOME/skills/`。
3. 运行 `python sts2_helper.py state` 读取游戏状态。

